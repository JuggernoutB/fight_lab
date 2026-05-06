# core/zones.py - Combat zones and zone multipliers

ZONES = ["head", "chest", "abdomen", "hips", "legs"]

# Base zone multipliers (before protection modifiers)
BASE_ZONE_MULTIPLIERS = {
    "head": 1.0,
    "chest": 0.9,
    "abdomen": 0.9,
    "hips": 0.9,
    "legs": 0.95,
}

# Legacy support - will be replaced by get_zone_multiplier()
ZONE_MULTIPLIERS = BASE_ZONE_MULTIPLIERS.copy()


def get_zone_multiplier(zone: str, defender_modifiers=None) -> float:
    """
    Get effective zone multiplier accounting for protection modifiers

    Args:
        zone: Zone name (head, chest, abdomen, hips, legs)
        defender_modifiers: CombatModifiers object (optional)

    Returns:
        Effective zone multiplier after protection

    Example:
        Base legs multiplier: 0.95
        Protection modifier: 0.01
        Final multiplier: 0.95 - 0.01 = 0.94
    """
    base_multiplier = BASE_ZONE_MULTIPLIERS.get(zone, 1.0)

    if defender_modifiers is None:
        return base_multiplier

    # Get zone-specific protection
    protection = defender_modifiers.get_zone_protection(zone)

    # Apply protection as reduction to zone multiplier
    # Higher protection = lower zone multiplier = less damage
    final_multiplier = max(0.1, base_multiplier - protection)

    return final_multiplier