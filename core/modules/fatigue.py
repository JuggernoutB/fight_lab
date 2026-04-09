# core/fatigue.py - Fatigue system

from ..config import CONFIG

# Fatigue level constants
FATIGUE_LEVEL_FRESH = 0
FATIGUE_LEVEL_TIRED = 1
FATIGUE_LEVEL_EXHAUSTED = 2

def get_fatigue_effects():
    """Get fatigue effects using current config values"""
    return {
        FATIGUE_LEVEL_FRESH: {
            'attack': CONFIG["fresh_multiplier"],
            'crit': CONFIG["fresh_multiplier"],
            'dodge': CONFIG["fresh_multiplier"],
            'block': CONFIG["fresh_multiplier"],
            'block_break': CONFIG["fresh_multiplier"]
        },
        FATIGUE_LEVEL_TIRED: {
            'attack': CONFIG["tired_multiplier"],
            'crit': CONFIG["tired_multiplier"],
            'dodge': CONFIG["tired_multiplier"],
            'block': CONFIG["tired_multiplier"],
            'block_break': CONFIG["tired_multiplier"]
        },
        FATIGUE_LEVEL_EXHAUSTED: {
            'attack': CONFIG["exhausted_multiplier"],
            'crit': CONFIG["exhausted_multiplier"],
            'dodge': CONFIG["exhausted_multiplier"],
            'block': CONFIG["exhausted_multiplier"],
            'block_break': CONFIG["exhausted_multiplier"]
        }
    }

# Legacy exports for backwards compatibility
STAMINA_NORMAL_THRESHOLD = CONFIG["stamina_fresh_threshold"]

def get_stamina_level(stamina: int) -> int:
    """
    Determine fatigue level based on current stamina
    0 = Fresh (>60 stamina)
    1 = Tired (30-60 stamina)
    2 = Exhausted (<30 stamina)
    """
    if stamina > CONFIG["stamina_fresh_threshold"]:
        return FATIGUE_LEVEL_FRESH
    elif stamina > CONFIG["stamina_tired_threshold"]:
        return FATIGUE_LEVEL_TIRED
    return FATIGUE_LEVEL_EXHAUSTED

def get_fatigue_multiplier(stamina: int, mechanic: str) -> float:
    """Get fatigue multiplier for specific combat mechanic"""
    level = get_stamina_level(stamina)
    fatigue_effects = get_fatigue_effects()
    return fatigue_effects[level].get(mechanic, 1.0)