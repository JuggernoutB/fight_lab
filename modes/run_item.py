# modes/run_item.py - Item effectiveness testing mode using build orchestration
"""
Item effectiveness testing mode using build mode orchestration
Tests items through winrate comparison using the formula:
VALUE(item) = Performance(with item) - Performance(without item)
"""

import json
import os
import subprocess
import re
from datetime import datetime
from simulation.level_benchmark import generate_random_fighter_at_level, generate_level_matched_fighters
from state.fighter_factory import create_fighter
from items import get_item

def run_item(config_path):
    """
    Test item effectiveness by orchestrating build mode comparisons

    Args:
        config_path: Path to item testing configuration JSON
    """
    # Load configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    item_id = config.get('item_id', 'wooden_sword')
    battles_per_opponent = config.get('battles_per_opponent', 50)
    action_mode = config.get('action_mode', 'normal')

    # Get the item being tested
    try:
        item = get_item(item_id)
        item_level = item.level
        print(f"🗡️ ITEM EFFECTIVENESS TEST")
        print(f"=" * 60)
        print(f"📦 Item: {item.name}")
        print(f"🎚️ Item Level: {item_level}")
        print(f"⚔️ Battles per opponent: {battles_per_opponent:,}")
        print(f"🎲 Action mode: {action_mode}")
        print()
        print(f"✅ Item loaded: {item.name}")
        print(f"   Slot: {item.slot.value}")
        print(f"   Level: {item_level}")
        print(f"   Modifiers: {item.modifiers}")
    except ValueError as e:
        print(f"❌ Error loading item '{item_id}': {e}")
        return

    print()
    print(f"🎯 TESTING METHODOLOGY")
    print(f"=" * 60)
    print(f"• Test fighters: UNIVERSAL builds at level {item_level}")
    print(f"• Opponent pool: 100 random builds at level {item_level}")
    print(f"• Battles: {battles_per_opponent} per opponent")
    print(f"• Method: Build mode orchestration")
    print(f"• Metric: Winrate delta (with item - without item)")
    print()

    # Test only at item level
    levels_to_test = [item_level]
    level_results = []

    total_planned_battles = len(levels_to_test) * 100 * battles_per_opponent * 2
    print(f"Total battles planned: {total_planned_battles:,} ({len(levels_to_test)} levels × 100 opponents × {battles_per_opponent} battles × 2 tests)")
    print()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = "temp_item_configs"
    os.makedirs(temp_dir, exist_ok=True)
    temp_files_to_cleanup = []

    try:
        for level_idx, level in enumerate(levels_to_test):
            print(f"🎯 TESTING LEVEL {level} ({level_idx + 1}/{len(levels_to_test)})")
            print(f"=" * 40)

            # Create UNIVERSAL test build for this level
            test_build = create_universal_build_at_level(level)
            print(f"📋 Test Build (UNIVERSAL level {level}): HP:{test_build.hp_stat}, ATK:{test_build.attack}, DEF:{test_build.defense}, AGI:{test_build.agility}")

            # Create opponent pool for this level
            opponent_pool = []
            for i in range(100):
                opponent = generate_random_fighter_at_level(level)
                opponent_pool.append(opponent)

            # Test this level
            level_wins_without = 0
            level_wins_with = 0
            level_total_battles = 0

            for i, opponent in enumerate(opponent_pool):
                # Create temp configs for this opponent
                config_without = f"{temp_dir}/level_{level}_opponent_{i}_without_{timestamp}.json"
                config_with = f"{temp_dir}/level_{level}_opponent_{i}_with_{timestamp}.json"
                temp_files_to_cleanup.extend([config_without, config_with])

                # Generate configs for this opponent
                create_build_config(config_without, test_build, opponent, battles_per_opponent, item=None, item_id=item_id)
                create_build_config(config_with, test_build, opponent, battles_per_opponent, item=item, item_id=item_id)

                # Test without item
                winrate_without = run_build_test(config_without)
                wins_without = int((winrate_without / 100.0) * battles_per_opponent)

                # Test with item
                winrate_with = run_build_test(config_with)
                wins_with = int((winrate_with / 100.0) * battles_per_opponent)

                # Accumulate results for this level
                level_wins_without += wins_without
                level_wins_with += wins_with
                level_total_battles += battles_per_opponent

                # Show progress every 20 opponents
                if (i + 1) % 20 == 0 or i == len(opponent_pool) - 1:
                    current_avg_without = (level_wins_without / level_total_battles) * 100
                    current_avg_with = (level_wins_with / level_total_battles) * 100
                    current_delta = current_avg_with - current_avg_without
                    print(f"   Progress: {i+1}/100 | {current_avg_without:.1f}% → {current_avg_with:.1f}% (Δ{current_delta:+.1f}%)")

            # Calculate final averages for this level
            level_winrate_without = (level_wins_without / level_total_battles) * 100
            level_winrate_with = (level_wins_with / level_total_battles) * 100
            level_delta = level_winrate_with - level_winrate_without

            # Store results for this level
            level_results.append({
                'level': level,
                'winrate_without': level_winrate_without,
                'winrate_with': level_winrate_with,
                'delta': level_delta,
                'battles': level_total_battles
            })

            print(f"✅ Level {level} complete: {level_winrate_without:.1f}% → {level_winrate_with:.1f}% (Δ{level_delta:+.1f}%)")
            print()

        # Print comprehensive results
        if len(level_results) == 1:
            # Single level result
            result = level_results[0]
            print_item_test_results(item, result['winrate_without'], result['winrate_with'],
                                   result['delta'], result['battles'], opponent_count=100)
        else:
            # Multi-level results (shouldn't happen now, but kept for compatibility)
            print_multi_level_results(item, level_results, battles_per_opponent)

    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files_to_cleanup)

def create_universal_build_at_level(level):
    """Create a UNIVERSAL build at specified level with equal stats"""
    # Calculate total stat points for level
    total_stats = 12 + (level - 1) * 5

    # Distribute equally across 4 stats
    base_stat = total_stats // 4
    remainder = total_stats % 4

    # Create build with equal stats (add remainder to HP)
    hp_stat = base_stat + remainder
    attack_stat = base_stat
    defense_stat = base_stat
    agility_stat = base_stat

    # Create the fighter
    fighter = create_fighter(
        hp_stat=hp_stat,
        attack_stat=attack_stat,
        defense_stat=defense_stat,
        agility_stat=agility_stat,
        role='UNIVERSAL'
    )

    # Store original stat for reference
    fighter.hp_stat = hp_stat

    return fighter

def create_build_config(config_path, test_build, opponent, battles, item=None, item_id=None):
    """Create a build configuration file"""

    # Create test fighter config
    test_fighter_config = {
        "type": "custom",
        "role": "UNIVERSAL",
        "stats": {
            "hp": test_build.hp_stat,
            "attack": test_build.attack,
            "defense": test_build.defense,
            "agility": test_build.agility
        },
        "equipment": {
            "helm": None,
            "cuirass": None,
            "midplate": None,
            "waistguard": None,
            "greaves": None,
            "main_hand": None,
            "off_hand": None
        }
    }

    # Add item if provided
    if item:
        # Use the item_id from the outer scope
        test_fighter_config["equipment"][item.slot.value] = item_id

    # Create opponent config (no equipment)
    opponent_config = {
        "type": "custom",
        "role": opponent.role,
        "stats": {
            "hp": getattr(opponent, 'hp_stat', opponent.hp // 10),
            "attack": opponent.attack,
            "defense": opponent.defense,
            "agility": opponent.agility
        },
        "equipment": {
            "helm": None,
            "cuirass": None,
            "midplate": None,
            "waistguard": None,
            "greaves": None,
            "main_hand": None,
            "off_hand": None
        }
    }

    # Create full config
    build_config = {
        "iterations": battles,
        "fighter_a": test_fighter_config,
        "fighter_b": opponent_config
    }

    # Write config file
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(build_config, f, indent=2, ensure_ascii=False)

def run_build_test(config_path):
    """Run build test and extract winrate for fighter A"""
    try:
        # Run build mode
        result = subprocess.run([
            'python3', 'main.py', 'build', config_path
        ], capture_output=True, text=True, cwd='.')

        if result.returncode != 0:
            print(f"❌ Build test failed: {result.stderr}")
            return 0.0

        # Parse winrate from output
        output = result.stdout

        # Look for "Fighter A wins: X (Y%)" pattern
        winrate_pattern = r'Fighter A wins: [\d,]+ \((\d+\.?\d*)%\)'
        match = re.search(winrate_pattern, output)

        if match:
            winrate = float(match.group(1))
            return winrate
        else:
            print(f"❌ Could not parse winrate from build output")
            print(f"Output excerpt: {output[-500:]}")
            return 0.0

    except Exception as e:
        print(f"❌ Error running build test: {e}")
        return 0.0

def cleanup_temp_files(file_paths):
    """Clean up temporary config files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove {file_path}: {e}")

def print_item_test_results(item, winrate_without, winrate_with, delta, total_battles, opponent_count=1):
    """Print comprehensive item test results"""
    print()
    print(f"📈 ITEM EFFECTIVENESS RESULTS")
    print(f"=" * 60)
    print(f"🗡️ Item: {item.name}")
    print(f"📦 Modifiers: {item.modifiers}")
    print(f"⚔️ Total battles: {total_battles:,}")
    print(f"👥 Opponents tested: {opponent_count}")
    if opponent_count > 1:
        battles_per_opponent = total_battles // opponent_count
        print(f"🥊 Battles per opponent: {battles_per_opponent:,}")
    print()

    print(f"📊 PERFORMANCE COMPARISON")
    print(f"{'-' * 40}")
    print(f"Without item: {winrate_without:.1f}% winrate")
    print(f"With {item.name}: {winrate_with:.1f}% winrate")
    print(f"Item VALUE: {delta:+.1f}% winrate delta")
    print()

    # Statistical confidence assessment
    if total_battles >= 50000:
        statistical_confidence = "EXCELLENT"
        confidence_icon = "🎯"
    elif total_battles >= 25000:
        statistical_confidence = "VERY HIGH"
        confidence_icon = "💎"
    elif total_battles >= 10000:
        statistical_confidence = "HIGH"
        confidence_icon = "✅"
    elif total_battles >= 5000:
        statistical_confidence = "GOOD"
        confidence_icon = "👍"
    elif total_battles >= 1000:
        statistical_confidence = "MODERATE"
        confidence_icon = "⚖️"
    else:
        statistical_confidence = "LOW"
        confidence_icon = "⚠️"

    # Effectiveness assessment
    if abs(delta) < 0.5:
        assessment = "NEGLIGIBLE EFFECT"
        icon = "😐"
    elif abs(delta) < 1.5:
        assessment = "MINIMAL EFFECT"
        icon = "🔹" if delta > 0 else "🔸"
    elif abs(delta) < 3.0:
        assessment = "SLIGHT EFFECT"
        icon = "📈" if delta > 0 else "📉"
    elif abs(delta) < 7.0:
        assessment = "MODERATE EFFECT"
        icon = "⚡" if delta > 0 else "⚠️"
    elif abs(delta) < 15.0:
        assessment = "STRONG EFFECT"
        icon = "💪" if delta > 0 else "💥"
    else:
        assessment = "EXTREME EFFECT"
        icon = "🚀" if delta > 0 else "💀"

    print(f"🎯 ASSESSMENT: {icon} {assessment}")
    print(f"📊 Statistical confidence: {confidence_icon} {statistical_confidence}")
    print(f"   Based on {total_battles:,} battles across {opponent_count} opponents")
    print()

    # Enhanced recommendations
    if abs(delta) > 10.0:
        print(f"💡 RECOMMENDATION: {icon} This item has {assessment.lower()}")
        if delta > 0:
            print(f"   🌟 HIGHLY RECOMMENDED - Major competitive advantage")
            print(f"   ✅ Strong positive impact (+{delta:.1f}%) - priority item for builds")
        else:
            print(f"   🚫 STRONGLY AVOID - Major competitive disadvantage")
            print(f"   ❌ Strong negative impact ({delta:+.1f}%) - never use this item")
    elif abs(delta) > 5.0:
        print(f"💡 RECOMMENDATION: {icon} This item shows {assessment.lower()}")
        if delta > 0:
            print(f"   ✅ RECOMMENDED - Clear positive impact (+{delta:.1f}%)")
            print(f"   🎯 Consider using in competitive builds")
        else:
            print(f"   ❌ AVOID - Clear negative impact ({delta:+.1f}%)")
            print(f"   ⚠️ Better alternatives likely exist")
    elif abs(delta) > 2.0:
        print(f"💡 RECOMMENDATION: {icon} This item has {assessment.lower()}")
        if delta > 0:
            print(f"   📈 SITUATIONAL - Minor positive impact (+{delta:.1f}%)")
            print(f"   ⚖️ May be worth using if no better options available")
        else:
            print(f"   📉 QUESTIONABLE - Minor negative impact ({delta:+.1f}%)")
            print(f"   🤔 Consider other options first")
    else:
        print(f"💡 RECOMMENDATION: {icon} This item has {assessment.lower()}")
        print(f"   ⚖️ NEUTRAL - Impact is minimal ({delta:+.1f}%)")
        print(f"   🎭 Choose based on other factors (cost, availability, aesthetics)")

    # Multi-opponent specific insights
    if opponent_count >= 50:
        print(f"\n🏆 ROBUSTNESS: Tested against {opponent_count} diverse opponents")
        print(f"   📊 Results are highly generalizable to real gameplay scenarios")
        if abs(delta) > 3.0:
            print(f"   💪 Consistent performance advantage across diverse matchups")
        elif abs(delta) > 1.0:
            print(f"   ✅ Stable minor advantage across most matchups")
        else:
            print(f"   ⚖️ No significant advantage in most matchups")

    print(f"\n💎 FINAL ITEM VALUE: {delta:+.2f}% winrate delta")
    if opponent_count > 1:
        print(f"🏅 CONFIDENCE RATING: {confidence_icon} {statistical_confidence} ({total_battles:,} battles vs {opponent_count} opponents)")

def print_multi_level_results(item, level_results, battles_per_opponent):
    """Print comprehensive multi-level item test results"""
    print()
    print(f"📊 MULTI-LEVEL ITEM EFFECTIVENESS ANALYSIS")
    print(f"=" * 80)
    print(f"🗡️ Item: {item.name}")
    print(f"📦 Modifiers: {item.modifiers}")
    print(f"🥊 Battles per level: {len(level_results) * 100 * battles_per_opponent:,} ({100 * battles_per_opponent:,} per level)")
    print()

    # Print table header
    print(f"📋 LEVEL-BY-LEVEL ANALYSIS")
    print(f"{'-' * 80}")
    print(f"{'Level':<6} {'Without Item':<12} {'With Item':<12} {'Delta':<10} {'Assessment':<15} {'Battles':<8}")
    print(f"{'-' * 80}")

    # Print results for each level
    total_battles_all = 0
    weighted_delta_sum = 0

    for result in level_results:
        level = result['level']
        without = result['winrate_without']
        with_item = result['winrate_with']
        delta = result['delta']
        battles = result['battles']

        # Assess effectiveness
        if abs(delta) < 0.5:
            assessment = "NEGLIGIBLE"
        elif abs(delta) < 1.5:
            assessment = "MINIMAL"
        elif abs(delta) < 3.0:
            assessment = "SLIGHT"
        elif abs(delta) < 7.0:
            assessment = "MODERATE"
        elif abs(delta) < 15.0:
            assessment = "STRONG"
        else:
            assessment = "EXTREME"

        total_battles_all += battles
        weighted_delta_sum += delta * battles

        print(f"{level:>5} {without:>10.1f}% {with_item:>10.1f}% {delta:>+8.1f}% {assessment:<15} {battles:>7,}")

    print(f"{'-' * 80}")

    # Calculate overall weighted average
    overall_weighted_delta = weighted_delta_sum / total_battles_all if total_battles_all > 0 else 0
    print(f"{'OVERALL':<6} {'---':<12} {'---':<12} {overall_weighted_delta:>+8.1f}% {'WEIGHTED AVG':<15} {total_battles_all:>7,}")
    print()

    # Trend analysis
    print(f"📈 TREND ANALYSIS")
    print(f"{'-' * 40}")

    # Calculate trend (linear regression-like analysis)
    deltas = [r['delta'] for r in level_results]
    levels = [r['level'] for r in level_results]

    # Simple trend calculation
    early_avg = sum(deltas[:3]) / 3  # Levels 2-4
    mid_avg = sum(deltas[3:6]) / 3   # Levels 5-7
    late_avg = sum(deltas[6:]) / 3   # Levels 8-10

    print(f"Early levels (2-4):  {early_avg:+.1f}% average delta")
    print(f"Mid levels (5-7):    {mid_avg:+.1f}% average delta")
    print(f"Late levels (8-10):  {late_avg:+.1f}% average delta")
    print()

    # Trend interpretation
    if early_avg > mid_avg > late_avg and (early_avg - late_avg) > 1.0:
        trend = "📉 DIMINISHING - Most effective at lower levels"
        trend_icon = "📉"
    elif late_avg > mid_avg > early_avg and (late_avg - early_avg) > 1.0:
        trend = "📈 SCALING - More effective at higher levels"
        trend_icon = "📈"
    elif max(deltas) - min(deltas) < 1.0:
        trend = "📊 STABLE - Consistent effect across levels"
        trend_icon = "📊"
    else:
        trend = "🎯 VARIABLE - Mixed effectiveness across levels"
        trend_icon = "🎯"

    print(f"🎯 OVERALL TREND: {trend}")

    # Best/worst levels
    best_level = max(level_results, key=lambda x: x['delta'])
    worst_level = min(level_results, key=lambda x: x['delta'])

    print(f"🏆 MOST EFFECTIVE: Level {best_level['level']} ({best_level['delta']:+.1f}% delta)")
    print(f"❌ LEAST EFFECTIVE: Level {worst_level['level']} ({worst_level['delta']:+.1f}% delta)")
    print()

    # Recommendations by level range
    print(f"💡 LEVEL-SPECIFIC RECOMMENDATIONS")
    print(f"{'-' * 50}")

    if early_avg > 3.0:
        print(f"🌟 EARLY GAME (2-4): HIGHLY RECOMMENDED (+{early_avg:.1f}% avg)")
    elif early_avg > 1.0:
        print(f"✅ EARLY GAME (2-4): RECOMMENDED (+{early_avg:.1f}% avg)")
    elif early_avg > 0:
        print(f"⚖️ EARLY GAME (2-4): SITUATIONAL (+{early_avg:.1f}% avg)")
    else:
        print(f"❌ EARLY GAME (2-4): NOT RECOMMENDED ({early_avg:+.1f}% avg)")

    if mid_avg > 3.0:
        print(f"🌟 MID GAME (5-7): HIGHLY RECOMMENDED (+{mid_avg:.1f}% avg)")
    elif mid_avg > 1.0:
        print(f"✅ MID GAME (5-7): RECOMMENDED (+{mid_avg:.1f}% avg)")
    elif mid_avg > 0:
        print(f"⚖️ MID GAME (5-7): SITUATIONAL (+{mid_avg:.1f}% avg)")
    else:
        print(f"❌ MID GAME (5-7): NOT RECOMMENDED ({mid_avg:+.1f}% avg)")

    if late_avg > 3.0:
        print(f"🌟 LATE GAME (8-10): HIGHLY RECOMMENDED (+{late_avg:.1f}% avg)")
    elif late_avg > 1.0:
        print(f"✅ LATE GAME (8-10): RECOMMENDED (+{late_avg:.1f}% avg)")
    elif late_avg > 0:
        print(f"⚖️ LATE GAME (8-10): SITUATIONAL (+{late_avg:.1f}% avg)")
    else:
        print(f"❌ LATE GAME (8-10): NOT RECOMMENDED ({late_avg:+.1f}% avg)")

    # Statistical confidence
    if total_battles_all >= 100000:
        confidence_rating = "🎯 EXCELLENT"
    elif total_battles_all >= 50000:
        confidence_rating = "💎 VERY HIGH"
    elif total_battles_all >= 25000:
        confidence_rating = "✅ HIGH"
    elif total_battles_all >= 10000:
        confidence_rating = "👍 GOOD"
    else:
        confidence_rating = "⚖️ MODERATE"

    print()
    print(f"📊 STATISTICAL CONFIDENCE: {confidence_rating}")
    print(f"   Based on {total_battles_all:,} total battles across {len(level_results)} levels")
    print()
    print(f"💎 OVERALL ITEM VALUE: {overall_weighted_delta:+.2f}% weighted average winrate delta")
    print(f"🏅 COMPREHENSIVE RATING: {confidence_rating} confidence across full level range")