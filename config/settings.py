"""
THE SYSTEM — Configuration
══════════════════════════
Central configuration for all system modules.
Loads environment variables and defines global constants.
"""

from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

# ── API Keys ──────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID", "")

# ── Database ──────────────────────────────────────────
DB_PATH = str(_project_root / "the_system.db")

# ── System Persona ────────────────────────────────────
SYSTEM_PERSONA = (
    "You are THE SYSTEM — a cold, mechanical AI that governs the growth of the Hunter. "
    "You speak in short, direct sentences. No pleasantries. Only results matter. "
    "Your role: analyze tasks submitted by the Hunter and return structured JSON assessments."
)

# ── Default Hunter Name ───────────────────────────────
DEFAULT_HUNTER_NAME = "Hunter"
USER_ID = 1  # Single-user MVP

# ── Penalty Config ────────────────────────────────────
PENALTY_XP = 50
DEFAULT_QUEST_DEADLINE = "22:00:00"
