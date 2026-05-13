# core/block.py - Block mechanics

import random
from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def apply_block(dmg: float, atk: int, defense: int, defender_stamina: int, defender_modifiers=None) -> float:
    base_reduction = max(CONFIG["min_block_reduction"], min(CONFIG["max_block_reduction"],
                        CONFIG["base_block_reduction"] + (defense - atk) * CONFIG["def_diff_block_scale"]))

    # Apply equipment block power bonus
    if defender_modifiers:
        base_reduction += defender_modifiers.block_power

    fatigue_multiplier = get_fatigue_multiplier(defender_stamina, 'block', defender_modifiers)
    effective_reduction = base_reduction * fatigue_multiplier

    return dmg * (1 - effective_reduction)

