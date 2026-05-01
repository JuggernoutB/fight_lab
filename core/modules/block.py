# core/block.py - Block and block break mechanics

import random
from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def apply_block(dmg: float, atk: int, defense: int, defender_stamina: int) -> float:
    base_reduction = max(CONFIG["min_block_reduction"], min(CONFIG["max_block_reduction"],
                        CONFIG["base_block_reduction"] + (defense - atk) * CONFIG["def_diff_block_scale"]))

    fatigue_multiplier = get_fatigue_multiplier(defender_stamina, 'block')
    effective_reduction = base_reduction * fatigue_multiplier

    return dmg * (1 - effective_reduction)

def block_break(agility: int, defense: int, attacker_stamina: int, attacker_fatigue_bonus: float = 0.0) -> bool:
    base_chance = max(CONFIG["min_block_break_chance"], min(CONFIG["max_block_break_chance"],
                     CONFIG["base_block_break_chance"] + (agility - defense) * CONFIG["agi_block_break_scale"]))

    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'block_break')
    effective_chance = base_chance * fatigue_multiplier

    effective_chance += attacker_fatigue_bonus

    return random.random() < effective_chance