"""
THE SYSTEM — Entry Point
══════════════════════════
Initializes the database and launches the Rich CLI.

Usage:
    python main.py
"""

import asyncio
import sys

from db.database import init_database
from ui.cli import run_cli
from config.settings import USER_ID

import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def main():
    """Bootstrap and run."""
    # Initialize DB (idempotent — safe to call every run)
    init_database()

    # Launch async CLI
    try:
        asyncio.run(run_cli(user_id=USER_ID))
    except KeyboardInterrupt:
        print("\n[ SESSION TERMINATED ]")
        sys.exit(0)


if __name__ == "__main__":
    main()
