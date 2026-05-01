# core/dodge.py - Dodge mechanics

import random
from typing import Tuple
from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def apply_dodge(dmg: float, atk_attack: int, def_agility: int, defender_stamina: int, atk_agility: int = None) -> Tuple[float, str]:
    agi_diff = def_agility - atk_agility
    agi_bonus = max(0, agi_diff) * CONFIG["agi_diff_dodge_scale"]

    base_chance = max(CONFIG["min_dodge_chance"], min(CONFIG["max_dodge_chance"],
                     CONFIG["base_dodge_chance"] + agi_bonus))

    # Apply fatigue to dodge chance
    fatigue_multiplier = get_fatigue_multiplier(defender_stamina, 'dodge')
    chance = base_chance * fatigue_multiplier

    roll = random.random()
    if roll < chance:
        return 0.0, "dodge"
    return dmg, "hit"