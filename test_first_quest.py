import asyncio
import os
from agents.task_agent import assess_task
from db.models import award_task, get_user_stats
from ui.cli import show_task_result, show_level_up, show_stats_panel
from rich.console import Console

console = Console()

async def submit_first_quest():
    user_id = 1
    raw_task = "I just ran 5 kilometers and drank 2 liters of water"
    console.print(f"[bold cyan]📝 Submitted Task:[/bold cyan] {raw_task}")
    
    console.print("\n[dim][ ANALYZING TASK... ][/dim]")
    assessment = await assess_task(raw_task)
    assessment["raw_input"] = raw_task
    
    result = award_task(user_id, assessment)
    console.print()
    show_task_result(result, assessment)
    
    if result["leveled_up"]:
        show_level_up(result["new_level"])
        
    console.print()
    show_stats_panel(user_id)

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(submit_first_quest())
