# core/crit.py - Critical hit mechanics

from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def calc_crit(att_agi: int, def_def: int, attacker_stamina: int) -> float:
    base_chance = max(CONFIG["min_crit_chance"], min(CONFIG["max_crit_chance"],
                     CONFIG["base_crit_chance"] + max(0, (att_agi - def_def) * CONFIG["agi_diff_crit_scale"])))
    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'crit')
    return base_chance * fatigue_multiplier

# Legacy exports for backwards compatibility
BASE_CRIT = CONFIG["base_crit_chance"]
AGI_SCALE = CONFIG["agi_diff_crit_scale"]
CRIT_MULT = CONFIG["crit_damage_multiplier"]