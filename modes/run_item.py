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

    level = config.get('level', 5)
    item_id = config.get('item_id', 'wooden_sword')
    battles_per_opponent = config.get('battles_per_opponent', 500)
    action_mode = config.get('action_mode', 'normal')

    print(f"🗡️ ITEM EFFECTIVENESS TEST")
    print(f"=" * 50)
    print(f"📦 Item: {item_id}")
    print(f"📊 Level: {level}")
    print(f"⚔️ Battles per opponent: {battles_per_opponent:,}")
    print(f"🎲 Action mode: {action_mode}")
    print()

    # Get the item being tested
    try:
        item = get_item(item_id)
        print(f"✅ Item loaded: {item.name}")
        print(f"   Slot: {item.slot.value}")
        print(f"   Modifiers: {item.modifiers}")
    except ValueError as e:
        print(f"❌ Error loading item '{item_id}': {e}")
        return

    print()
    print(f"🎯 TESTING METHODOLOGY")
    print(f"=" * 50)
    print(f"• Test fighter: UNIVERSAL level {level} build")
    print(f"• Opponent: Single random build (will expand later)")
    print(f"• Battles: {battles_per_opponent} per comparison")
    print(f"• Method: Build mode orchestration")
    print(f"• Metric: Winrate delta (with item - without item)")
    print()

    # Create UNIVERSAL test build
    test_build = create_universal_build_at_level(level)
    print(f"📋 Test Build (UNIVERSAL level {level}):")
    print(f"   HP: {test_build.hp_stat}, ATK: {test_build.attack}, DEF: {test_build.defense}, AGI: {test_build.agility}")

    # Create opponent build
    opponent = generate_random_fighter_at_level(level)
    print(f"🎯 Opponent ({opponent.role}):")
    print(f"   HP: {getattr(opponent, 'hp_stat', opponent.hp // 10)}, ATK: {opponent.attack}, DEF: {opponent.defense}, AGI: {opponent.agility}")
    print()

    # Create temporary config files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = "temp_item_configs"
    os.makedirs(temp_dir, exist_ok=True)

    config_without = f"{temp_dir}/test_without_{item_id}_{timestamp}.json"
    config_with = f"{temp_dir}/test_with_{item_id}_{timestamp}.json"

    try:
        # Generate configs
        create_build_config(config_without, test_build, opponent, battles_per_opponent, item=None, item_id=item_id)
        create_build_config(config_with, test_build, opponent, battles_per_opponent, item=item, item_id=item_id)

        print(f"🔬 RUNNING TESTS...")
        print(f"=" * 50)

        # Test WITHOUT item
        print(f"🥊 Testing without item...")
        winrate_without = run_build_test(config_without)

        print(f"🗡️ Testing with {item.name}...")
        winrate_with = run_build_test(config_with)

        # Calculate results
        delta = winrate_with - winrate_without

        # Print results
        print_item_test_results(item, winrate_without, winrate_with, delta, battles_per_opponent)

    finally:
        # Clean up temporary files
        cleanup_temp_files([config_without, config_with])

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

def print_item_test_results(item, winrate_without, winrate_with, delta, total_battles):
    """Print comprehensive item test results"""
    print()
    print(f"📈 ITEM EFFECTIVENESS RESULTS")
    print(f"=" * 60)
    print(f"🗡️ Item: {item.name}")
    print(f"📦 Modifiers: {item.modifiers}")
    print(f"⚔️ Total battles: {total_battles:,}")
    print()

    print(f"📊 PERFORMANCE COMPARISON")
    print(f"{'-' * 40}")
    print(f"Without item: {winrate_without:.1f}% winrate")
    print(f"With {item.name}: {winrate_with:.1f}% winrate")
    print(f"Item VALUE: {delta:+.1f}% winrate delta")
    print()

    # Effectiveness assessment
    if abs(delta) < 1.0:
        assessment = "MINIMAL EFFECT"
        icon = "😐"
    elif abs(delta) < 3.0:
        assessment = "SLIGHT EFFECT"
        icon = "🔹" if delta > 0 else "🔸"
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
    confidence = "HIGH" if total_battles >= 500 else "MEDIUM" if total_battles >= 100 else "LOW"
    print(f"   Confidence: {confidence} (based on {total_battles:,} battles)")
    print()

    if abs(delta) > 5.0:
        print(f"💡 RECOMMENDATION: This item shows {assessment.lower()}")
        if delta > 0:
            print(f"   ✅ Positive impact - consider using in builds")
        else:
            print(f"   ❌ Negative impact - avoid using this item")
    else:
        print(f"💡 RECOMMENDATION: This item has {assessment.lower()}")
        print(f"   ⚖️ Impact is minimal - other factors more important")