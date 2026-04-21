# simulation/simulator.py - Legacy compatibility wrapper
# Bridges old telemetry API with new minimal game loop

from .game_engine import simulate_fight as engine_simulate_fight
from telemetry.telemetry import Telemetry
from core.api import get_initial_stamina


STAMINA_INIT = get_initial_stamina()

def simulate_fight(state, max_rounds=25, seed=None, action_mode="normal"):
    """
    Legacy compatibility wrapper for old telemetry API

    Args:
        state: FightState with two fighters
        max_rounds: Maximum number of rounds (default 25)
        seed: Random seed for deterministic results (default None)

    Returns:
        (final_state, telemetry) - legacy format
    """
    from core.api import get_config
    from copy import deepcopy

    # Use new clean game engine
    fight_result = engine_simulate_fight(state, max_rounds, seed, action_mode)

    # Convert back to legacy format
    final_state = fight_result["final_state"]

    # Build telemetry with proper stamina tracking
    telemetry = Telemetry()

    # Reconstruct stamina states for each round
    # Start with initial stamina
    stamina_a = STAMINA_INIT
    stamina_b = STAMINA_INIT

    # Record initial state (beginning of fight)
    initial_state = deepcopy(state)
    initial_state.fighter_a.stamina = stamina_a
    initial_state.fighter_b.stamina = stamina_b

    for event in fight_result["log"]:
        # Record stamina state AT START OF ROUND (before actions)
        round_state = deepcopy(initial_state)
        round_state.fighter_a.stamina = stamina_a
        round_state.fighter_b.stamina = stamina_b

        # Convert event for telemetry
        legacy_event = {
            "round": event["round"],
            "attacks": []
        }
        for attack in event["attacks"]:
            legacy_attack = {
                "attacker": attack["attacker"],
                "target": attack["defender"],  # defender → target
                "zone": attack["zone"],
                "damage": attack["damage"],
                "event": attack["event"]
            }

            # Add absorption information if available
            if "absorbed" in attack:
                legacy_attack["absorbed"] = attack["absorbed"]

            legacy_event["attacks"].append(legacy_attack)

        # Add skip events if available
        if "skip_events" in event:
            legacy_event["skip_events"] = event["skip_events"]

        # Record with proper round state
        telemetry.record(legacy_event, round_state)

        # Update stamina for next round (simulate costs + regen)
        # Simplified: assume 1 attack zone + 0-2 defense zones per fighter
        config = get_config()
        attack_cost = config["attack_stamina_cost_per_zone"]  # 1 mandatory zone
        defense_cost = 2 * config["defense_stamina_cost_per_zone"]  # Typical 2 zones
        regen = config["stamina_regen_per_round"]

        stamina_a = max(0, min(STAMINA_INIT, stamina_a - attack_cost - defense_cost + regen))
        stamina_b = max(0, min(STAMINA_INIT, stamina_b - attack_cost - defense_cost + regen))

    return final_state, telemetry