"""
THE SYSTEM — Job Class Progression
══════════════════════════════════
Handles unlocking hidden classes based on stat milestones.
"""

import logging

logger = logging.getLogger(__name__)

# Threshold required to unlock a job
JOB_STAT_THRESHOLD = 50

# Map primary stats to Job Classes
JOB_CLASSES = {
    "agility": "Assassin",
    "intelligence": "Mage",
    "strength": "Fighter",
    "endurance": "Tank",
    "charisma": "Commander"
}

def check_job_change(current_stats: dict) -> tuple[bool, str]:
    """
    Check if a hunter has reached a stat threshold to unlock a new Job Class.
    Returns (True/False, New_Job_Name)
    """
    # If they already have a class, they can't change it (for now)
    if current_stats.get("job_class") and current_stats["job_class"] != "None":
        return False, ""

    # Find the highest stat that meets the threshold
    highest_stat_name = None
    highest_val = 0
    
    for stat_name in JOB_CLASSES.keys():
        val = current_stats.get(stat_name, 0)
        if val >= JOB_STAT_THRESHOLD and val > highest_val:
            highest_val = val
            highest_stat_name = stat_name
            
    if highest_stat_name:
        new_class = JOB_CLASSES[highest_stat_name]
        logger.info(f"Job Change triggered: {new_class} unlocked!")
        return True, new_class
        
    return False, ""
