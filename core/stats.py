"""
THE SYSTEM — Stat Management
══════════════════════════════
Stat definitions, radar helpers, and display utilities.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StatInfo:
    """Describes a single stat attribute."""
    key: str
    name: str
    icon: str
    color: str
    task_types: list[str]


# ── Stat Registry ─────────────────────────────────────────
STATS: dict[str, StatInfo] = {
    "strength": StatInfo(
        key="strength",
        name="Strength",
        icon="💪",
        color="bright_red",
        task_types=["Physical", "Exercise", "Lifting", "Sports"],
    ),
    "intelligence": StatInfo(
        key="intelligence",
        name="Intelligence",
        icon="🧠",
        color="bright_blue",
        task_types=["Cognitive", "Study", "Learning", "Research", "Coding"],
    ),
    "agility": StatInfo(
        key="agility",
        name="Agility",
        icon="⚡",
        color="bright_yellow",
        task_types=["Physical", "Cardio", "Running", "Speed"],
    ),
    "endurance": StatInfo(
        key="endurance",
        name="Endurance",
        icon="🛡️",
        color="bright_green",
        task_types=["Discipline", "Habits", "Consistency", "Routines"],
    ),
    "charisma": StatInfo(
        key="charisma",
        name="Charisma",
        icon="✨",
        color="bright_magenta",
        task_types=["Creative", "Social", "Art", "Writing", "Communication"],
    ),
}


def stat_display(stat_key: str, value: int) -> str:
    """Return a Rich-markup styled stat line."""
    info = STATS.get(stat_key.lower())
    if info is None:
        return f"{stat_key}: {value}"
    return f"[{info.color}]{info.icon} {info.name:<14} {value:>4}[/{info.color}]"


def stat_bar(value: int, max_val: int = 100) -> str:
    """Return a visual progress bar for a stat."""
    if max_val <= 0:
        max_val = 1
    filled = min(int((value / max_val) * 20), 20)
    return "█" * filled + "░" * (20 - filled)


def get_all_stat_keys() -> list[str]:
    """Return ordered list of stat column names."""
    return list(STATS.keys())
