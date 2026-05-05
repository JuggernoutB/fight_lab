# state/level_system.py - Level-based fighter creation system

from typing import Dict, Tuple
from .fight_state import FighterState
from .fighter_factory import create_fighter


# Level system constants
BASE_STATS = 12  # All stats start at 3, total = 3*4 = 12
STATS_PER_LEVEL = 5  # +5 stat points per level


def level_to_stat_budget(level: int) -> int:
    """Convert level to total stat budget"""
    return BASE_STATS + (level - 1) * STATS_PER_LEVEL


def stat_budget_to_level(total_stats: int) -> int:
    """Convert total stats back to level (for analysis)"""
    return ((total_stats - BASE_STATS) // STATS_PER_LEVEL) + 1


# Role weight definitions - percentages for stat distribution
ROLE_WEIGHTS = {
    "TANK": {
        "hp": 0.35,    # 35% into HP
        "def": 0.35,   # 35% into DEF
        "atk": 0.15,   # 15% into ATK
        "agi": 0.15    # 15% into AGI
    },
    "BRUISER": {
        "hp": 0.30,    # 30% into HP
        "atk": 0.30,   # 30% into ATK
        "def": 0.25,   # 25% into DEF
        "agi": 0.15    # 15% into AGI
    },
    "ASSASSIN": {
        "atk": 0.40,   # 40% into ATK
        "agi": 0.40,   # 40% into AGI
        "hp": 0.10,    # 10% into HP
        "def": 0.10    # 10% into DEF
    },
    "SKIRMISHER": {
        "agi": 0.40,   # 40% into AGI
        "atk": 0.25,   # 25% into ATK
        "def": 0.20,   # 20% into DEF
        "hp": 0.15     # 15% into HP
    },
    "UNIVERSAL": {
        "hp": 0.25,    # 25% into HP
        "atk": 0.25,   # 25% into ATK
        "def": 0.25,   # 25% into DEF
        "agi": 0.25    # 25% into AGI
    },

    # 2-stat builds (50/50 distribution)
    "ATK_DEF": {
        "atk": 0.40,   # 40% into ATK
        "def": 0.40,   # 40% into DEF
        "hp": 0.10,    # 10% into HP
        "agi": 0.10    # 10% into AGI
    },
    "ATK_HP": {
        "atk": 0.40,   # 40% into ATK
        "hp": 0.40,    # 40% into HP
        "def": 0.10,   # 10% into DEF
        "agi": 0.10    # 10% into AGI
    },
    "ATK_AGI": {
        "atk": 0.40,   # 40% into ATK
        "agi": 0.40,   # 40% into AGI
        "hp": 0.10,    # 10% into HP
        "def": 0.10    # 10% into DEF
    },
    "AGI_DEF": {
        "agi": 0.40,   # 40% into AGI
        "def": 0.40,   # 40% into DEF
        "atk": 0.10,   # 10% into ATK
        "hp": 0.10     # 10% into HP
    },
    "AGI_HP": {
        "agi": 0.40,   # 40% into AGI
        "hp": 0.40,    # 40% into HP
        "atk": 0.10,   # 10% into ATK
        "def": 0.10    # 10% into DEF
    },
    "HP_DEF": {
        "hp": 0.40,    # 40% into HP
        "def": 0.40,   # 40% into DEF
        "atk": 0.10,   # 10% into ATK
        "agi": 0.10    # 10% into AGI
    },

    # 3-stat builds (33.3/33.3/33.3 distribution for main stats)
    "ATK_HP_DEF": {
        "atk": 0.33,   # 33% into ATK
        "hp": 0.33,    # 33% into HP
        "def": 0.33,   # 33% into DEF
        "agi": 0.01    # 1% into AGI (minimal)
    },
    "ATK_HP_AGI": {
        "atk": 0.33,   # 33% into ATK
        "hp": 0.33,    # 33% into HP
        "agi": 0.33,   # 33% into AGI
        "def": 0.01    # 1% into DEF (minimal)
    },
    "ATK_DEF_AGI": {
        "atk": 0.33,   # 33% into ATK
        "def": 0.33,   # 33% into DEF
        "agi": 0.33,   # 33% into AGI
        "hp": 0.01     # 1% into HP (minimal)
    },
    "AGI_HP_DEF": {
        "agi": 0.33,   # 33% into AGI
        "hp": 0.33,    # 33% into HP
        "def": 0.33,   # 33% into DEF
        "atk": 0.01    # 1% into ATK (minimal)
    },
    "AGI_HP_ATK": {
        "agi": 0.33,   # 33% into AGI
        "hp": 0.33,    # 33% into HP
        "atk": 0.33,   # 33% into ATK
        "def": 0.01    # 1% into DEF (minimal)
    },
    "AGI_DEF_ATK": {
        "agi": 0.33,   # 33% into AGI
        "def": 0.33,   # 33% into DEF
        "atk": 0.33,   # 33% into ATK
        "hp": 0.01     # 1% into HP (minimal)
    },
    "DEF_HP_AGI": {
        "def": 0.33,   # 33% into DEF
        "hp": 0.33,    # 33% into HP
        "agi": 0.33,   # 33% into AGI
        "atk": 0.01    # 1% into ATK (minimal)
    },
    "DEF_HP_ATK": {
        "def": 0.33,   # 33% into DEF
        "hp": 0.33,    # 33% into HP
        "atk": 0.33,   # 33% into ATK
        "agi": 0.01    # 1% into AGI (minimal)
    }
}


def distribute_stats_by_weights(total_stats: int, weights: Dict[str, float]) -> Dict[str, int]:
    """
    Distribute total stat points according to role weights

    Args:
        total_stats: Total stat budget to distribute
        weights: Dict with stat weights (hp, atk, def, agi)

    Returns:
        Dict with actual stat values
    """
    # Start with minimum 3 in each stat
    stats = {"hp": 3, "atk": 3, "def": 3, "agi": 3}
    remaining_points = total_stats - 12  # 12 points used for base 3s

    # Distribute remaining points according to weights
    if remaining_points > 0:
        for stat, weight in weights.items():
            additional = int(remaining_points * weight)
            stats[stat] += additional

        # Handle rounding - add leftover points to highest weighted stat
        current_total = sum(stats.values())
        diff = total_stats - current_total

        if diff != 0:
            max_weight_stat = max(weights, key=weights.get)
            stats[max_weight_stat] += diff

    return stats


def create_fighter_by_level(level: int, role: str) -> FighterState:
    """
    Create fighter using level-based stat distribution

    Args:
        level: Fighter level (1+)
        role: Role name (TANK, BRUISER, etc.)

    Returns:
        FighterState with level-appropriate stats
    """
    if role not in ROLE_WEIGHTS:
        raise ValueError(f"Unknown role: {role}. Available: {list(ROLE_WEIGHTS.keys())}")

    total_stats = level_to_stat_budget(level)
    weights = ROLE_WEIGHTS[role]
    stats = distribute_stats_by_weights(total_stats, weights)

    return create_fighter(
        hp_stat=stats["hp"],
        attack_stat=stats["atk"],
        defense_stat=stats["def"],
        agility_stat=stats["agi"],
        role=role
    )


def create_custom_fighter_by_level(level: int, role: str, custom_stats: Dict[str, int]) -> FighterState:
    """
    Create custom fighter at specific level with custom stat distribution

    Args:
        level: Fighter level (for validation)
        role: Role name
        custom_stats: Dict with hp, atk, def, agi values

    Returns:
        FighterState with custom stats
    """
    expected_total = level_to_stat_budget(level)
    actual_total = sum(custom_stats.values())

    if actual_total != expected_total:
        raise ValueError(f"Stat total mismatch: expected {expected_total} for level {level}, got {actual_total}")

    # Validate minimum stats
    for stat, value in custom_stats.items():
        if value < 3:
            raise ValueError(f"Stat {stat} cannot be below 3, got {value}")

    return create_fighter(
        hp_stat=custom_stats["hp"],
        attack_stat=custom_stats["atk"],
        defense_stat=custom_stats["def"],
        agility_stat=custom_stats["agi"],
        role=role
    )


def analyze_level_distribution(fighters: list) -> Dict:
    """Analyze level distribution of a list of fighters"""
    levels = []
    for fighter in fighters:
        hp_stat = getattr(fighter, 'hp_stat', 0)
        total = hp_stat + fighter.attack + fighter.defense + fighter.agility
        level = stat_budget_to_level(total)
        levels.append(level)

    return {
        "levels": levels,
        "min_level": min(levels),
        "max_level": max(levels),
        "avg_level": sum(levels) / len(levels),
        "level_spread": max(levels) - min(levels)
    }


def print_level_examples():
    """Print examples of different level builds for documentation"""
    print("=== LEVEL SYSTEM EXAMPLES ===")
    print()

    for level in [1, 5, 9, 10]:
        total = level_to_stat_budget(level)
        print(f"Level {level}: {total} stat points")

        for role in ["TANK", "BRUISER", "ASSASSIN"]:
            fighter = create_fighter_by_level(level, role)
            hp_stat = getattr(fighter, 'hp_stat', 0)
            print(f"  {role:9s}: HP={hp_stat:2d} ATK={fighter.attack:2d} DEF={fighter.defense:2d} AGI={fighter.agility:2d}")
        print()