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
            'block': CONFIG["fresh_multiplier"]
        },
        FATIGUE_LEVEL_TIRED: {
            'attack': CONFIG["tired_multiplier"],
            'crit': CONFIG["tired_multiplier"],
            'dodge': CONFIG["tired_multiplier"],
            'block': CONFIG["tired_multiplier"]
        },
        FATIGUE_LEVEL_EXHAUSTED: {
            'attack': CONFIG["exhausted_multiplier"],
            'crit': CONFIG["exhausted_multiplier"],
            'dodge': CONFIG["exhausted_multiplier"],
            'block': CONFIG["exhausted_multiplier"]
        }
    }

# Legacy exports for backwards compatibility
STAMINA_NORMAL_THRESHOLD = CONFIG["stamina_fresh_threshold"]

def get_stamina_level(stamina: int) -> int:
    """
    Determine fatigue level based on current stamina
    0 = Fresh
    1 = Tired
    2 = Exhausted
    """
    if stamina > CONFIG["stamina_fresh_threshold"]:
        return FATIGUE_LEVEL_FRESH
    elif stamina > CONFIG["stamina_tired_threshold"]:
        return FATIGUE_LEVEL_TIRED
    return FATIGUE_LEVEL_EXHAUSTED

def get_fatigue_multiplier(stamina: int, mechanic: str, modifiers=None) -> float:
    """
    Get fatigue multiplier for specific combat mechanic with fatigue_efficiency support

    How fatigue_efficiency works:
    - Does NOT give stamina or reduce costs directly
    - Instead REDUCES the penalty from fatigue states
    - Formula: penalty = 1.0 - base_multiplier
              reduced_penalty = penalty * (1 - fatigue_efficiency)
              final_multiplier = 1.0 - reduced_penalty

    Example: TIRED base_multiplier = 0.75, fatigue_efficiency = 0.20
             penalty = 0.25
             reduced_penalty = 0.25 * 0.8 = 0.20
             final_multiplier = 0.80

    Safe range for fatigue_efficiency: 0.02-0.10
    """
    level = get_stamina_level(stamina)
    fatigue_effects = get_fatigue_effects()
    base_multiplier = fatigue_effects[level].get(mechanic, 1.0)

    # Apply fatigue_efficiency if provided
    if modifiers and hasattr(modifiers, 'fatigue_efficiency') and modifiers.fatigue_efficiency != 0.0:
        # Safety clamp: allow negative values but prevent extreme positive values >= 1.0
        safe_efficiency = max(-0.99, min(0.99, modifiers.fatigue_efficiency))

        # Calculate penalty reduction (or increase for negative values)
        penalty = 1.0 - base_multiplier
        reduced_penalty = penalty * (1.0 - safe_efficiency)
        final_multiplier = 1.0 - reduced_penalty

        return final_multiplier

    return base_multiplier