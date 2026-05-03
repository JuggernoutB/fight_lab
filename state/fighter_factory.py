# state/fighter_factory.py - Proper fighter creation from stats

from .fight_state import FighterState
from core.api import get_initial_stamina
from core.modules.ehp import EHPDamageCalculator  # Direct import for internal use
from core.modules.rounding import round_hp_to_int


def create_fighter(hp_stat: int, attack_stat: int, defense_stat: int, agility_stat: int, role: str) -> FighterState:
    """
    Create fighter from base stats (3-18 range)

    Args:
        hp_stat: Base HP stat (3-18)
        attack_stat: Base attack stat (3-18)
        defense_stat: Base defense stat (3-18)
        agility_stat: Base agility stat (3-18)
        role: Fighter role (BRUISER, ASSASSIN, etc.)

    Returns:
        FighterState with computed HP and initial stamina
    """
    calculator = EHPDamageCalculator()

    # Compute actual HP from stat using EHP formula and round to integer
    actual_hp_float = calculator.calculate_base_hp(hp_stat)
    actual_hp = round_hp_to_int(actual_hp_float)

    # Create fighter with computed values
    fighter = FighterState(
        hp=actual_hp,                        # Computed from hp_stat
        stamina=get_initial_stamina(),
        role=role,
        attack=attack_stat,
        defense=defense_stat,
        agility=agility_stat
    )

    # Store original stat for reference
    fighter.hp_stat = hp_stat

    return fighter


def create_fighter_balanced_level(role: str, level: int = 12) -> FighterState:
    """
    Create fighter with role-based stats at specified level
    All fighters get exactly the same total stat points: 12 + (level-1) * 5

    Args:
        role: Fighter role
        level: Stat level (1+), determines total stat budget

    Returns:
        FighterState with role-based stat distribution at given level
    """
    # Clamp level to valid range
    level = max(3, min(18, level))

    # Calculate total stat budget using the same system as benchmark: 12 + (level-1) * 5
    # This ensures compatibility with level_system.py
    BASE_STATS = 12  # All stats start at 3, total = 3*4 = 12
    STATS_PER_LEVEL = 5  # +5 stat points per level
    total_stats = BASE_STATS + (level - 1) * STATS_PER_LEVEL

    if role == "BRUISER":
        # HP/DEF focused, balanced ATK, low AGI
        hp_stat = total_stats // 4 + 3    # Higher HP
        def_stat = total_stats // 4 + 3   # Higher DEF
        atk_stat = total_stats // 4       # Average ATK
        agi_stat = total_stats - hp_stat - def_stat - atk_stat  # Remaining points

    elif role == "ASSASSIN":
        # ATK/AGI focused, low HP/DEF
        atk_stat = total_stats // 4 + 4   # Higher ATK
        agi_stat = total_stats // 4 + 4   # Higher AGI
        hp_stat = total_stats // 4 - 2    # Lower HP
        def_stat = total_stats - atk_stat - agi_stat - hp_stat  # Remaining points

    elif role == "TANK":
        # HP/DEF maximized, low ATK/AGI
        hp_stat = total_stats // 4 + 4    # Highest HP
        def_stat = total_stats // 4 + 4   # Highest DEF
        atk_stat = total_stats // 4 - 2   # Lower ATK
        agi_stat = total_stats - hp_stat - def_stat - atk_stat  # Remaining points

    elif role == "SKIRMISHER":
        # AGI focused, balanced other stats
        agi_stat = total_stats // 4 + 3   # Higher AGI
        atk_stat = total_stats // 4 + 1   # Slightly higher ATK
        def_stat = total_stats // 4 + 1   # Slightly higher DEF
        hp_stat = total_stats - agi_stat - atk_stat - def_stat  # Remaining points

    elif role == "ATK_DEF":
        # Attack + Defense focused
        atk_stat = total_stats // 4 + 4   # Higher ATK
        def_stat = total_stats // 4 + 4   # Higher DEF
        hp_stat = total_stats // 4 - 2    # Lower HP
        agi_stat = total_stats - atk_stat - def_stat - hp_stat  # Remaining points

    elif role == "AGI_DEF":
        # Agility + Defense focused
        agi_stat = total_stats // 4 + 4   # Higher AGI
        def_stat = total_stats // 4 + 4   # Higher DEF
        hp_stat = total_stats // 4 - 2    # Lower HP
        atk_stat = total_stats - agi_stat - def_stat - hp_stat  # Remaining points

    elif role == "AGI_HP":
        # Agility + HP focused
        agi_stat = total_stats // 4 + 4   # Higher AGI
        hp_stat = total_stats // 4 + 4    # Higher HP
        atk_stat = total_stats // 4 - 2   # Lower ATK
        def_stat = total_stats - agi_stat - hp_stat - atk_stat  # Remaining points

    elif role == "ATK_HP":
        # Attack + HP focused
        atk_stat = total_stats // 4 + 4   # Higher ATK
        hp_stat = total_stats // 4 + 4    # Higher HP
        def_stat = total_stats // 4 - 2   # Lower DEF
        agi_stat = total_stats - atk_stat - hp_stat - def_stat  # Remaining points

    else:  # UNIVERSAL or unknown
        # All stats equal
        base_stat = total_stats // 4
        remainder = total_stats % 4
        hp_stat = base_stat + (1 if remainder > 0 else 0)
        atk_stat = base_stat + (1 if remainder > 1 else 0)
        def_stat = base_stat + (1 if remainder > 2 else 0)
        agi_stat = base_stat

    # Ensure all stats are in valid range (3-18)
    hp_stat = max(3, min(18, hp_stat))
    atk_stat = max(3, min(18, atk_stat))
    def_stat = max(3, min(18, def_stat))
    agi_stat = max(3, min(18, agi_stat))

    return create_fighter(hp_stat=hp_stat, attack_stat=atk_stat, defense_stat=def_stat, agility_stat=agi_stat, role=role)


def create_fighter_balanced(role: str) -> FighterState:
    """
    Create fighter with balanced stats for testing

    Args:
        role: Fighter role

    Returns:
        FighterState with appropriate stat distribution
    """
    # Extreme builds (1 stat)
    if role == "ATK":
        return create_fighter(hp_stat=3, attack_stat=18, defense_stat=3, agility_stat=3, role=role)
    elif role == "AGI":
        return create_fighter(hp_stat=3, attack_stat=3, defense_stat=3, agility_stat=18, role=role)
    elif role == "DEF":
        return create_fighter(hp_stat=3, attack_stat=3, defense_stat=18, agility_stat=3, role=role)
    elif role == "HP":
        return create_fighter(hp_stat=18, attack_stat=3, defense_stat=3, agility_stat=3, role=role)

    # 2-stat builds
    elif role == "ATK_AGI":
        return create_fighter(hp_stat=3, attack_stat=15, defense_stat=3, agility_stat=12, role=role)
    elif role == "ATK_DEF":
        return create_fighter(hp_stat=3, attack_stat=15, defense_stat=12, agility_stat=3, role=role)
    elif role == "ATK_HP":
        return create_fighter(hp_stat=12, attack_stat=15, defense_stat=3, agility_stat=3, role=role)
    elif role == "AGI_DEF":
        return create_fighter(hp_stat=3, attack_stat=3, defense_stat=15, agility_stat=12, role=role)
    elif role == "AGI_HP":
        return create_fighter(hp_stat=12, attack_stat=3, defense_stat=3, agility_stat=15, role=role)
    elif role == "HP_DEF":
        return create_fighter(hp_stat=15, attack_stat=3, defense_stat=12, agility_stat=3, role=role)

    # 3-stat builds
    elif role == "ATK_HP_DEF":
        return create_fighter(hp_stat=6, attack_stat=15, defense_stat=6, agility_stat=3, role=role)
    elif role == "ATK_HP_AGI":
        return create_fighter(hp_stat=6, attack_stat=15, defense_stat=3, agility_stat=6, role=role)
    elif role == "ATK_DEF_AGI":
        return create_fighter(hp_stat=3, attack_stat=15, defense_stat=6, agility_stat=6, role=role)
    elif role == "AGI_HP_DEF":
        return create_fighter(hp_stat=6, attack_stat=3, defense_stat=6, agility_stat=15, role=role)
    elif role == "AGI_HP_ATK":
        return create_fighter(hp_stat=6, attack_stat=6, defense_stat=3, agility_stat=15, role=role)
    elif role == "AGI_DEF_ATK":
        return create_fighter(hp_stat=3, attack_stat=6, defense_stat=6, agility_stat=15, role=role)
    elif role == "DEF_HP_AGI":
        return create_fighter(hp_stat=6, attack_stat=3, defense_stat=15, agility_stat=6, role=role)
    elif role == "DEF_HP_ATK":
        return create_fighter(hp_stat=6, attack_stat=6, defense_stat=15, agility_stat=3, role=role)
    elif role == "DEF_AGI_ATK":
        return create_fighter(hp_stat=3, attack_stat=6, defense_stat=15, agility_stat=6, role=role)
    elif role == "HP_ATK_DEF":
        return create_fighter(hp_stat=15, attack_stat=6, defense_stat=6, agility_stat=3, role=role)
    elif role == "HP_ATK_AGI":
        return create_fighter(hp_stat=15, attack_stat=6, defense_stat=3, agility_stat=6, role=role)
    elif role == "HP_AGI_DEF":
        return create_fighter(hp_stat=15, attack_stat=3, defense_stat=6, agility_stat=6, role=role)

    # Universal
    elif role == "UNIVERSAL":
        return create_fighter(hp_stat=8, attack_stat=8, defense_stat=8, agility_stat=8, role=role)

    else:
        # Default universal
        return create_fighter(hp_stat=8, attack_stat=8, defense_stat=8, agility_stat=8, role=role)


def classify_build_role(hp_stat: int, attack_stat: int, defense_stat: int, agility_stat: int) -> tuple[str, float]:
    """
    Classify build into role using scoring system for smooth transitions

    Args:
        hp_stat, attack_stat, defense_stat, agility_stat: Fighter stats

    Returns:
        Tuple of (role_name, confidence) where confidence indicates role purity
    """
    # Normalize stats to prevent stat inflation bias
    total = hp_stat + attack_stat + defense_stat + agility_stat
    hp_n = hp_stat / total
    atk_n = attack_stat / total
    def_n = defense_stat / total
    agi_n = agility_stat / total

    # Calculate role scores using weighted combinations
    scores = {}

    # 3 stat builds
    scores["ATK_HP_DEF"] = atk_n * 0.5 + hp_n * 0.25 + def_n * 0.25
    scores["ATK_HP_AGI"] = atk_n * 0.5 + hp_n * 0.25 + agi_n * 0.25
    scores["ATK_DEF_AGI"] = atk_n * 0.5 + def_n * 0.25 + agi_n * 0.25
    scores["AGI_HP_DEF"] = agi_n * 0.5 + def_n * 0.25 + hp_n * 0.25
    scores["AGI_HP_ATK"] = agi_n * 0.5 + atk_n * 0.25 + hp_n * 0.25
    scores["AGI_DEF_ATK"] = agi_n * 0.5 + atk_n * 0.25 + def_n * 0.25
    scores["DEF_HP_AGI"] = def_n * 0.5 + agi_n * 0.25 + hp_n * 0.25
    scores["DEF_HP_ATK"] = def_n * 0.5 + atk_n * 0.25 + hp_n * 0.25
    scores["DEF_AGI_ATK"] = def_n * 0.5 + atk_n * 0.25 + agi_n * 0.25
    scores["HP_ATK_DEF"] = hp_n * 0.5 + atk_n * 0.25 + def_n * 0.25
    scores["HP_ATK_AGI"] = hp_n * 0.5 + atk_n * 0.25 + agi_n * 0.25
    scores["HP_AGI_DEF"] = hp_n * 0.5 + def_n * 0.25 + agi_n * 0.25

    # 2 stat builds
    scores["ATK_AGI"] = atk_n * 0.5 + agi_n * 0.5
    scores["ATK_DEF"] = atk_n * 0.5 + def_n * 0.5
    scores["ATK_HP"] = atk_n * 0.5 + hp_n * 0.5
    scores["AGI_DEF"] = agi_n * 0.5 + def_n * 0.5
    scores["AGI_HP"] = agi_n * 0.5 + hp_n * 0.5
    scores["HP_DEF"] = hp_n * 0.5 + def_n * 0.5

    # 1 stat extreme builds (all points in one stat)
    # Lower multiplier to allow mixed builds to compete
    scores["ATK"] = atk_n * 0.65
    scores["AGI"] = agi_n * 0.65
    scores["DEF"] = def_n * 0.65
    scores["HP"] = hp_n * 0.65

    # UNIVERSAL: Balanced builds (high when stats are even)
    stat_range = max([hp_n, atk_n, def_n, agi_n]) - min([hp_n, atk_n, def_n, agi_n])
    scores["UNIVERSAL"] = 1.0 - stat_range * 4  # Scale range penalty

    # Find best role and calculate confidence
    best_role = max(scores, key=scores.get)
    sorted_scores = sorted(scores.values(), reverse=True)
    confidence = sorted_scores[0] - sorted_scores[1]  # Gap between 1st and 2nd place

    return best_role, confidence


def create_fighter_random(role: str = None) -> FighterState:
    """
    Create fighter with random stats in proper 3-18 range
    If role is None, classify based on generated stats

    Args:
        role: Fighter role (optional - will be classified if None)

    Returns:
        FighterState with randomized stats and appropriate role
    """
    import random

    # Generate random stats
    hp_stat = random.randint(3, 18)
    attack_stat = random.randint(3, 18)
    defense_stat = random.randint(3, 18)
    agility_stat = random.randint(3, 18)

    # Classify role based on stats if not provided
    if role is None:
        role, confidence = classify_build_role(hp_stat, attack_stat, defense_stat, agility_stat)

    return create_fighter(
        hp_stat=hp_stat,
        attack_stat=attack_stat,
        defense_stat=defense_stat,
        agility_stat=agility_stat,
        role=role
    )


def print_fighter_stats(fighter: FighterState) -> None:
    """Debug helper to print fighter stats"""
    print(f"Role: {fighter.role}")
    print(f"Stats: HP={getattr(fighter, 'hp_stat', '?')}, ATK={fighter.attack}, DEF={fighter.defense}, AGI={fighter.agility}")
    print(f"Computed: HP={fighter.hp:.1f}, Stamina={fighter.stamina}")