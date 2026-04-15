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


def simulate_fight(state, max_rounds=25, seed=None):
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

    # Game log for replay/UI
    log = []

    # Main game loop
    for round_num in range(1, max_rounds + 1):
        fight_state.round_id = round_num

        # Process round
        round_events = process_round(fight_state, rng)
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


def process_round(state, rng):
    """Process a single round and return events"""
    events = []

    a = state.fighter_a
    b = state.fighter_b

    # AI decisions
    action_a = choose_action(a, state)
    action_b = choose_action(b, state)

    # Convert to zones and validate
    atk_zones_a, def_zones_a = to_zones(action_a)
    atk_zones_b, def_zones_b = to_zones(action_b)

    # Combat resolution
    res_a = process_attack(
        attacker={"attack": a.attack, "agility": a.agility},
        defender={"defense": b.defense, "agility": b.agility},
        attacker_stamina=a.stamina,
        defender_stamina=b.stamina,
        atk_zones=atk_zones_a,
        def_zones=def_zones_b
    )

    res_b = process_attack(
        attacker={"attack": b.attack, "agility": b.agility},
        defender={"defense": a.defense, "agility": a.agility},
        attacker_stamina=b.stamina,
        defender_stamina=a.stamina,
        atk_zones=atk_zones_b,
        def_zones=def_zones_a
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

    # Add round event with fighter states
    round_event = {
        "round": state.round_id,
        "attacks": round_attacks,
        "fighters_pre_round": {
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
    }
    events.append(round_event)

    # ============================================================
    # DAMAGE ABSORPTION RESOURCE SYSTEM
    # ============================================================

    # Calculate absorbed damage for each fighter
    absorbed_by_a = 0.0  # A absorbed damage from B's attacks
    absorbed_by_b = 0.0  # B absorbed damage from A's attacks

    for zone, attack_data in res_b.items():  # B attacking A
        if "absorbed" in attack_data:
            absorbed_by_a += attack_data["absorbed"]["dodge"] + attack_data["absorbed"]["block"]

    for zone, attack_data in res_a.items():  # A attacking B
        if "absorbed" in attack_data:
            absorbed_by_b += attack_data["absorbed"]["dodge"] + attack_data["absorbed"]["block"]

    # Process absorption events and update resources
    absorption_events = []
    config = get_config()

    # Process A's absorption
    if absorbed_by_a > 0:
        absorption_events.extend(_process_absorption_resource(
            a, b, absorbed_by_a, "A", config, rng
        ))

    # Process B's absorption
    if absorbed_by_b > 0:
        absorption_events.extend(_process_absorption_resource(
            b, a, absorbed_by_b, "B", config, rng
        ))

    # Add absorption events to round events
    if absorption_events:
        round_event["absorption_events"] = absorption_events

    # Apply resource decay to both fighters
    a.damage_absorption_resource *= config["absorption_resource_decay"]
    b.damage_absorption_resource *= config["absorption_resource_decay"]

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

    # Apply stamina changes
    a.stamina = apply_stamina(a.stamina, action_a)
    b.stamina = apply_stamina(b.stamina, action_b)

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


def _process_absorption_resource(absorber, opponent, absorbed_damage, absorber_id, config, rng):
    """
    Process damage absorption resource logic for one fighter

    Args:
        absorber: Fighter who absorbed damage
        opponent: Fighter who dealt damage
        absorbed_damage: Amount of damage absorbed
        absorber_id: "A" or "B"
        config: Game configuration
        rng: Random generator

    Returns:
        List of absorption events that occurred
    """
    events = []

    # Convert absorbed damage to resource
    opponent_max_hp = getattr(opponent, 'max_hp', opponent.hp)  # Use max_hp if available
    if hasattr(opponent, 'hp_stat'):
        # Calculate max HP from EHP system
        from core.modules.ehp import EHPDamageCalculator
        calc = EHPDamageCalculator()
        opponent_max_hp = calc.calculate_base_hp(opponent.hp_stat)

    damage_to_resource = (absorbed_damage / opponent_max_hp) * config["damage_absorption_koef"]

    # Add to current resource (capped at 1.0)
    old_resource = absorber.damage_absorption_resource
    absorber.damage_absorption_resource = min(1.0, old_resource + damage_to_resource)

    # Check for absorption event (BEFORE decay as specified)
    if absorber.damage_absorption_resource >= config["absorption_event_threshold"]:
        # Event probability = resource value
        event_probability = absorber.damage_absorption_resource

        if rng.random() < event_probability:
            # Absorption event triggered!
            event = {
                "type": "absorption_event",
                "fighter": absorber_id,
                "resource_before": old_resource,
                "resource_after": absorber.damage_absorption_resource,
                "absorbed_damage": absorbed_damage,
                "probability": event_probability
            }
            events.append(event)

            # Reset resource to 0 after successful event
            absorber.damage_absorption_resource = 0.0

    return events