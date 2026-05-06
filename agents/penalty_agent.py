"""
THE SYSTEM — Penalty Agent
════════════════════════════
Monitors daily quests and applies XP penalties
for overdue, incomplete objectives.
"""

import asyncio
from datetime import datetime

from db.database import get_connection
from config.settings import PENALTY_XP


async def check_penalties(user_id: int) -> list[dict]:
    """
    Check all of today's daily quests for the given user.
    Any quest past its deadline that hasn't been completed
    receives a -PENALTY_XP deduction.

    Returns a list of penalty dicts with quest details.
    """
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().time()

    cur.execute(
        """SELECT id, quest_name, deadline
           FROM daily_quests
           WHERE user_id = ?
             AND completed = FALSE
             AND penalty_sent = FALSE
             AND quest_date = DATE('now')""",
        (user_id,),
    )

    penalties = []
    for row in cur.fetchall():
        quest_id = row["id"]
        quest_name = row["quest_name"]
        deadline_str = row["deadline"]

        try:
            deadline = datetime.strptime(deadline_str, "%H:%M:%S").time()
        except (ValueError, TypeError):
            continue

        if now > deadline:
            # Apply penalty
            cur.execute(
                "UPDATE daily_quests SET penalty_sent = TRUE WHERE id = ?",
                (quest_id,),
            )
            cur.execute(
                "UPDATE user_stats SET total_xp = MAX(0, total_xp - ?) WHERE id = ?",
                (PENALTY_XP, user_id),
            )

            penalties.append({
                "quest_id": quest_id,
                "quest_name": quest_name,
                "deadline": deadline_str,
                "xp_lost": PENALTY_XP,
            })

    conn.commit()
    conn.close()
    return penalties


async def run_penalty_loop(user_id: int, interval_seconds: int = 300) -> None:
    """
    Background loop that checks penalties every `interval_seconds`.
    Designed to run as an asyncio task alongside the main CLI.
    """
    while True:
        penalties = await check_penalties(user_id)
        for p in penalties:
            # Penalties are displayed by the CLI layer
            pass
        await asyncio.sleep(interval_seconds)
