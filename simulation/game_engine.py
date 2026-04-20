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
    res_a, updated_resource_a, updated_resource_b_from_a, action_costs_a, skip_events_a = process_attack(
        attacker={"attack": a.attack, "agility": a.agility},
        defender={"defense": b.defense, "agility": b.agility},
        attacker_stamina=a.stamina,
        defender_stamina=b.stamina,
        atk_zones=atk_zones_a,
        def_zones=def_zones_b,
        attacker_absorption_resource=a.damage_absorption_resource,
        defender_absorption_resource=b.damage_absorption_resource,
        attacker_fatigue_bonus=0.0,
        opponent_defense=a.defense  # Defender's opponent (attacker) defense for skip protection comparison
    )

    res_b, updated_resource_b, updated_resource_a_from_b, action_costs_b, skip_events_b = process_attack(
        attacker={"attack": b.attack, "agility": b.agility},
        defender={"defense": a.defense, "agility": a.agility},
        attacker_stamina=b.stamina,
        defender_stamina=a.stamina,
        atk_zones=atk_zones_b,
        def_zones=def_zones_a,
        attacker_absorption_resource=b.damage_absorption_resource,
        defender_absorption_resource=a.damage_absorption_resource,
        attacker_fatigue_bonus=0.0,
        opponent_defense=b.defense  # Defender's opponent (attacker) defense for skip protection comparison
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

    # Add skip events if any occurred
    all_skip_events = []
    if skip_events_a:
        for event_type, occurred in skip_events_a.items():
            if occurred:
                all_skip_events.append({
                    "type": "skip_protection",
                    "defender": "B",  # B defended against A's attack
                    "attacker": "A",
                    "blocked_mechanic": event_type.replace("_skip", "")
                })

    if skip_events_b:
        for event_type, occurred in skip_events_b.items():
            if occurred:
                all_skip_events.append({
                    "type": "skip_protection",
                    "defender": "A",  # A defended against B's attack
                    "attacker": "B",
                    "blocked_mechanic": event_type.replace("_skip", "")
                })

    if all_skip_events:
        round_event["skip_events"] = all_skip_events

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

        # EHP INTEGRATION: Apply absorption efficiency based on A's defense
        from core.modules.ehp import calculate_absorption_efficiency
        absorption_efficiency = calculate_absorption_efficiency(a.defense)
        effective_absorbed = absorbed_by_a * absorption_efficiency

        damage_to_resource = (effective_absorbed / opponent_max_hp) * config["damage_absorption_koef"]
        a.damage_absorption_resource = min(1.0, a.damage_absorption_resource + damage_to_resource)

    if absorbed_by_b > 0:
        # B absorbed damage - add to B's resource
        opponent_max_hp = getattr(a, 'max_hp', a.hp)
        if hasattr(a, 'hp_stat'):
            from core.modules.ehp import EHPDamageCalculator
            calc = EHPDamageCalculator()
            opponent_max_hp = calc.calculate_base_hp(a.hp_stat)

        # EHP INTEGRATION: Apply absorption efficiency based on B's defense
        from core.modules.ehp import calculate_absorption_efficiency
        absorption_efficiency = calculate_absorption_efficiency(b.defense)
        effective_absorbed = absorbed_by_b * absorption_efficiency

        damage_to_resource = (effective_absorbed / opponent_max_hp) * config["damage_absorption_koef"]
        b.damage_absorption_resource = min(1.0, b.damage_absorption_resource + damage_to_resource)

    # NEW SKIP PROTECTION LOGIC - Skip events already handled in combat.py
    # Resource consumption for skip protection already handled there
    # Just need to apply resource decay

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

    # Apply stamina changes for actions first
    a.stamina = apply_stamina(a.stamina, action_a)
    b.stamina = apply_stamina(b.stamina, action_b)

    # Apply stamina costs for successful combat mechanics
    config = get_config()

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


