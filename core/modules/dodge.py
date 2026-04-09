# core/dodge.py - Dodge mechanics

import random
from typing import Tuple
from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def apply_dodge(dmg: float, atk: int, agi: int, defender_stamina: int) -> Tuple[float, str]:
    diff = agi - atk
    base_chance = max(CONFIG["min_dodge_chance"], min(CONFIG["max_dodge_chance"],
                     CONFIG["base_dodge_chance"] + diff * CONFIG["agi_diff_dodge_scale"]))

    # Apply fatigue to dodge chance
    fatigue_multiplier = get_fatigue_multiplier(defender_stamina, 'dodge')
    chance = base_chance * fatigue_multiplier

    roll = random.random()
    if roll < chance * CONFIG["full_dodge_ratio"]:
        return 0.0, "dodge"
    if roll < chance:
        return dmg * CONFIG["glance_damage_ratio"], "glance"
    return dmg, "none"