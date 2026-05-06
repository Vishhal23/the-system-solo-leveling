"""
THE SYSTEM — Rich CLI Interface
═════════════════════════════════
Premium terminal UI with panels, tables, progress bars,
and level-up animations. This is what the Hunter sees.
"""

import asyncio
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.live import Live
from rich.style import Style

from agents.task_agent import assess_task
from agents.penalty_agent import check_penalties
from db.models import (
    get_user_stats,
    award_task,
    get_task_history,
    get_total_tasks,
    add_daily_quest,
    complete_daily_quest,
    get_todays_quests,
    update_hunter_name,
)
from core.leveling import xp_to_next_level, xp_progress_pct, xp_for_level, RANK_XP
from core.ranks import rank_display, rank_color, RANKS, rank_bar
from core.stats import stat_display, stat_bar, STATS, get_all_stat_keys

console = Console()

# ── ASCII Banner ──────────────────────────────────────────
BANNER = r"""
[bold bright_cyan]
  ████████╗██╗  ██╗███████╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
  ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
     ██║   ███████║█████╗      ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
     ██║   ██╔══██║██╔══╝      ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
     ██║   ██║  ██║███████╗    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
     ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
[/bold bright_cyan]
"""

MENU_TEXT = """[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]
  [bold cyan]1[/bold cyan]  ⚔️  Submit Task       [bold cyan]2[/bold cyan]  📊  View Stats
  [bold cyan]3[/bold cyan]  📜  Task History      [bold cyan]4[/bold cyan]  🎯  Daily Quests
  [bold cyan]5[/bold cyan]  ✅  Complete Quest    [bold cyan]6[/bold cyan]  ⚠️   Check Penalties
  [bold cyan]7[/bold cyan]  📋  Rank Guide        [bold cyan]0[/bold cyan]  🚪  Exit
[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]"""


# ═══════════════════════════════════════════════════════════
# DISPLAY COMPONENTS
# ═══════════════════════════════════════════════════════════

def show_banner():
    """Print the system boot sequence."""
    console.print(BANNER)
    console.print(
        Align.center("[bold bright_white][ SOLO LEVELING SYSTEM v1.0 ][/bold bright_white]")
    )
    console.print(
        Align.center("[dim]Arise, Hunter. Your journey begins now.[/dim]\n")
    )


def show_menu():
    """Print the main command menu."""
    console.print(MENU_TEXT)


def show_stats_panel(user_id: int):
    """Display the hunter's full stat card as a Rich panel."""
    stats = get_user_stats(user_id)
    if stats is None:
        console.print("[red]User not found.[/red]")
        return

    total_tasks = get_total_tasks(user_id)
    xp_current, xp_needed = xp_to_next_level(stats["total_xp"], stats["level"])
    progress_pct = xp_progress_pct(stats["total_xp"], stats["level"])

    # Build stat lines
    stat_keys = get_all_stat_keys()
    max_stat = max(stats.get(k, 0) for k in stat_keys) or 1
    # Use a reasonable scale — at least 50
    bar_max = max(max_stat, 50)

    stat_lines = []
    for key in stat_keys:
        val = stats.get(key, 0)
        info = STATS[key]
        bar = stat_bar(val, bar_max)
        stat_lines.append(
            f"  [{info.color}]{info.icon} {info.name:<14}[/{info.color}]"
            f"  [bold]{val:>4}[/bold]  [dim]{bar}[/dim]"
        )

    # XP progress bar
    filled = int(progress_pct * 30)
    xp_bar = "[bright_cyan]" + "█" * filled + "[/bright_cyan]" + "[dim]░[/dim]" * (30 - filled)

    body = (
        f"  [bold bright_white]🏷️  {stats['username']}[/bold bright_white]\n"
        f"  [bold yellow]⭐ Level {stats['level']}[/bold yellow]    "
        f"[dim]|  {total_tasks} tasks completed[/dim]\n\n"
        f"  [dim]XP[/dim]  {xp_bar}  [bold]{xp_current}[/bold][dim]/{xp_needed}[/dim]\n"
        f"  [dim]Total XP: {stats['total_xp']:,}[/dim]\n\n"
        + "\n".join(stat_lines)
    )

    panel = Panel(
        body,
        title="[bold bright_cyan]⚔️  HUNTER STATUS[/bold bright_cyan]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    )
    console.print(panel)


def show_task_result(result: dict, assessment: dict):
    """Display task completion results with rank badge and XP gain."""

    rank = result["rank"]
    rinfo = RANKS.get(rank)
    color = rinfo.color if rinfo else "white"

    body = (
        f"  [bold]📝 Task:[/bold]     {result['task_name']}\n"
        f"  [bold]🏅 Rank:[/bold]     [{color}]{rinfo.emoji if rinfo else '?'} {rank}-Rank[/{color}]"
        f"  [dim]{rank_bar(rank)}[/dim]\n"
        f"  [bold]💡 Reason:[/bold]   [italic dim]{result['reasoning']}[/italic dim]\n\n"
        f"  [bold bright_green]▸ XP Awarded:[/bold bright_green]   +{result['xp_gained']} XP"
        f"    [dim]({result['old_xp']:,} → {result['new_xp']:,})[/dim]\n"
        f"  [bold {STATS.get(result['stat_type'].lower(), STATS['endurance']).color}]"
        f"▸ {result['stat_type'].upper()}:[/bold {STATS.get(result['stat_type'].lower(), STATS['endurance']).color}]"
        f"   +{result['stat_points']} points"
    )

    panel = Panel(
        body,
        title="[bold green]✅ TASK VERIFIED[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def show_level_up(new_level: int):
    """Animated level-up announcement."""
    console.print()

    frames = [
        "[bold bright_yellow]  ⚡ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ⚡[/bold bright_yellow]",
        "[bold bright_yellow]  ⚡ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ⚡[/bold bright_yellow]",
        "[bold bright_yellow]  ⚡ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ⚡[/bold bright_yellow]",
        "[bold bright_yellow]  ⚡ ████████████████████████████████████████ ⚡[/bold bright_yellow]",
    ]

    for frame in frames:
        console.print(frame, end="\r")
        time.sleep(0.15)

    console.print()
    level_panel = Panel(
        Align.center(
            f"[bold bright_yellow]⚡ LEVEL UP ⚡[/bold bright_yellow]\n\n"
            f"[bold white]You have ascended to[/bold white]\n"
            f"[bold bright_yellow]✦  LEVEL {new_level}  ✦[/bold bright_yellow]\n\n"
            f"[dim]The shadows grow deeper. You grow stronger.[/dim]"
        ),
        border_style="bright_yellow",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
    )
    console.print(level_panel)
    console.print()


def show_task_history(user_id: int):
    """Display recent tasks as a Rich table."""
    tasks = get_task_history(user_id, limit=15)

    if not tasks:
        console.print("[dim]No tasks logged yet. Begin your hunt, Hunter.[/dim]")
        return

    table = Table(
        title="[bold bright_cyan]📜 QUEST LOG[/bold bright_cyan]",
        box=box.SIMPLE_HEAVY,
        border_style="bright_cyan",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Task", style="white", max_width=35)
    table.add_column("Rank", justify="center", width=10)
    table.add_column("XP", justify="right", style="bright_green", width=6)
    table.add_column("Stat", justify="center", width=14)
    table.add_column("Date", style="dim", width=12)

    for i, t in enumerate(tasks, 1):
        rinfo = RANKS.get(t["rank"])
        rank_str = f"[{rinfo.color}]{rinfo.emoji} {t['rank']}[/{rinfo.color}]" if rinfo else t["rank"]

        sinfo = STATS.get(t.get("stat_type", "").lower())
        stat_str = f"[{sinfo.color}]{sinfo.icon} {sinfo.name}[/{sinfo.color}]" if sinfo else t.get("stat_type", "")

        date_str = str(t.get("completed_at", ""))[:10]

        table.add_row(
            str(i),
            t.get("task_name", "Unknown"),
            rank_str,
            f"+{t['xp_awarded']}",
            stat_str,
            date_str,
        )

    console.print(table)


def show_daily_quests(user_id: int):
    """Display today's daily quests."""
    quests = get_todays_quests(user_id)

    if not quests:
        console.print("[dim]No daily quests set for today. Use option 4 to add one.[/dim]")
        return

    table = Table(
        title="[bold bright_yellow]🎯 DAILY QUESTS[/bold bright_yellow]",
        box=box.SIMPLE_HEAVY,
        border_style="bright_yellow",
        show_lines=True,
    )
    table.add_column("ID", style="dim", width=4)
    table.add_column("Quest", style="white", max_width=35)
    table.add_column("Deadline", justify="center", width=10)
    table.add_column("Status", justify="center", width=12)

    for q in quests:
        if q["completed"]:
            status = "[bold green]✅ DONE[/bold green]"
        elif q["penalty_sent"]:
            status = "[bold red]💀 FAILED[/bold red]"
        else:
            status = "[yellow]⏳ PENDING[/yellow]"

        table.add_row(
            str(q["id"]),
            q["quest_name"],
            q["deadline"],
            status,
        )

    console.print(table)


def show_rank_guide():
    """Display the rank classification guide."""
    table = Table(
        title="[bold bright_cyan]📋 RANK CLASSIFICATION GUIDE[/bold bright_cyan]",
        box=box.DOUBLE_EDGE,
        border_style="bright_cyan",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Rank", justify="center", width=12)
    table.add_column("Difficulty", width=12)
    table.add_column("Base XP", justify="right", width=8)
    table.add_column("Power", width=10)
    table.add_column("Examples", style="dim", max_width=40)

    examples = {
        "E": "Drink water, make bed, stretch",
        "D": "20-min walk, read 10 pages",
        "C": "1hr study, gym workout",
        "B": "Build a feature, 10km run",
        "A": "Complete a project module",
        "S": "Ship a product, 24hr hackathon",
    }

    for letter in ["E", "D", "C", "B", "A", "S"]:
        r = RANKS[letter]
        table.add_row(
            f"[{r.color}]{r.emoji} {r.name}[/{r.color}]",
            r.difficulty,
            f"{r.base_xp} XP",
            f"[{r.color}]{rank_bar(letter)}[/{r.color}]",
            examples.get(letter, ""),
        )

    console.print(table)


def show_penalties(penalties: list[dict]):
    """Display penalty notifications."""
    if not penalties:
        console.print("[green]No penalties. All quests in order, Hunter.[/green]")
        return

    for p in penalties:
        console.print(
            Panel(
                f"  [bold red]⚠ PENALTY APPLIED[/bold red]\n\n"
                f"  Quest: [bold]{p['quest_name']}[/bold]\n"
                f"  Deadline: {p['deadline']}\n"
                f"  [bold red]-{p['xp_lost']} XP[/bold red]\n\n"
                f"  [dim italic]Disgraceful. The System does not tolerate weakness.[/dim italic]",
                border_style="red",
                box=box.HEAVY,
                padding=(1, 2),
            )
        )


# ═══════════════════════════════════════════════════════════
# MAIN CLI LOOP
# ═══════════════════════════════════════════════════════════

async def run_cli(user_id: int = 1):
    """Main interactive CLI loop."""
    show_banner()

    # Check if user wants to set their name on first run
    stats = get_user_stats(user_id)
    if stats and stats["username"] == "Hunter":
        console.print("[dim]First awakening detected.[/dim]")
        name = console.input("[bold cyan]  Enter your Hunter name: [/bold cyan]").strip()
        if name:
            update_hunter_name(user_id, name)
            console.print(f"\n[bold]  Registered: [bright_cyan]{name}[/bright_cyan][/bold]\n")

    while True:
        show_menu()
        choice = console.input("\n[bold bright_white]  ⌘ Command > [/bold bright_white]").strip()

        if choice == "1":
            # ── Submit Task ───────────────────────────────
            console.print()
            raw = console.input("[bold cyan]  📝 Describe your task, Hunter > [/bold cyan]").strip()
            if not raw:
                console.print("[dim]  No input. Ignored.[/dim]")
                continue

            console.print("\n[dim]  [ ANALYZING TASK... ][/dim]")
            assessment = await assess_task(raw)
            assessment["raw_input"] = raw

            result = award_task(user_id, assessment)
            console.print()
            show_task_result(result, assessment)

            if result["leveled_up"]:
                show_level_up(result["new_level"])

        elif choice == "2":
            # ── View Stats ────────────────────────────────
            console.print()
            show_stats_panel(user_id)

        elif choice == "3":
            # ── Task History ──────────────────────────────
            console.print()
            show_task_history(user_id)

        elif choice == "4":
            # ── Daily Quests ──────────────────────────────
            console.print()
            show_daily_quests(user_id)
            console.print()
            add = console.input("[dim]  Add a new quest? (y/n) > [/dim]").strip().lower()
            if add == "y":
                quest = console.input("[bold cyan]  Quest name > [/bold cyan]").strip()
                if quest:
                    deadline = console.input("[dim]  Deadline (HH:MM:SS, default 22:00:00) > [/dim]").strip()
                    if not deadline:
                        deadline = "22:00:00"
                    qid = add_daily_quest(user_id, quest, deadline)
                    console.print(f"[green]  ✅ Quest #{qid} added.[/green]")

        elif choice == "5":
            # ── Complete Quest ────────────────────────────
            console.print()
            show_daily_quests(user_id)
            qid_str = console.input("\n[bold cyan]  Quest ID to complete > [/bold cyan]").strip()
            try:
                qid = int(qid_str)
                if complete_daily_quest(qid):
                    console.print(f"[bold green]  ✅ Quest #{qid} completed. Well done, Hunter.[/bold green]")
                else:
                    console.print("[dim]  Quest not found or already completed.[/dim]")
            except ValueError:
                console.print("[dim]  Invalid ID.[/dim]")

        elif choice == "6":
            # ── Check Penalties ───────────────────────────
            console.print()
            penalties = await check_penalties(user_id)
            show_penalties(penalties)

        elif choice == "7":
            # ── Rank Guide ────────────────────────────────
            console.print()
            show_rank_guide()

        elif choice == "0":
            console.print(
                Panel(
                    Align.center(
                        "[bold bright_cyan][ SESSION TERMINATED ][/bold bright_cyan]\n\n"
                        "[dim]The System watches. Always.[/dim]"
                    ),
                    border_style="bright_cyan",
                    box=box.DOUBLE_EDGE,
                    padding=(1, 4),
                )
            )
            break

        else:
            console.print("[dim]  Unknown command. Choose 0-7.[/dim]")

        console.print()
