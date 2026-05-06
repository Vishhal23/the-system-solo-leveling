"""
THE SYSTEM — Rank Classification
══════════════════════════════════
Rank definitions, display helpers, and Rich color mappings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RankInfo:
    """Immutable rank descriptor."""
    letter: str
    name: str
    difficulty: str
    base_xp: int
    color: str          # Rich markup color
    emoji: str


# ── Rank Registry ─────────────────────────────────────────
RANKS: dict[str, RankInfo] = {
    "E": RankInfo("E", "E-Rank", "Trivial",   10,  "dim white",    "⚪"),
    "D": RankInfo("D", "D-Rank", "Easy",      25,  "green",        "🟢"),
    "C": RankInfo("C", "C-Rank", "Moderate",  50,  "cyan",         "🔵"),
    "B": RankInfo("B", "B-Rank", "Hard",      100, "yellow",       "🟡"),
    "A": RankInfo("A", "A-Rank", "Very Hard", 200, "bright_red",   "🔴"),
    "S": RankInfo("S", "S-Rank", "Legendary", 500, "bold magenta", "🟣"),
}


def rank_display(rank: str) -> str:
    """Return a Rich-markup styled rank string."""
    info = RANKS.get(rank)
    if info is None:
        return f"[dim]?-Rank[/dim]"
    return f"[{info.color}]{info.emoji} {info.name}[/{info.color}]"


def rank_color(rank: str) -> str:
    """Return the Raw Rich color for a rank."""
    info = RANKS.get(rank)
    return info.color if info else "white"


def rank_bar(rank: str) -> str:
    """Return a simple visual bar representing rank power."""
    order = {"E": 1, "D": 2, "C": 3, "B": 4, "A": 5, "S": 6}
    level = order.get(rank, 0)
    return "█" * level + "░" * (6 - level)
