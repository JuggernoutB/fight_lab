# core/crit.py - Critical hit mechanics

from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def calc_crit(att_agi: int, def_def: int, attacker_stamina: int, attacker_fatigue_bonus: float = 0.0) -> bool:
    """
    Check if critical hit occurs.
    Returns: True if critical hit landed
    """

    import random

    base_chance = max(CONFIG["min_crit_chance"], min(CONFIG["max_crit_chance"],
                     CONFIG["base_crit_chance"] + max(0, (att_agi - def_def) * CONFIG["agi_diff_crit_scale"])))
    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'crit')
    effective_chance = base_chance * fatigue_multiplier

    # Apply fatigue bonus
    effective_chance += attacker_fatigue_bonus

    return random.random() < effective_chance

def calc_crit_chance_only(att_agi: int, def_def: int, attacker_stamina: int) -> float:
    """Legacy function for backward compatibility - returns only chance value"""
    base_chance = max(CONFIG["min_crit_chance"], min(CONFIG["max_crit_chance"],
                     CONFIG["base_crit_chance"] + max(0, (att_agi - def_def) * CONFIG["agi_diff_crit_scale"])))
    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'crit')
    return base_chance * fatigue_multiplier

