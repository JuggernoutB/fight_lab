# core/block.py - Block and block break mechanics

import random
from ..config import CONFIG
from .fatigue import get_fatigue_multiplier

def apply_block(dmg: float, atk: int, defense: int, defender_stamina: int) -> float:
    base_reduction = max(CONFIG["min_block_reduction"], min(CONFIG["max_block_reduction"],
                        CONFIG["base_block_reduction"] + (defense - atk) * CONFIG["def_diff_block_scale"]))

    # Apply fatigue to block effectiveness
    fatigue_multiplier = get_fatigue_multiplier(defender_stamina, 'block')
    effective_reduction = base_reduction * fatigue_multiplier

    return dmg * (1 - effective_reduction)

def block_break(agility: int, defense: int, attacker_stamina: int, attacker_absorption_resource: float = 0.0) -> tuple[bool, float]:
    """
    Check if block is broken using two-stage logic:
    1. First check absorption resource (if >= 0.5)
    2. Then check standard formula

    Returns: (block_broken, updated_absorption_resource)
    """

    # Stage 1: Check absorption resource first
    #threshold = CONFIG["absorption_event_threshold"]
    #if attacker_absorption_resource >= threshold:
    #    absorption_chance = attacker_absorption_resource  # Direct probability threshold-1.0
    #    if random.random() < absorption_chance:
    #        # Block break triggered by absorption resource
    #        return True, 0.0  # Reset resource on successful trigger

    # Stage 2: Standard formula check
    base_chance = max(CONFIG["min_block_break_chance"], min(CONFIG["max_block_break_chance"],
                     CONFIG["base_block_break_chance"] + (agility - defense) * CONFIG["agi_block_break_scale"]))

    # Apply fatigue to block break chance
    fatigue_multiplier = get_fatigue_multiplier(attacker_stamina, 'block_break')
    effective_chance = base_chance * fatigue_multiplier

    if random.random() < effective_chance:
        # Block break triggered by standard formula (resource unchanged)
        return True, attacker_absorption_resource

    # No block break (resource unchanged)
    return False, attacker_absorption_resource