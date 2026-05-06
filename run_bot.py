"""
THE SYSTEM — Telegram Bot Entry Point
═════════════════════════════════════
Initializes the database and starts the Telegram polling loop.
"""

import sys
import asyncio

# Fix for Windows asyncio loop with python-telegram-bot / aiohttp
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from db.database import init_database
from bot.telegram_bot import run

def main():
    """Bootstrap and run the bot."""
    # Ensure database is initialized before starting
    init_database()

    # Start the bot (this blocks until Ctrl+C)
    run()

if __name__ == "__main__":
    main()
