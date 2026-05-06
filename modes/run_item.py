# modes/run_item.py - Item effectiveness testing mode
"""
Item value assessment mode for testing item effectiveness through performance delta

This mode tests items by measuring winrate delta:
VALUE(item) = Performance(with item) - Performance(without item)

The test uses a UNIVERSAL build against a pool of opponents with
BALANCED_ROLE_DISTRIBUTION to get statistically significant results.
"""

import json
import random
from typing import Dict, List, Tuple
from state.fighter_factory import create_fighter
from simulation.level_benchmark import BALANCED_ROLE_DISTRIBUTION, generate_random_fighter_at_level
from items import get_item, Equipment, assemble_fighter_from_state
from game.run_fight import run_fight


def run_item(config_path: str):
    """
    Run item effectiveness testing

    Args:
        config_path: Path to JSON config file
    """
    # Load configuration
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # Extract configuration
    level = cfg.get("level", 5)
    item_id = cfg["item_id"]
    battles_per_opponent = cfg.get("battles_per_opponent", 500)
    seed = cfg.get("seed", 42)
    action_mode = cfg.get("action_mode", "normal")

    # Validate item exists
    try:
        test_item = get_item(item_id)
    except ValueError as e:
        print(f"❌ {e}")
        return

    # Print test configuration
    print_item_test_info(test_item, level, battles_per_opponent, seed)

    # Create test build (UNIVERSAL build with equal stats)
    test_build = create_universal_build(level)
    print_test_build_info(test_build, level)

    # Generate opponent pool based on BALANCED_ROLE_DISTRIBUTION
    opponent_pool = generate_opponent_pool(level)
    print_opponent_pool_info(opponent_pool)

    print(f"\n🥊 RUNNING ITEM EFFECTIVENESS TEST")
    print("=" * 60)

    # Test winrate WITHOUT item
    print("📊 Phase 1: Testing WITHOUT item...")
    winrate_without = test_against_opponents(
        test_build, None, opponent_pool, battles_per_opponent, seed, action_mode
    )

    # Test winrate WITH item
    print("📊 Phase 2: Testing WITH item...")
    winrate_with = test_against_opponents(
        test_build, test_item, opponent_pool, battles_per_opponent, seed + 100000, action_mode
    )

    # Calculate item value
    item_value = winrate_with - winrate_without

    # Print results
    print_item_effectiveness_results(
        test_item, winrate_without, winrate_with, item_value,
        len(opponent_pool), battles_per_opponent
    )


def create_universal_build(level: int):
    """Create UNIVERSAL build with equal stats for given level"""
    # Calculate stats for UNIVERSAL build
    base_stats = 3  # Minimum stats
    total_points = 12 + (level - 1) * 5  # Level-based stat budget
    remaining_points = total_points - (base_stats * 4)
    points_per_stat = remaining_points // 4
    extra_points = remaining_points % 4

    # Distribute stats as equally as possible
    stats = [base_stats + points_per_stat] * 4
    for i in range(extra_points):
        stats[i] += 1

    hp_stat, attack, defense, agility = stats

    return create_fighter(
        hp_stat=hp_stat,
        attack_stat=attack,
        defense_stat=defense,
        agility_stat=agility,
        role="UNIVERSAL_TEST"
    )


def generate_opponent_pool(level: int) -> List:
    """Generate opponent pool based on BALANCED_ROLE_DISTRIBUTION"""
    opponents = []

    # Create opponents for each role in distribution
    for role, percentage in BALANCED_ROLE_DISTRIBUTION.items():
        # Calculate number of opponents for this role (at least 1)
        count = max(1, int(percentage * 10))  # Scale to reasonable numbers

        for _ in range(count):
            opponent = generate_random_fighter_at_level(level, force_role=role)
            opponents.append((role, opponent))

    return opponents


def test_against_opponents(test_build, item, opponent_pool, battles_per_opponent, base_seed, action_mode) -> float:
    """Test build against opponent pool and return winrate"""

    total_wins = 0
    total_battles = 0

    # Test against each opponent type
    for i, (opponent_role, opponent) in enumerate(opponent_pool):
        wins_vs_opponent = 0

        # Progress tracking
        if len(opponent_pool) > 1:
            print(f"  Testing vs {opponent_role} ({i+1}/{len(opponent_pool)})...")

        for battle_num in range(battles_per_opponent):
            # Deterministic seeding
            battle_seed = base_seed + i * battles_per_opponent + battle_num
            random.seed(battle_seed)

            # Prepare fighter A (with/without item)
            if item:
                # Equip item to test build
                equipment = Equipment()
                equipment = equipment.equip_item(item)
                final_stats, final_modifiers = assemble_fighter_from_state(test_build, equipment)

                # Create fighter dict with modifiers
                fighter_a = {
                    "type": "custom",
                    "role": f"UNIVERSAL_WITH_{item.name.upper().replace(' ', '_')}",
                    "stats": {
                        "hp": test_build.hp_stat,
                        "attack": test_build.attack,
                        "defense": test_build.defense,
                        "agility": test_build.agility
                    },
                    "modifiers": final_modifiers
                }
            else:
                # No item - standard build
                fighter_a = {
                    "type": "custom",
                    "role": "UNIVERSAL_NO_ITEM",
                    "stats": {
                        "hp": test_build.hp_stat,
                        "attack": test_build.attack,
                        "defense": test_build.defense,
                        "agility": test_build.agility
                    }
                }

            # Fighter B (opponent)
            fighter_b = {
                "type": "custom",
                "role": opponent_role,
                "stats": {
                    "hp": opponent.hp_stat,
                    "attack": opponent.attack,
                    "defense": opponent.defense,
                    "agility": opponent.agility
                }
            }

            # Run fight
            options = {
                "seed": battle_seed,
                "include_detailed_log": False,
                "action_mode": action_mode
            }

            result = run_fight(fighter_a, fighter_b, options)

            # Track wins for fighter A
            if result["winner"] == "A":
                wins_vs_opponent += 1

        total_wins += wins_vs_opponent
        total_battles += battles_per_opponent

        # Show progress per opponent
        winrate_vs_opponent = (wins_vs_opponent / battles_per_opponent) * 100
        if len(opponent_pool) > 1:
            print(f"    Winrate vs {opponent_role}: {winrate_vs_opponent:.1f}% ({wins_vs_opponent}/{battles_per_opponent})")

    # Calculate overall winrate
    overall_winrate = (total_wins / total_battles) * 100
    return overall_winrate


def print_item_test_info(item, level, battles_per_opponent, seed):
    """Print item test configuration"""
    print(f"⚔️ ITEM EFFECTIVENESS TEST:")
    print("=" * 50)
    print(f"Testing Item: {item.name}")
    print(f"Item Slot: {item.slot.value}")
    print(f"Item Modifiers: {item.modifiers}")
    print(f"Test Level: {level}")
    print(f"Battles per opponent: {battles_per_opponent:,}")
    print(f"Base seed: {seed}")


def print_test_build_info(build, level):
    """Print test build information"""
    print(f"\n🛠️ TEST BUILD (UNIVERSAL Level {level}):")
    print(f"  HP={build.hp} | ATK={build.attack} | DEF={build.defense} | AGI={build.agility}")

    # Show stat total
    stat_total = build.hp_stat + build.attack + build.defense + build.agility
    expected_total = 12 + (level - 1) * 5
    print(f"  Stat Total: {stat_total} (expected: {expected_total})")


def print_opponent_pool_info(opponent_pool):
    """Print opponent pool information"""
    print(f"\n👥 OPPONENT POOL ({len(opponent_pool)} opponents):")

    # Count opponents by role
    role_counts = {}
    for role, _ in opponent_pool:
        role_counts[role] = role_counts.get(role, 0) + 1

    for role, count in sorted(role_counts.items()):
        percentage = (count / len(opponent_pool)) * 100
        print(f"  {role}: {count} opponents ({percentage:.1f}%)")


def print_item_effectiveness_results(item, winrate_without, winrate_with, item_value,
                                   opponent_count, battles_per_opponent):
    """Print comprehensive item effectiveness results"""

    total_battles = opponent_count * battles_per_opponent

    print(f"\n📈 ITEM EFFECTIVENESS RESULTS:")
    print("=" * 50)

    print(f"\n🏆 WINRATE COMPARISON:")
    print(f"  WITHOUT {item.name}: {winrate_without:.2f}%")
    print(f"  WITH {item.name}: {winrate_with:.2f}%")
    print(f"  DELTA (Item Value): {item_value:+.2f}%")

    print(f"\n📊 TEST STATISTICS:")
    print(f"  Total battles: {total_battles:,}")
    print(f"  Opponent types: {opponent_count}")
    print(f"  Battles per opponent: {battles_per_opponent:,}")

    print(f"\n🎯 ITEM ASSESSMENT:")
    if item_value > 5.0:
        print(f"  💪 VERY EFFECTIVE - Strong positive impact ({item_value:+.1f}%)")
    elif item_value > 2.0:
        print(f"  ✅ EFFECTIVE - Clear positive impact ({item_value:+.1f}%)")
    elif item_value > 0.5:
        print(f"  📈 SLIGHTLY EFFECTIVE - Minor positive impact ({item_value:+.1f}%)")
    elif item_value > -0.5:
        print(f"  ⚖️ NEUTRAL - Negligible impact ({item_value:+.1f}%)")
    elif item_value > -2.0:
        print(f"  📉 SLIGHTLY HARMFUL - Minor negative impact ({item_value:+.1f}%)")
    else:
        print(f"  ❌ HARMFUL - Clear negative impact ({item_value:+.1f}%)")

    # Statistical significance note
    if total_battles >= 5000:
        print(f"  📊 High statistical confidence ({total_battles:,} battles)")
    elif total_battles >= 1000:
        print(f"  📊 Good statistical confidence ({total_battles:,} battles)")
    else:
        print(f"  ⚠️ Limited statistical confidence ({total_battles:,} battles - recommend >1000)")

    print(f"\n💎 FINAL ITEM VALUE: {item_value:+.2f}% winrate delta")