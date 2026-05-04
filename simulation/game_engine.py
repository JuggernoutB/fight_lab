# simulation/game_engine.py - Minimal Game Loop Engine
# Clean API for game integration

import random
import copy
from core.api import process_attack, apply_stamina, get_config, get_stamina_level
from state.meta_layer import update_meta
from ai.role_engine import choose_action

# Combat action validation constants
MIN_ATTACK_ZONES = 1
MAX_ATTACK_ZONES = 2
MIN_DEFENSE_ZONES = 0
MAX_DEFENSE_ZONES = 2
DEFAULT_ATTACK_ZONE = "chest"


def simulate_fight(state, max_rounds=25, seed=None, action_mode="normal"):
    """
    Clean game engine API - returns pure game data

    Args:
        state: FightState with two fighters
        max_rounds: Maximum number of rounds
        seed: Random seed for deterministic results

    Returns:
        {
            "winner": "A" | "B" | "DRAW_MUTUAL_DEATH" | "DRAW_STAMINA" | "DRAW_TIMEOUT",
            "rounds": int,
            "log": [events...],
            "final_state": FightState
        }
    """
    # Setup deterministic RNG
    rng = random.Random(seed)
    if seed is not None:
        random.seed(seed)

    # Copy state to avoid mutation
    fight_state = copy.deepcopy(state)
    fight_state.round_id = 0
    fight_state.end_reason = None

    a = fight_state.fighter_a
    b = fight_state.fighter_b

    # Game log for replay/UI
    log = []

    # Main game loop
    for round_num in range(1, max_rounds + 1):
        fight_state.round_id = round_num

        # Process round
        round_events = process_round(fight_state, rng, action_mode)
        log.extend(round_events)

        # Check end conditions
        if is_fight_finished(fight_state):
            break

    # Set timeout if no winner
    if fight_state.end_reason is None:
        fight_state.end_reason = "max_rounds"

    return {
        "winner": determine_winner(fight_state),
        "rounds": fight_state.round_id,
        "log": log,
        "final_state": fight_state
    }


def process_round(state, rng, action_mode="normal"):
    """Process a single round and return events"""
    events = []

    a = state.fighter_a
    b = state.fighter_b

    # Capture fighter states BEFORE combat for accurate display
    fighters_pre_round = {
        "A": {
            "hp": a.hp,
            "stamina": a.stamina,
            "fatigue_level": get_stamina_level(a.stamina)
        },
        "B": {
            "hp": b.hp,
            "stamina": b.stamina,
            "fatigue_level": get_stamina_level(b.stamina)
        }
    }

    # AI decisions
    action_a = choose_action(a, state, action_mode)
    action_b = choose_action(b, state, action_mode)

    # Convert to zones and validate
    atk_zones_a, def_zones_a = to_zones(action_a)
    atk_zones_b, def_zones_b = to_zones(action_b)

    # Combat resolution
    res_a, action_costs_a, skip_events_a = process_attack(
        attacker={"attack": a.attack, "agility": a.agility},
        defender={"defense": b.defense, "agility": b.agility},
        attacker_stamina=a.stamina,
        defender_stamina=b.stamina,
        atk_zones=atk_zones_a,
        def_zones=def_zones_b,
        attacker_fatigue_bonus=0.0
    )

    res_b, action_costs_b, skip_events_b = process_attack(
        attacker={"attack": b.attack, "agility": b.agility},
        defender={"defense": a.defense, "agility": a.agility},
        attacker_stamina=b.stamina,
        defender_stamina=a.stamina,
        atk_zones=atk_zones_b,
        def_zones=def_zones_a,
        attacker_fatigue_bonus=0.0
    )

    # Build event log for this round
    round_attacks = []

    # A's attacks
    for zone, attack_data in res_a.items():
        attack_event = {
            "attacker": "A",
            "defender": "B",
            "zone": zone,
            "damage": attack_data["damage"],
            "event": attack_data["event"]
        }
        # Add absorption data if available
        if "absorbed" in attack_data:
            attack_event["absorbed"] = attack_data["absorbed"]

        round_attacks.append(attack_event)

    # B's attacks
    for zone, attack_data in res_b.items():
        attack_event = {
            "attacker": "B",
            "defender": "A",
            "zone": zone,
            "damage": attack_data["damage"],
            "event": attack_data["event"]
        }
        # Add absorption data if available
        if "absorbed" in attack_data:
            attack_event["absorbed"] = attack_data["absorbed"]

        round_attacks.append(attack_event)

    # Add round event with fighter states (captured before combat)
    round_event = {
        "round": state.round_id,
        "attacks": round_attacks,
        "fighters_pre_round": fighters_pre_round
    }

    # Skip events removed (legacy compatibility maintained)
    # skip_events_a and skip_events_b are now empty lists

    events.append(round_event)

    # ============================================================
    # APPLY DAMAGE
    # ============================================================

    # Apply damage
    dmg_to_a = sum(attack_data["damage"] for attack_data in res_b.values())
    dmg_to_b = sum(attack_data["damage"] for attack_data in res_a.values())

    a.hp -= dmg_to_a
    b.hp -= dmg_to_b
    a.last_damage_taken = dmg_to_a
    b.last_damage_taken = dmg_to_b

    # Update meta state
    update_meta(state, events)

    # Apply stamina changes for actions first
    a.stamina = apply_stamina(a.stamina, action_a)
    b.stamina = apply_stamina(b.stamina, action_b)

    # Get config for stamina costs
    config = get_config()

    # Apply stamina costs for successful combat mechanics

    # Fighter A action costs
    stamina_cost_a = (action_costs_a["dodge"] * config["stamina_cost_dodge"] +
                     action_costs_a["crit"] * config["stamina_cost_crit"] +
                     action_costs_a["block_break"] * config["stamina_cost_block_break"])

    # Fighter B action costs
    stamina_cost_b = (action_costs_b["dodge"] * config["stamina_cost_dodge"] +
                     action_costs_b["crit"] * config["stamina_cost_crit"] +
                     action_costs_b["block_break"] * config["stamina_cost_block_break"])

    # Apply costs (cannot go below 0)
    a.stamina = max(0, a.stamina - stamina_cost_a)
    b.stamina = max(0, b.stamina - stamina_cost_b)

    return events


def to_zones(action):
    """Convert action to attack/defense zones with validation"""
    if "attack_zones" in action:
        atk = action["attack_zones"]
        df = action.get("defense_zones", [])
    else:
        atk = ["chest"] * action.get("attack", 0)
        df = ["chest"] * action.get("defense", 0)

    # MANDATORY: Must attack MIN_ATTACK_ZONES-MAX_ATTACK_ZONES zones
    if len(atk) < MIN_ATTACK_ZONES:
        atk = [DEFAULT_ATTACK_ZONE] * MIN_ATTACK_ZONES
    elif len(atk) > MAX_ATTACK_ZONES:
        atk = atk[:MAX_ATTACK_ZONES]

    # OPTIONAL: Can defend MIN_DEFENSE_ZONES-MAX_DEFENSE_ZONES zones
    if len(df) > MAX_DEFENSE_ZONES:
        df = df[:MAX_DEFENSE_ZONES]

    return atk, df


def is_fight_finished(state):
    """Check if fight should end"""
    a = state.fighter_a
    b = state.fighter_b

    # Death condition
    if a.hp <= 0 or b.hp <= 0:
        state.end_reason = "death"
        return True

    # Mutual stamina exhaustion
    config = get_config()
    min_attack_cost = MIN_ATTACK_ZONES * config["attack_stamina_cost_per_zone"]
    a_cant_attack = a.stamina < min_attack_cost
    b_cant_attack = b.stamina < min_attack_cost

    if a_cant_attack and b_cant_attack:
        state.end_reason = "stamina_exhaustion"
        return True

    return False


def determine_winner(state):
    """Determine fight winner based on final state"""
    a = state.fighter_a
    b = state.fighter_b

    if a.hp <= 0 and b.hp <= 0:
        return "DRAW_MUTUAL_DEATH"
    if b.hp <= 0:
        return "A"
    if a.hp <= 0:
        return "B"

    # Other types of draws
    if state.end_reason == "stamina_exhaustion":
        return "DRAW_STAMINA"
    elif state.end_reason == "max_rounds":
        return "DRAW_TIMEOUT"
    else:
        return "DRAW_OTHER"


