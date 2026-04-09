# state/fighter_factory.py - Proper fighter creation from stats

from .fight_state import FighterState
from core.api import get_initial_stamina
from core.modules.ehp import EHPDamageCalculator  # Direct import for internal use


def create_fighter(hp_stat: int, attack_stat: int, defense_stat: int, agility_stat: int, role: str) -> FighterState:
    """
    Create fighter from base stats (8-18 range)

    Args:
        hp_stat: Base HP stat (8-18)
        attack_stat: Base attack stat (8-18)
        defense_stat: Base defense stat (8-18)
        agility_stat: Base agility stat (8-18)
        role: Fighter role (BRUISER, ASSASSIN, etc.)

    Returns:
        FighterState with computed HP and initial stamina
    """
    calculator = EHPDamageCalculator()

    # Compute actual HP from stat using EHP formula
    actual_hp = calculator.calculate_base_hp(hp_stat)

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


def create_fighter_balanced(role: str) -> FighterState:
    """
    Create fighter with balanced stats for testing

    Args:
        role: Fighter role

    Returns:
        FighterState with balanced 12-14 stat range
    """
    if role == "BRUISER":
        return create_fighter(hp_stat=15, attack_stat=12, defense_stat=15, agility_stat=8, role=role)
    elif role == "ASSASSIN":
        return create_fighter(hp_stat=10, attack_stat=16, defense_stat=8, agility_stat=16, role=role)
    elif role == "TANK":
        return create_fighter(hp_stat=18, attack_stat=8, defense_stat=18, agility_stat=8, role=role)
    elif role == "SKIRMISHER":
        return create_fighter(hp_stat=12, attack_stat=14, defense_stat=12, agility_stat=14, role=role)
    else:
        # Default balanced
        return create_fighter(hp_stat=12, attack_stat=12, defense_stat=12, agility_stat=12, role=role)


def create_fighter_random(role: str) -> FighterState:
    """
    Create fighter with random stats in proper 8-18 range

    Args:
        role: Fighter role

    Returns:
        FighterState with randomized stats
    """
    import random

    return create_fighter(
        hp_stat=random.randint(8, 18),
        attack_stat=random.randint(8, 18),
        defense_stat=random.randint(8, 18),
        agility_stat=random.randint(8, 18),
        role=role
    )


def print_fighter_stats(fighter: FighterState) -> None:
    """Debug helper to print fighter stats"""
    print(f"Role: {fighter.role}")
    print(f"Stats: HP={getattr(fighter, 'hp_stat', '?')}, ATK={fighter.attack}, DEF={fighter.defense}, AGI={fighter.agility}")
    print(f"Computed: HP={fighter.hp:.1f}, Stamina={fighter.stamina}")