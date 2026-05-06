"""
THE SYSTEM — Telegram Bot
═════════════════════════
Handles Telegram interactions, fetching stats, and processing task submissions via Gemini.
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config.settings import TELEGRAM_TOKEN, TELEGRAM_ALLOWED_USER_ID, USER_ID
from core.leveling import xp_for_level
from db.models import get_user_stats, get_task_history, award_task
from agents.task_agent import assess_task

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    if not await _is_authorized(update):
        return

    welcome_text = (
        "⚔️ **THE SYSTEM INITIALIZED** ⚔️\n\n"
        "Welcome, Hunter. I am your guide.\n"
        "Submit your daily tasks by simply typing them here.\n\n"
        "Commands:\n"
        "/stats - View your current Hunter Status\n"
        "/history - View recent tasks"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the user's current stats."""
    if not await _is_authorized(update):
        return

    stats = await asyncio.to_thread(get_user_stats, USER_ID)
    if not stats:
        await update.message.reply_text("Hunter profile not found.")
        return

    level = stats["level"]
    xp = stats["current_xp"]
    required_xp = xp_for_level(level)
    
    stats_text = (
        f"⚔️ **HUNTER STATUS** ⚔️\n\n"
        f"⭐ **Level:** {level}\n"
        f"💠 **XP:** {xp} / {required_xp}\n\n"
        f"💪 **Strength:** {stats['strength']}\n"
        f"🧠 **Intelligence:** {stats['intelligence']}\n"
        f"⚡ **Agility:** {stats['agility']}\n"
        f"🛡️ **Endurance:** {stats['endurance']}\n"
        f"✨ **Charisma:** {stats['charisma']}\n"
    )
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the last 5 tasks."""
    if not await _is_authorized(update):
        return

    history = await asyncio.to_thread(get_task_history, USER_ID, 5)
    if not history:
        await update.message.reply_text("No recent tasks found.")
        return

    history_text = "📜 **RECENT QUESTS** 📜\n\n"
    for task in history:
        history_text += f"• **{task['task_name']}** [{task['rank']}-Rank]\n  +{task['xp_awarded']} XP | {task['stat_type']}\n\n"

    await update.message.reply_text(history_text, parse_mode="Markdown")

async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process a raw text message as a task submission."""
    if not await _is_authorized(update):
        return

    raw_input = update.message.text
    await update.message.reply_text("⏳ *Analyzing task...*", parse_mode="Markdown")

    # 1. Assess via AI
    assessment = await assess_task(raw_input)

    # 2. Award XP and update stats
    result = await asyncio.to_thread(award_task, USER_ID, assessment)

    # 3. Format response
    success_msg = f"✅ <b>Task Assessed & Logged!</b>\n\n"
    success_msg += f"🏅 <b>Rank:</b> {result['rank']}\n"
    success_msg += f"📊 <b>XP Gained:</b> +{result['xp_gained']}\n"
    success_msg += f"💪 <b>Stat Increased:</b> {result['stat_type'].title()} (+{result['stat_points']})\n\n"
    
    if result['leveled_up']:
        success_msg += f"🎉 <b>LEVEL UP!</b> You are now Level {result['new_level']}! 🎉\n\n"
        
    if result.get('unlocked_job'):
        success_msg += f"👑 <b>[HIDDEN QUEST COMPLETED]</b> 👑\n"
        success_msg += f"You have met the hidden stat requirements.\n"
        success_msg += f"Your new Job Class is: <b>{result['job_name']}</b>!\n\n"

    success_msg += f"<i>System Reasoning:</i> {result['reasoning']}"

    await update.message.reply_text(success_msg, parse_mode="HTML")

async def _is_authorized(update: Update) -> bool:
    """Check if the user is authorized to use this bot."""
    if not TELEGRAM_ALLOWED_USER_ID:
        # If no restriction is set, warn in logs but allow (not recommended for production)
        logger.warning("TELEGRAM_ALLOWED_USER_ID is not set. Anyone can use the bot.")
        return True

    user_id = str(update.message.from_user.id)
    if user_id != str(TELEGRAM_ALLOWED_USER_ID):
        logger.warning(f"Unauthorized access attempt from User ID: {user_id}")
        await update.message.reply_text("You are not authorized to access The System.")
        return False
    return True

def run():
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set in .env")
        print("[ERROR] TELEGRAM_TOKEN is not set in .env. Please set it and try again.")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CommandHandler("history", show_history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_task))

    print("[BOT] Starting the System Scheduler...")
    from core.scheduler import start_scheduler
    start_scheduler(application)

    print("[BOT] The System Bot is now running... Press Ctrl+C to stop.")
    application.run_polling()
