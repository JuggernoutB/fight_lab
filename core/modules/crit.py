# core/crit.py - Critical hit mechanics

from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def calc_crit(att_agi: int, def_def: int, attacker_stamina: int, attacker_absorption_resource: float = 0.0) -> tuple[bool, float]:
    """
    Check if critical hit occurs using two-stage logic:
    1. First check absorption resource (if >= 0.5)
    2. Then check standard formula

    Returns: (is_crit, updated_absorption_resource)
    """

    import random

    # Stage 1: Check absorption resource first
    #threshold = CONFIG["absorption_event_threshold"]
    #if attacker_absorption_resource >= threshold:
    #    absorption_chance = attacker_absorption_resource  # Direct probability threshold-1.0
    #    if random.random() < absorption_chance:
    #        # Critical hit triggered by absorption resource
    #        return True, 0.0  # Reset resource on successful trigger

    # Stage 2: Standard formula check
    base_chance = max(CONFIG["min_crit_chance"], min(CONFIG["max_crit_chance"],
                     CONFIG["base_crit_chance"] + max(0, (att_agi - def_def) * CONFIG["agi_diff_crit_scale"])))
    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'crit')
    effective_chance = base_chance * fatigue_multiplier

    if random.random() < effective_chance:
        # Critical hit triggered by standard formula (resource unchanged)
        return True, attacker_absorption_resource

    # No critical hit (resource unchanged)
    return False, attacker_absorption_resource

def calc_crit_chance_only(att_agi: int, def_def: int, attacker_stamina: int) -> float:
    """Legacy function for backward compatibility - returns only chance value"""
    base_chance = max(CONFIG["min_crit_chance"], min(CONFIG["max_crit_chance"],
                     CONFIG["base_crit_chance"] + max(0, (att_agi - def_def) * CONFIG["agi_diff_crit_scale"])))
    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'crit')
    return base_chance * fatigue_multiplier

# Legacy exports for backwards compatibility
BASE_CRIT = CONFIG["base_crit_chance"]
AGI_SCALE = CONFIG["agi_diff_crit_scale"]
CRIT_MULT = CONFIG["crit_damage_multiplier"]