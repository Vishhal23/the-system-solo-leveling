"""
THE SYSTEM — Automated Scheduler
════════════════════════════════
Manages daily quests, penalties, and background tasks.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import USER_ID, DEFAULT_QUEST_DEADLINE
from db.models import add_daily_quest, get_todays_quests, apply_penalty

logger = logging.getLogger(__name__)

# Daily Quests (The "Solo Leveling" basics)
DAILY_QUESTS = [
    "100 Push-ups",
    "100 Sit-ups",
    "100 Squats",
    "10 km Run",
]


async def _generate_daily_quests() -> None:
    """Assign new daily quests to the Hunter at midnight."""
    logger.info("Generating daily quests...")
    # Add today's quests
    for quest in DAILY_QUESTS:
        add_daily_quest(USER_ID, quest, deadline=DEFAULT_QUEST_DEADLINE)
    logger.info("Daily quests generated successfully.")


async def _check_penalties(bot=None) -> None:
    """Check for incomplete quests at the deadline and apply penalties."""
    logger.info("Checking for incomplete daily quests...")
    quests = get_todays_quests(USER_ID)
    
    penalties_applied = 0
    for quest in quests:
        if not quest["completed"] and not quest["penalty_sent"]:
            apply_penalty(USER_ID, quest["id"])
            penalties_applied += 1
            
    if penalties_applied > 0 and bot:
        from config.settings import TELEGRAM_ALLOWED_USER_ID
        if TELEGRAM_ALLOWED_USER_ID:
            message = (
                f"⚠️ **PENALTY ZONE ACTIVATED** ⚠️\n\n"
                f"You failed to complete {penalties_applied} daily quests.\n"
                f"The System has deducted XP as punishment. Survive."
            )
            try:
                await bot.send_message(chat_id=TELEGRAM_ALLOWED_USER_ID, text=message, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to send penalty notification: {e}")


def start_scheduler(telegram_bot_app=None) -> AsyncIOScheduler:
    """
    Initialize and start the background scheduler.
    """
    scheduler = AsyncIOScheduler()
    
    # 1. Midnight trigger: Generate new quests
    scheduler.add_job(
        _generate_daily_quests,
        trigger=CronTrigger(hour=0, minute=0),
        id="generate_daily_quests",
        replace_existing=True,
    )
    
    # 2. Deadline trigger (e.g., 22:00): Check penalties
    hour, minute, _ = map(int, DEFAULT_QUEST_DEADLINE.split(":"))
    
    # Passing the bot instance so we can send penalty messages
    bot_instance = telegram_bot_app.bot if telegram_bot_app else None
    
    scheduler.add_job(
        _check_penalties,
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[bot_instance],
        id="check_penalties",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("System Scheduler started.")
    return scheduler
