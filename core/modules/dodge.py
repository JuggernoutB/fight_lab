# core/dodge.py - Dodge mechanics

import random
from typing import Tuple
from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def apply_dodge(dmg: float, atk_attack: int, def_agility: int, defender_stamina: int, atk_agility: int = None) -> Tuple[float, str]:
    # NEW: Agility vs Agility comparison for dodge
    # If defender has higher agility than attacker - bonus dodge chance
    # If defender has lower agility - only base dodge chance
    if atk_agility is not None:
        agi_diff = def_agility - atk_agility  # positive = defender faster
        agi_bonus = max(0, agi_diff) * CONFIG["agi_diff_dodge_scale"]  # only positive diff helps
    else:
        # Fallback: old logic without attacker agility
        agi_bonus = max(0, def_agility - atk_attack) * CONFIG["agi_diff_dodge_scale"]

    base_chance = max(CONFIG["min_dodge_chance"], min(CONFIG["max_dodge_chance"],
                     CONFIG["base_dodge_chance"] + agi_bonus))

    # Apply fatigue to dodge chance
    fatigue_multiplier = get_fatigue_multiplier(defender_stamina, 'dodge')
    chance = base_chance * fatigue_multiplier

    roll = random.random()
    if roll < chance * CONFIG["full_dodge_ratio"]:
        return 0.0, "dodge"
    if roll < chance:
        return dmg * CONFIG["glance_damage_ratio"], "glance"
    return dmg, "none"