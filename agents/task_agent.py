"""
THE SYSTEM — Task Verification Agent
══════════════════════════════════════
LangChain + Gemini agent that classifies raw task input
into structured assessments with rank, stat type, and reasoning.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, SYSTEM_PERSONA

GEMINI_MODEL = "gemini-2.5-flash"

# Configure genai
genai.configure(api_key=GEMINI_API_KEY)

logger = logging.getLogger(__name__)

# System Prompt Template
SYSTEM_PROMPT = """You are the AI Gamemaster for 'The System', a Solo Leveling inspired productivity tracker.
Your job is to classify a user's task log into a specific rank, assign base XP, and determine the primary stat it improves.

The user will provide a raw text input describing what they did.
Analyze the input based on the following criteria:

Ranks & Base XP:
- E (Trivial): 10 XP (Drink water, make bed)
- D (Easy): 25 XP (20-min walk, read 10 pages)
- C (Moderate): 50 XP (1hr study session, gym workout)
- B (Hard): 100 XP (Build a feature, 10km run)
- A (Very Hard): 200 XP (Complete a project module)
- S (Legendary): 500 XP (Ship a product, 24hr hackathon)

Stats (Choose ONE):
- Strength (Physical exertion)
- Agility (Speed, reflexes, cardio)
- Intelligence (Learning, coding, deep work)
- Endurance (Discipline, long-duration tasks, habit consistency)
- Charisma (Social, communication, leadership)

Return ONLY a valid JSON object matching this schema. Do not include markdown code blocks or any other text.
{
    "task_name": "Short 3-5 word summary",
    "rank": "E|D|C|B|A|S",
    "stat": "Strength|Agility|Intelligence|Endurance|Charisma",
    "xp_awarded": <integer>,
    "ai_message": "A brief, in-character system message (e.g., '[System] A new skill has been registered.')"
}
"""


def _extract_json(text: str) -> Dict[str, Any]:
    """Fallback parser for the raw AI output if it includes markdown."""
    try:
        # Check if wrapped in code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI JSON response: {e}\\nRaw output: {text}")
        return None

def _fallback_assessment(raw_input: str) -> dict:
    """Default E-rank assessment when LLM parsing fails."""
    return {
        "task_name": raw_input[:60].strip(),
        "rank": "E",
        "stat_type": "Endurance",
        "reasoning": "Parsing failure. Minimum reward assigned.",
        "verified": True,
    }

def _validate_assessment(result: dict) -> dict:
    """Ensure all required fields exist and values are valid."""
    valid_ranks = {"E", "D", "C", "B", "A", "S"}
    valid_stats = {"Strength", "Intelligence", "Agility", "Endurance", "Charisma"}

    # Normalize rank
    rank = str(result.get("rank", "E")).upper().strip()
    if rank not in valid_ranks:
        rank = "E"
    result["rank"] = rank

    # Normalize stat_type. Fallback looks for 'stat' or 'stat_type'
    stat_raw = result.get("stat_type", result.get("stat", "Endurance"))
    stat = str(stat_raw).strip().title()
    if stat not in valid_stats:
        stat = "Endurance"
    result["stat_type"] = stat

    # Ensure other fields
    if not result.get("task_name"):
        result["task_name"] = "Unknown Task"
    if not result.get("reasoning"):
        # map ai_message to reasoning or use default
        result["reasoning"] = result.get("ai_message", "Assessment complete.")
    result["verified"] = result.get("verified", True)

    return result

async def assess_task(raw_input: str) -> dict:
    """
    Sends the raw task input to Gemini via google.generativeai,
    returns the parsed JSON assessment.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return _fallback_assessment(raw_input)

    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2}
        )
        
        response = await model.generate_content_async(raw_input)
        raw_response = response.text
        print(f"DEBUG raw_response: {raw_response}")

        result = _extract_json(raw_response)
        if result is None:
            return _fallback_assessment(raw_input)

        return _validate_assessment(result)
    except Exception as e:
        logger.error(f"DEBUG: Exception in assess_task: {e}")
        return _fallback_assessment(raw_input)
