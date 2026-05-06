"""
THE SYSTEM — Leveling Engine
═════════════════════════════
XP formulas, level-up detection, and rank reward tables.
Threshold formula: XP_required(level) = 100 * (level ^ 1.5)
"""

import math

# ── Rank → Base XP reward ─────────────────────────────────
RANK_XP: dict[str, int] = {
    "E": 10,
    "D": 25,
    "C": 50,
    "B": 100,
    "A": 200,
    "S": 500,
}

# ── Rank → Stat points awarded ────────────────────────────
RANK_STATS: dict[str, int] = {
    "E": 1,
    "D": 2,
    "C": 3,
    "B": 5,
    "A": 8,
    "S": 15,
}

# ── Rank order (for display & sorting) ───────────────────
RANK_ORDER: list[str] = ["E", "D", "C", "B", "A", "S"]


def xp_for_level(level: int) -> int:
    """
    XP required to advance FROM the given level to the next.
    Formula: 100 * (level ^ 1.5), truncated to int.

    Examples:
        Level 1  →  100 XP
        Level 5  →  1,118 XP (cumulative threshold)
        Level 10 →  3,162 XP
    """
    return int(100 * math.pow(level, 1.5))


def check_level_up(total_xp: int, current_level: int) -> tuple[int, bool]:
    """
    Determine if the hunter has enough cumulative XP to level up.
    Supports multi-level jumps (e.g., massive S-rank task at low level).

    Returns:
        (new_level, leveled_up)
    """
    level = current_level
    leveled_up = False
    remaining_xp = total_xp

    # Subtract XP thresholds for all levels up to current
    for lvl in range(1, level):
        remaining_xp -= xp_for_level(lvl)

    # Check if remaining XP exceeds next level threshold
    while remaining_xp >= xp_for_level(level):
        remaining_xp -= xp_for_level(level)
        level += 1
        leveled_up = True

    return level, leveled_up


def xp_to_next_level(total_xp: int, current_level: int) -> tuple[int, int]:
    """
    Calculate XP progress toward the next level.

    Returns:
        (xp_into_current_level, xp_needed_for_next_level)
    """
    remaining = total_xp
    for lvl in range(1, current_level):
        remaining -= xp_for_level(lvl)

    needed = xp_for_level(current_level)
    return remaining, needed


def xp_progress_pct(total_xp: int, current_level: int) -> float:
    """Return level progress as a float 0.0 – 1.0."""
    current, needed = xp_to_next_level(total_xp, current_level)
    if needed == 0:
        return 1.0
    return min(current / needed, 1.0)
