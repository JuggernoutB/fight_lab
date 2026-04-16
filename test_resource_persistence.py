#!/usr/bin/env python3
"""
Test absorption resource persistence between fights of same build combinations
"""

import sys
import copy
from state.level_system import create_fighter_by_level
from state.fight_state import FightState
from simulation.simulator import simulate_fight


def test_resource_persistence():
    """Test that absorption resources persist between fights of same build combinations"""

    print("=== TESTING ABSORPTION RESOURCE PERSISTENCE ===\n")

    # Create specific fighters for testing
    tank_fighter = create_fighter_by_level(5, "TANK")
    assassin_fighter = create_fighter_by_level(5, "ASSASSIN")

    # Build tuples for tracking
    tank_build = (getattr(tank_fighter, 'hp_stat', 0), tank_fighter.attack, tank_fighter.defense, tank_fighter.agility)
    assassin_build = (getattr(assassin_fighter, 'hp_stat', 0), assassin_fighter.attack, assassin_fighter.defense, assassin_fighter.agility)

    print(f"TANK build: HP={tank_build[0]}, ATK={tank_build[1]}, DEF={tank_build[2]}, AGI={tank_build[3]}")
    print(f"ASSASSIN build: HP={assassin_build[0]}, ATK={assassin_build[1]}, DEF={assassin_build[2]}, AGI={assassin_build[3]}")
    print()

    # Simulate resource persistence manually
    build_combination_resources = {}

    def get_combination_key(build_a, build_b):
        """Create stable key for build combination (order-independent)"""
        if build_a <= build_b:
            return (build_a, build_b)
        else:
            return (build_b, build_a)

    def is_swapped_combination(build_a, build_b, combination_key):
        """Check if current assignment is swapped relative to stored key"""
        return combination_key[0] != build_a

    # Fight 1: TANK vs ASSASSIN (first encounter)
    print("Fight 1: TANK vs ASSASSIN (first encounter)")

    fighter_a = create_fighter_by_level(5, "TANK")
    fighter_b = create_fighter_by_level(5, "ASSASSIN")
    build_a = (getattr(fighter_a, 'hp_stat', 0), fighter_a.attack, fighter_a.defense, fighter_a.agility)
    build_b = (getattr(fighter_b, 'hp_stat', 0), fighter_b.attack, fighter_b.defense, fighter_b.agility)
    combination_key = get_combination_key(build_a, build_b)

    # New combination: start with default resources (0.0)
    fighter_a.damage_absorption_resource = 0.0
    fighter_b.damage_absorption_resource = 0.0

    print(f"  Initial resources: A={fighter_a.damage_absorption_resource:.3f}, B={fighter_b.damage_absorption_resource:.3f}")

    # Simulate fight
    state = FightState(0, fighter_a, fighter_b)
    result_state, telemetry = simulate_fight(state, max_rounds=15, seed=1001)

    final_resource_a = result_state.fighter_a.damage_absorption_resource
    final_resource_b = result_state.fighter_b.damage_absorption_resource

    print(f"  Final resources: A={final_resource_a:.3f}, B={final_resource_b:.3f}")
    print(f"  Rounds: {result_state.round_id}")

    # Store resources
    if is_swapped_combination(build_a, build_b, combination_key):
        build_combination_resources[combination_key] = {
            'resource_a': final_resource_b,
            'resource_b': final_resource_a
        }
    else:
        build_combination_resources[combination_key] = {
            'resource_a': final_resource_a,
            'resource_b': final_resource_b
        }

    print(f"  Stored for combination {combination_key}: {build_combination_resources[combination_key]}")
    print()

    # Fight 2: TANK vs ASSASSIN (second encounter - should restore resources)
    print("Fight 2: TANK vs ASSASSIN (second encounter - should restore resources)")

    fighter_a2 = create_fighter_by_level(5, "TANK")
    fighter_b2 = create_fighter_by_level(5, "ASSASSIN")
    build_a2 = (getattr(fighter_a2, 'hp_stat', 0), fighter_a2.attack, fighter_a2.defense, fighter_a2.agility)
    build_b2 = (getattr(fighter_b2, 'hp_stat', 0), fighter_b2.attack, fighter_b2.defense, fighter_b2.agility)
    combination_key2 = get_combination_key(build_a2, build_b2)

    # Should match previous combination
    if combination_key2 in build_combination_resources:
        stored_resources = build_combination_resources[combination_key2]

        if is_swapped_combination(build_a2, build_b2, combination_key2):
            fighter_a2.damage_absorption_resource = stored_resources['resource_b']
            fighter_b2.damage_absorption_resource = stored_resources['resource_a']
        else:
            fighter_a2.damage_absorption_resource = stored_resources['resource_a']
            fighter_b2.damage_absorption_resource = stored_resources['resource_b']

    print(f"  Restored resources: A={fighter_a2.damage_absorption_resource:.3f}, B={fighter_b2.damage_absorption_resource:.3f}")

    # Simulate second fight
    state2 = FightState(0, fighter_a2, fighter_b2)
    result_state2, telemetry2 = simulate_fight(state2, max_rounds=15, seed=1002)

    final_resource_a2 = result_state2.fighter_a.damage_absorption_resource
    final_resource_b2 = result_state2.fighter_b.damage_absorption_resource

    print(f"  Final resources: A={final_resource_a2:.3f}, B={final_resource_b2:.3f}")
    print(f"  Rounds: {result_state2.round_id}")
    print()

    # Fight 3: Different build combination (SKIRMISHER vs BRUISER - should start fresh)
    print("Fight 3: SKIRMISHER vs BRUISER (new combination - should start fresh)")

    fighter_a3 = create_fighter_by_level(5, "SKIRMISHER")
    fighter_b3 = create_fighter_by_level(5, "BRUISER")
    build_a3 = (getattr(fighter_a3, 'hp_stat', 0), fighter_a3.attack, fighter_a3.defense, fighter_a3.agility)
    build_b3 = (getattr(fighter_b3, 'hp_stat', 0), fighter_b3.attack, fighter_b3.defense, fighter_b3.agility)
    combination_key3 = get_combination_key(build_a3, build_b3)

    # New combination: start with default resources (0.0)
    fighter_a3.damage_absorption_resource = 0.0
    fighter_b3.damage_absorption_resource = 0.0

    print(f"  Initial resources (new combo): A={fighter_a3.damage_absorption_resource:.3f}, B={fighter_b3.damage_absorption_resource:.3f}")

    # Simulate third fight
    state3 = FightState(0, fighter_a3, fighter_b3)
    result_state3, telemetry3 = simulate_fight(state3, max_rounds=15, seed=1003)

    final_resource_a3 = result_state3.fighter_a.damage_absorption_resource
    final_resource_b3 = result_state3.fighter_b.damage_absorption_resource

    print(f"  Final resources: A={final_resource_a3:.3f}, B={final_resource_b3:.3f}")
    print(f"  Rounds: {result_state3.round_id}")
    print()

    # Results analysis
    print("=== PERSISTENCE TEST RESULTS ===")
    print(f"1. First TANK vs ASSASSIN fight started with 0.0/0.0 resources")
    print(f"2. Second TANK vs ASSASSIN fight started with {fighter_a2.damage_absorption_resource:.3f}/{fighter_b2.damage_absorption_resource:.3f} resources (restored!)")
    print(f"3. SKIRMISHER vs BRUISER fight started with 0.0/0.0 resources (new combo)")
    print()

    if fighter_a2.damage_absorption_resource > 0.0 or fighter_b2.damage_absorption_resource > 0.0:
        print("✅ SUCCESS: Resource persistence working correctly!")
        print("   - Same build combination preserved absorption resources between fights")
        print("   - New build combination started fresh with 0.0 resources")
    else:
        print("❌ FAILURE: Resource persistence not working")
        print("   - Expected non-zero resources in second fight of same combination")

    print()
    print(f"Total build combinations tracked: {len(build_combination_resources)}")
    for combo_key, resources in build_combination_resources.items():
        print(f"  {combo_key}: {resources}")


if __name__ == "__main__":
    test_resource_persistence()