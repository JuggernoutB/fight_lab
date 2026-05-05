# core/modules/rounding.py - Integer HP and probabilistic damage rounding

import random
import math
from ..config import CONFIG

def round_hp_to_int(hp_value: float) -> int:
    """
    Round HP to integer using standard rounding rules.

    Args:
        hp_value: Float HP value to round

    Returns:
        Integer HP value (≥0.5 rounds up, <0.5 rounds down)
    """
    return round(hp_value)

def apply_damage_variance(damage_value: float) -> float:
    """
    Apply random variance to damage before rounding.

    Multiplies damage by a random factor within configured range.

    Args:
        damage_value: Float damage value to apply variance to

    Returns:
        Float damage value with variance applied
    """
    if not CONFIG["damage_variance_enabled"]:
        return damage_value

    if damage_value <= 0:
        return damage_value

    # Generate random multiplier between min and max variance
    variance_multiplier = random.uniform(
        CONFIG["damage_variance_min"],
        CONFIG["damage_variance_max"]
    )

    return damage_value * variance_multiplier


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