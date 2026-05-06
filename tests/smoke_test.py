"""Smoke test — verify DB init, user seeding, and task processing."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import init_database
from db.models import get_user_stats, award_task, get_task_history

# Initialize
init_database()
print("[OK] Database initialized")

# Check default user
stats = get_user_stats(1)
assert stats is not None, "Default user not found!"
print(f"[OK] Hunter: {stats['username']}, Level: {stats['level']}, XP: {stats['total_xp']}")

# Simulate a task award
fake_assessment = {
    "task_name": "Smoke Test Task",
    "rank": "C",
    "stat_type": "Intelligence",
    "reasoning": "System verification.",
    "verified": True,
    "raw_input": "test task submission",
}
result = award_task(1, fake_assessment)
print(f"[OK] Task awarded: +{result['xp_gained']} XP, Level {result['new_level']}")

# Check history
history = get_task_history(1, limit=5)
assert len(history) > 0, "Task history is empty!"
print(f"[OK] Task history: {len(history)} entries")

# Re-check stats
stats = get_user_stats(1)
print(f"[OK] Updated stats: Level {stats['level']}, XP {stats['total_xp']}, INT {stats['intelligence']}")

print("\n=== ALL SMOKE TESTS PASSED ===")
