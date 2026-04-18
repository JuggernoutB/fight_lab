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

    # Reset absorption resources before fight begins
    fight_state.fighter_a.damage_absorption_resource = 0.0
    fight_state.fighter_b.damage_absorption_resource = 0.0

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

    # Combat resolution with absorption resource integration
    res_a, updated_resource_a, updated_resource_b_from_a = process_attack(
        attacker={"attack": a.attack, "agility": a.agility},
        defender={"defense": b.defense, "agility": b.agility},
        attacker_stamina=a.stamina,
        defender_stamina=b.stamina,
        atk_zones=atk_zones_a,
        def_zones=def_zones_b,
        attacker_absorption_resource=a.damage_absorption_resource,
        defender_absorption_resource=b.damage_absorption_resource,
        attacker_fatigue_bonus=0.0
    )

    res_b, updated_resource_b, updated_resource_a_from_b = process_attack(
        attacker={"attack": b.attack, "agility": b.agility},
        defender={"defense": a.defense, "agility": a.agility},
        attacker_stamina=b.stamina,
        defender_stamina=a.stamina,
        atk_zones=atk_zones_b,
        def_zones=def_zones_a,
        attacker_absorption_resource=b.damage_absorption_resource,
        defender_absorption_resource=a.damage_absorption_resource,
        attacker_fatigue_bonus=0.0
    )

    # Update fighter absorption resources
    # A gets resource from defending against B's attacks
    a.damage_absorption_resource = updated_resource_a_from_b
    # B gets resource from defending against A's attacks
    b.damage_absorption_resource = updated_resource_b_from_a

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
                "fatigue_level": get_stamina_level(a.stamina),
                "absorption_resource": a.damage_absorption_resource
            },
            "B": {
                "hp": b.hp,
                "stamina": b.stamina,
                "fatigue_level": get_stamina_level(b.stamina),
                "absorption_resource": b.damage_absorption_resource
            }
        }
    }
    events.append(round_event)

    # ============================================================
    # DAMAGE ABSORPTION RESOURCE SYSTEM
    # ============================================================

    # Calculate absorbed damage for each fighter (BLOCK ONLY - exclude dodge)
    absorbed_by_a = 0.0  # A absorbed damage from B's attacks via blocking
    absorbed_by_b = 0.0  # B absorbed damage from A's attacks via blocking

    for zone, attack_data in res_b.items():  # B attacking A
        if "absorbed" in attack_data:
            absorbed_by_a += attack_data["absorbed"]["block"]  # Only block absorption

    for zone, attack_data in res_a.items():  # A attacking B
        if "absorbed" in attack_data:
            absorbed_by_b += attack_data["absorbed"]["block"]  # Only block absorption

    # Process absorption events and update resources
    absorption_events = []
    config = get_config()

    # Add absorbed damage to resources first
    if absorbed_by_a > 0:
        # A absorbed damage - add to A's resource
        opponent_max_hp = getattr(b, 'max_hp', b.hp)
        if hasattr(b, 'hp_stat'):
            from core.modules.ehp import EHPDamageCalculator
            calc = EHPDamageCalculator()
            opponent_max_hp = calc.calculate_base_hp(b.hp_stat)

        damage_to_resource = (absorbed_by_a / opponent_max_hp) * config["damage_absorption_koef"]
        a.damage_absorption_resource = min(1.0, a.damage_absorption_resource + damage_to_resource)

    if absorbed_by_b > 0:
        # B absorbed damage - add to B's resource
        opponent_max_hp = getattr(a, 'max_hp', a.hp)
        if hasattr(a, 'hp_stat'):
            from core.modules.ehp import EHPDamageCalculator
            calc = EHPDamageCalculator()
            opponent_max_hp = calc.calculate_base_hp(a.hp_stat)

        damage_to_resource = (absorbed_by_b / opponent_max_hp) * config["damage_absorption_koef"]
        b.damage_absorption_resource = min(1.0, b.damage_absorption_resource + damage_to_resource)

    # NEW ENHANCED STAMINA TRANSFER LOGIC
    threshold = config["absorption_event_threshold"]

    # Check who can trigger stamina transfer
    a_can_transfer = (a.damage_absorption_resource >= threshold and
                     get_stamina_level(a.stamina) != 2 and  # Not exhausted
                     get_stamina_level(b.stamina) != 0 and  # Opponent must be tired/exhausted (not fresh)
                     a.role != "BRUISER")  # BRUISER cannot use stamina transfer
    b_can_transfer = (b.damage_absorption_resource >= threshold and
                     get_stamina_level(b.stamina) != 2 and  # Not exhausted
                     get_stamina_level(a.stamina) != 0 and  # Opponent must be tired/exhausted (not fresh)
                     b.role != "BRUISER")  # BRUISER cannot use stamina transfer

    # Determine who gets the transfer
    transfer_winner = None
    if a_can_transfer and b_can_transfer:
        # Both can transfer - winner is who has higher DEFENSE
        transfer_winner = "A" if a.defense > b.defense else "B"
    elif a_can_transfer:
        transfer_winner = "A"
    elif b_can_transfer:
        transfer_winner = "B"

    # Execute stamina transfer - but only if winner has significant DEF advantage (3+ points)
    if transfer_winner:
        if transfer_winner == "A":
            def_advantage = a.defense - b.defense
        else:
            def_advantage = b.defense - a.defense

        # Only proceed if the winner has sufficient defense advantage
        min_def_advantage = config["min_defense_advantage"]
        if def_advantage < min_def_advantage:
            transfer_winner = None

    if transfer_winner:
        if transfer_winner == "A":
            absorber, opponent, absorber_id = a, b, "A"
        else:
            absorber, opponent, absorber_id = b, a, "B"

        stamina_transfer = config["stamina_transfer_amount"]
        current_opponent_stamina = opponent.stamina
        absorber_stamina_before = absorber.stamina

        # Transfer stamina
        opponent.stamina = max(0, opponent.stamina - stamina_transfer)
        absorber.stamina = min(100, absorber.stamina + stamina_transfer)

        # Create event
        stamina_event = {
            "type": "absorption_stamina_transfer",
            "fighter": absorber_id,
            "opponent": "A" if absorber_id == "B" else "B",
            "resource_used": absorber.damage_absorption_resource,
            "stamina_transferred": stamina_transfer,
            "opponent_stamina_before": current_opponent_stamina,
            "opponent_stamina_after": opponent.stamina,
            "absorber_stamina_before": absorber_stamina_before,
            "absorber_stamina_after": absorber.stamina,
            "win_reason": "both_ready_higher_defense_3plus" if (a_can_transfer and b_can_transfer) else "only_ready_3plus",
            "def_advantage": def_advantage
        }
        absorption_events.append(stamina_event)

    # Add absorption events to round events
    if absorption_events:
        round_event["absorption_events"] = absorption_events

    # Check if any absorption event was triggered and reset both fighters' resources
    absorption_triggered = False
    for event in absorption_events:
        if event.get("type") == "absorption_stamina_transfer":
            absorption_triggered = True
            break

    if absorption_triggered:
        # Reset both fighters' absorption resources after absorption event is used
        a.damage_absorption_resource = 0.0
        b.damage_absorption_resource = 0.0

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


