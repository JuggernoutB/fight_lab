# game/run_fight.py - Clean API for Telegram Mini App Game
"""
Frontend/Game API for combat simulation
Provides simplified interface for Telegram mini app integration
"""

from state.fight_state import FightState
from state.fighter_factory import create_fighter_balanced, create_fighter_random
from simulation.game_engine import simulate_fight as engine_simulate_fight


def run_fight(fighter_a_config, fighter_b_config, options=None):
    """
    Main game API for frontend/backend integration

    Args:
        fighter_a_config: Dict with fighter A configuration
            {
                "type": "balanced" | "random",
                "role": "BRUISER" | "ASSASSIN" | "TANK" | "SKIRMISHER",
                "stats": {"hp": 15, "attack": 12, "defense": 15, "agility": 8}  # Optional for custom
            }
        fighter_b_config: Dict with fighter B configuration (same format)
        options: Optional dict with game options
            {
                "max_rounds": 25,        # Default: 25
                "seed": 12345,           # Optional: for deterministic results
                "include_detailed_log": True  # Default: True
            }

    Returns:
        {
            "winner": "A" | "B" | "DRAW_MUTUAL_DEATH" | "DRAW_STAMINA" | "DRAW_TIMEOUT",
            "rounds": int,
            "fighter_a": {
                "role": str,
                "final_hp": float,
                "final_stamina": int
            },
            "fighter_b": {
                "role": str,
                "final_hp": float,
                "final_stamina": int
            },
            "log": [events...] | None,  # Detailed combat log (optional)
            "summary": {
                "total_damage_to_a": float,
                "total_damage_to_b": float,
                "fight_length": int
            }
        }
    """
    # Parse options
    if options is None:
        options = {}
    max_rounds = options.get("max_rounds", 25)
    seed = options.get("seed", None)
    include_log = options.get("include_detailed_log", True)

    # Create fighters
    fighter_a = _create_fighter(fighter_a_config)
    fighter_b = _create_fighter(fighter_b_config)

    # Create initial fight state
    initial_state = FightState(0, fighter_a, fighter_b)

    # Run simulation
    fight_result = engine_simulate_fight(initial_state, max_rounds, seed)

    # Calculate summary statistics from initial HP vs final HP
    initial_hp_a = fighter_a.hp
    initial_hp_b = fighter_b.hp
    final_hp_a = fight_result["final_state"].fighter_a.hp
    final_hp_b = fight_result["final_state"].fighter_b.hp

    total_dmg_to_a = max(0, initial_hp_a - final_hp_a)
    total_dmg_to_b = max(0, initial_hp_b - final_hp_b)

    # Build clean response with versioning
    from core.api import CORE_VERSION

    response = {
        "api_version": "1.0",
        "core_version": CORE_VERSION,
        "event_schema_version": "v1",
        "winner": fight_result["winner"],
        "rounds": fight_result["rounds"],
        "fighter_a": {
            "role": fighter_a.role,
            "final_hp": fight_result["final_state"].fighter_a.hp,
            "final_stamina": fight_result["final_state"].fighter_a.stamina
        },
        "fighter_b": {
            "role": fighter_b.role,
            "final_hp": fight_result["final_state"].fighter_b.hp,
            "final_stamina": fight_result["final_state"].fighter_b.stamina
        },
        "log": fight_result["log"] if include_log else None,
        "summary": {
            "total_damage_to_a": total_dmg_to_a,
            "total_damage_to_b": total_dmg_to_b,
            "fight_length": fight_result["rounds"]
        }
    }

    return response


def _create_fighter(config):
    """Create fighter from configuration"""
    # Validate config structure
    if not isinstance(config, dict):
        raise ValueError("Fighter config must be a dictionary")

    fighter_type = config.get("type", "balanced")
    role = config.get("role", "BRUISER")

    # Validate role
    valid_roles = ["BRUISER", "ASSASSIN", "TANK", "SKIRMISHER"]
    if role not in valid_roles:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {valid_roles}")

    if fighter_type == "balanced":
        return create_fighter_balanced(role)
    elif fighter_type == "random":
        return create_fighter_random(role)
    elif fighter_type == "custom" and "stats" in config:
        # Custom fighter creation with validation
        from state.fighter_factory import create_fighter
        stats = config["stats"]

        # Validate stats
        _validate_stats(stats)

        return create_fighter(
            hp_stat=stats.get("hp", 12),
            attack_stat=stats.get("attack", 12),
            defense_stat=stats.get("defense", 12),
            agility_stat=stats.get("agility", 12),
            role=role
        )
    else:
        # Default to balanced
        return create_fighter_balanced(role)


def _validate_stats(stats):
    """Validate fighter stats are in valid range"""
    required_stats = ["hp", "attack", "defense", "agility"]

    for stat_name in required_stats:
        if stat_name not in stats:
            raise ValueError(f"Missing required stat: {stat_name}")

        stat_value = stats[stat_name]
        if not isinstance(stat_value, int) or not (3 <= stat_value <= 18):
            raise ValueError(f"Invalid {stat_name}: {stat_value}. Must be integer between 3-18")


def run_quick_fight(role_a="BRUISER", role_b="ASSASSIN", seed=None):
    """
    Simplified API for quick testing

    Args:
        role_a: Fighter A role
        role_b: Fighter B role
        seed: Optional seed for deterministic results

    Returns:
        Simple result dict with winner and basic stats
    """
    fighter_a_config = {"type": "balanced", "role": role_a}
    fighter_b_config = {"type": "balanced", "role": role_b}
    options = {"seed": seed, "include_detailed_log": False}

    result = run_fight(fighter_a_config, fighter_b_config, options)

    return {
        "winner": result["winner"],
        "rounds": result["rounds"],
        "damage_dealt": {
            "a_to_b": result["summary"]["total_damage_to_b"],
            "b_to_a": result["summary"]["total_damage_to_a"]
        }
    }


# Convenience functions for common game scenarios
def run_tournament_fight(fighter_a_role, fighter_b_role, match_seed=None):
    """Tournament-style fight with deterministic seeding"""
    return run_quick_fight(fighter_a_role, fighter_b_role, match_seed)


def run_training_fight(player_role="BRUISER", opponent_role="random", difficulty="balanced"):
    """Training mode with various difficulty levels"""
    opponent_type = "random" if opponent_role == "random" else "balanced"

    fighter_a_config = {"type": "balanced", "role": player_role}
    fighter_b_config = {"type": opponent_type, "role": opponent_role if opponent_role != "random" else "BRUISER"}

    return run_fight(fighter_a_config, fighter_b_config)