"""
THE SYSTEM — Database Models / Query Helpers
═════════════════════════════════════════════
Pure SQL queries — no ORM overhead. Each function
opens its own connection for thread safety.
"""

import sqlite3
from datetime import date, datetime
from typing import Optional

from config.settings import PENALTY_XP
from core.leveling import RANK_XP, RANK_STATS, check_level_up
from db.database import get_connection


# ── Stat column whitelist (prevents SQL injection) ────────
_VALID_STATS = {"strength", "intelligence", "agility", "endurance", "charisma"}


def _safe_stat_col(stat_type: str) -> str:
    """Validate and return the stat column name."""
    col = stat_type.lower()
    if col not in _VALID_STATS:
        raise ValueError(f"Invalid stat type: {stat_type!r}. Must be one of {_VALID_STATS}")
    return col


# ═══════════════════════════════════════════════════════════
# USER STATS
# ═══════════════════════════════════════════════════════════

def get_user_stats(user_id: int) -> Optional[dict]:
    """Fetch full user profile as a dict."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_stats WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def update_hunter_name(user_id: int, name: str) -> None:
    """Update the hunter's display name."""
    conn = get_connection()
    conn.execute("UPDATE user_stats SET username = ? WHERE id = ?", (name, user_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════
# TASK PROCESSING
# ═══════════════════════════════════════════════════════════

def award_task(user_id: int, assessment: dict) -> dict:
    """
    Full task processing pipeline:
    1. Calculate XP & stat points from rank
    2. Fetch current user stats
    3. Update XP, check level-up, update stat
    4. Insert task record
    5. Insert XP audit log entry
    Returns a result summary dict.
    """
    conn = get_connection()
    cur = conn.cursor()

    rank = assessment["rank"]
    xp = RANK_XP[rank]
    stat_pts = RANK_STATS[rank]
    stat_col = _safe_stat_col(assessment["stat_type"])

    # ── Fetch current stats ───────────────────────────────
    cur.execute("SELECT level, total_xp FROM user_stats WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"User {user_id} not found")

    old_level = row["level"]
    old_xp = row["total_xp"]

    new_xp = old_xp + xp
    new_level, leveled_up = check_level_up(new_xp, old_level)

    # ── Update user stats ─────────────────────────────────
    cur.execute(
        f"UPDATE user_stats SET level = ?, total_xp = ?, {stat_col} = {stat_col} + ? WHERE id = ?",
        (new_level, new_xp, stat_pts, user_id),
    )

    # ── Insert task record ────────────────────────────────
    cur.execute(
        """INSERT INTO tasks
           (user_id, raw_input, task_name, rank, xp_awarded, stat_type, stat_points, verified)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            assessment.get("raw_input", ""),
            assessment["task_name"],
            rank,
            xp,
            assessment["stat_type"],
            stat_pts,
            assessment.get("verified", True),
        ),
    )
    task_id = cur.lastrowid

    # ── Insert XP audit log ──────────────────────────────
    cur.execute(
        """INSERT INTO experience_log
           (user_id, task_id, xp_before, xp_after, level_before, level_after, leveled_up)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, task_id, old_xp, new_xp, old_level, new_level, leveled_up),
    )

    # ── Job Class Check ───────────────────────────────────
    cur.execute("SELECT * FROM user_stats WHERE id = ?", (user_id,))
    updated_row = dict(cur.fetchone())
    
    from core.progression import check_job_change
    unlocked_job, job_name = check_job_change(updated_row)
    
    if unlocked_job:
        cur.execute("UPDATE user_stats SET job_class = ? WHERE id = ?", (job_name, user_id))

    conn.commit()
    conn.close()

    return {
        "task_id": task_id,
        "task_name": assessment["task_name"],
        "rank": rank,
        "reasoning": assessment.get("reasoning", ""),
        "xp_gained": xp,
        "old_xp": old_xp,
        "new_xp": new_xp,
        "old_level": old_level,
        "new_level": new_level,
        "leveled_up": leveled_up,
        "stat_type": assessment["stat_type"],
        "stat_points": stat_pts,
        "unlocked_job": unlocked_job,
        "job_name": job_name,
    }


# ═══════════════════════════════════════════════════════════
# TASK HISTORY
# ═══════════════════════════════════════════════════════════

def get_task_history(user_id: int, limit: int = 10) -> list[dict]:
    """Return the most recent tasks for a user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, task_name, rank, xp_awarded, stat_type, stat_points, completed_at
           FROM tasks WHERE user_id = ? ORDER BY completed_at DESC LIMIT ?""",
        (user_id, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_total_tasks(user_id: int) -> int:
    """Count total completed tasks."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


# ═══════════════════════════════════════════════════════════
# DAILY QUESTS
# ═══════════════════════════════════════════════════════════

def add_daily_quest(user_id: int, quest_name: str, deadline: str = "22:00:00") -> int:
    """Add a new daily quest. Returns quest ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO daily_quests (user_id, quest_name, deadline)
           VALUES (?, ?, ?)""",
        (user_id, quest_name, deadline),
    )
    quest_id = cur.lastrowid
    conn.commit()
    conn.close()
    return quest_id


def complete_daily_quest(quest_id: int) -> bool:
    """Mark a daily quest as completed. Returns True if found."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE daily_quests SET completed = TRUE WHERE id = ? AND completed = FALSE",
        (quest_id,),
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_todays_quests(user_id: int) -> list[dict]:
    """Fetch all daily quests for today."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, quest_name, deadline, completed, penalty_sent
           FROM daily_quests
           WHERE user_id = ? AND quest_date = DATE('now')
           ORDER BY deadline""",
        (user_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def apply_penalty(user_id: int, quest_id: int) -> None:
    """Deduct PENALTY_XP and mark quest as penalty_sent."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE daily_quests SET penalty_sent = TRUE WHERE id = ?", (quest_id,))
    cur.execute(
        "UPDATE user_stats SET total_xp = MAX(0, total_xp - ?) WHERE id = ?",
        (PENALTY_XP, user_id),
    )
    conn.commit()
    conn.close()
