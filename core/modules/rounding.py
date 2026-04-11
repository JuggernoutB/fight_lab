# core/modules/rounding.py - Integer HP and probabilistic damage rounding

import random
import math

def round_hp_to_int(hp_value: float) -> int:
    """
    Round HP to integer using standard rounding rules.

    Args:
        hp_value: Float HP value to round

    Returns:
        Integer HP value (≥0.5 rounds up, <0.5 rounds down)
    """
    return round(hp_value)

def round_damage_probabilistic(damage_value: float) -> int:
    """
    Round damage using probabilistic rounding based on fractional part.

    Example: 10.42 → 42% chance to round to 11, 58% chance to round to 10

    Args:
        damage_value: Float damage value to round

    Returns:
        Integer damage value using probabilistic rounding
    """
    if damage_value < 0:
        return 0

    integer_part = int(damage_value)
    fractional_part = damage_value - integer_part

    # Use fractional part as probability to round up
    if random.random() < fractional_part:
        return integer_part + 1
    else:
        return integer_part