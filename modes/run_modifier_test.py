# modes/run_modifier_test.py - Comprehensive modifier effectiveness testing

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from items.item import Item, EquipmentSlot
from items.catalog import ITEM_CATALOG
from game.run_fight import run_fight


def create_test_item(modifier_name: str, modifier_value: float, slot: EquipmentSlot = EquipmentSlot.MAIN_HAND) -> Item:
    """Create a temporary test item with a single modifier"""
    item_name = f"Test_{modifier_name}_{modifier_value}"
    modifiers = {modifier_name: modifier_value}

    return Item(
        name=item_name,
        slot=slot,
        modifiers=modifiers
    )




def register_temporary_item(item: Item) -> str:
    """Temporarily register item in catalog and return its ID"""
    item_id = f"test_item_{item.name}"
    ITEM_CATALOG[item_id] = item
    return item_id


def unregister_temporary_item(item_id: str):
    """Remove temporary item from catalog"""
    if item_id in ITEM_CATALOG:
        del ITEM_CATALOG[item_id]


def run_single_modifier_test(modifier_name: str, modifier_value: float, level: int, battles: int) -> Tuple[float, str]:
    """Run test for a single modifier value and return winrate delta"""
    # Create test item
    test_item = create_test_item(modifier_name, modifier_value)

    # Register item temporarily
    item_id = register_temporary_item(test_item)

    try:
        # Create fighter configs directly
        base_stats = {
            "hp": level + 2,
            "attack": level + 2,
            "defense": level + 2,
            "agility": level + 2
        }

        # Fighter A has the test item
        equipment_with_item = {
            "helm": item_id if test_item.slot == EquipmentSlot.HELM else None,
            "cuirass": item_id if test_item.slot == EquipmentSlot.CUIRASS else None,
            "midplate": item_id if test_item.slot == EquipmentSlot.MIDPLATE else None,
            "waistguard": item_id if test_item.slot == EquipmentSlot.WAISTGUARD else None,
            "greaves": item_id if test_item.slot == EquipmentSlot.GREAVES else None,
            "main_hand": item_id if test_item.slot == EquipmentSlot.MAIN_HAND else None,
            "off_hand": item_id if test_item.slot == EquipmentSlot.OFF_HAND else None
        }

        fighter_a_config = {
            "type": "custom",
            "role": f"Test_With_{test_item.name}",
            "stats": base_stats,
            "equipment": equipment_with_item,
            "_verbose_equipment": False
        }

        # Fighter B has no equipment
        fighter_b_config = {
            "type": "custom",
            "role": "Control_No_Item",
            "stats": base_stats,
            "equipment": {
                "helm": None,
                "cuirass": None,
                "midplate": None,
                "waistguard": None,
                "greaves": None,
                "main_hand": None,
                "off_hand": None
            },
            "_verbose_equipment": False
        }

        # Run multiple fights (similar to run_build.py logic)
        wins_a = 0
        wins_b = 0
        draws = 0

        for i in range(battles):
            fight_seed = 42 + i  # Incremental seed for reproducibility

            options = {
                "seed": fight_seed,
                "include_detailed_log": False
            }

            try:
                result = run_fight(fighter_a_config, fighter_b_config, options)

                winner = result["winner"]
                if winner == "A":
                    wins_a += 1
                elif winner == "B":
                    wins_b += 1
                else:
                    draws += 1

            except Exception as e:
                return 0.0, f"ERROR: Fight simulation failed: {str(e)[:50]}"

        # Calculate winrate
        winrate = (wins_a / battles) * 100
        winrate_delta = winrate - 50.0

        return winrate_delta, "SUCCESS"

    except Exception as e:
        return 0.0, f"ERROR: {str(e)[:50]}"

    finally:
        # Clean up temporary item
        unregister_temporary_item(item_id)


def run_modifier_test(config_path: str):
    """Run comprehensive modifier effectiveness testing"""
    print("🔬 Loading modifier test configuration...")

    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)

    level = config.get('level', 5)
    battles_per_test = config.get('battles_per_test', 500)
    modifiers_to_test = config.get('modifiers_to_test', {})

    print(f"📋 Test Configuration:")
    print(f"   Level: {level}")
    print(f"   Battles per test: {battles_per_test}")
    print(f"   Modifiers to test: {len(modifiers_to_test)}")

    # Calculate total tests
    total_tests = sum(len(values) for values in modifiers_to_test.values())
    print(f"   Total tests: {total_tests}")
    print()

    # First, establish baseline (no modifier)
    print("📊 Establishing baseline (no modifiers)...")
    baseline_winrate, baseline_status = run_single_modifier_test('damage_base', 0.0, level, battles_per_test)

    if baseline_status != "SUCCESS":
        print(f"❌ Failed to establish baseline: {baseline_status}")
        return []

    # The baseline_winrate is the delta from 50%, so actual baseline is 50 + baseline_winrate
    actual_baseline = 50.0 + baseline_winrate
    print(f"   Baseline winrate: {actual_baseline:.2f}%")
    print()

    # Run tests
    results = []
    test_counter = 0

    print("🔥 RUNNING MODIFIER EFFECTIVENESS TESTS")
    print("=" * 60)

    for modifier_name, test_values in modifiers_to_test.items():
        print(f"\n📊 Testing modifier: {modifier_name}")
        print(f"    Values: {test_values}")

        for value in test_values:
            test_counter += 1
            progress_percent = (test_counter / total_tests) * 100

            print(f"    [{test_counter:3d}/{total_tests:3d}] ({progress_percent:5.1f}%) Testing {modifier_name} = {value:+.3f}...", end=" ")

            # Run the test
            raw_winrate_delta, status = run_single_modifier_test(
                modifier_name, value, level, battles_per_test
            )

            if status == "SUCCESS":
                # Calculate true delta relative to baseline
                # raw_winrate_delta is delta from 50%, we want delta from actual baseline
                actual_winrate = 50.0 + raw_winrate_delta
                true_delta = actual_winrate - actual_baseline

                # Categorize effect strength
                abs_delta = abs(true_delta)
                if abs_delta < 0.5:
                    effect_rating = "MINIMAL"
                elif abs_delta < 2.0:
                    effect_rating = "WEAK"
                elif abs_delta < 5.0:
                    effect_rating = "MODERATE"
                elif abs_delta < 10.0:
                    effect_rating = "STRONG"
                else:
                    effect_rating = "EXTREME"

                print(f"{true_delta:+6.2f}% ({effect_rating})")
            else:
                effect_rating = "ERROR"
                true_delta = 0.0
                print(f"FAILED ({status})")

            # Store result
            results.append({
                'modifier': modifier_name,
                'value': value,
                'winrate_delta': true_delta,
                'effect_rating': effect_rating,
                'status': status,
                'battles': battles_per_test
            })

    print()
    print("=" * 60)
    print("🏁 MODIFIER EFFECTIVENESS TEST COMPLETED")
    print()

    # Generate summary
    print_modifier_summary(results)

    # Generate HTML report if requested
    output_config = config.get('output', {})
    if output_config.get('generate_html', True):
        html_filename = output_config.get('html_filename', 'modifier_effectiveness_analysis.html')
        generate_modifier_html_report(results, config, html_filename)
        print(f"📄 HTML report generated: output/{html_filename}")

    return results


def print_modifier_summary(results: List[Dict]):
    """Print summary of modifier test results"""
    print("📋 MODIFIER EFFECTIVENESS SUMMARY")
    print("=" * 60)

    # Group by modifier
    by_modifier = {}
    for result in results:
        mod_name = result['modifier']
        if mod_name not in by_modifier:
            by_modifier[mod_name] = []
        by_modifier[mod_name].append(result)

    for modifier_name in sorted(by_modifier.keys()):
        modifier_results = by_modifier[modifier_name]
        successful_results = [r for r in modifier_results if r['status'] == 'SUCCESS']

        if not successful_results:
            print(f"\n❌ {modifier_name}: All tests failed")
            continue

        # Find best and worst values
        best = max(successful_results, key=lambda x: abs(x['winrate_delta']))
        worst = min(successful_results, key=lambda x: abs(x['winrate_delta']))

        print(f"\n📊 {modifier_name}:")
        print(f"    Range tested: {min(r['value'] for r in modifier_results):+.3f} to {max(r['value'] for r in modifier_results):+.3f}")
        print(f"    Best effect: {best['value']:+.3f} = {best['winrate_delta']:+.2f}% ({best['effect_rating']})")
        print(f"    Minimal effect: {worst['value']:+.3f} = {worst['winrate_delta']:+.2f}% ({worst['effect_rating']})")
        print(f"    Successful tests: {len(successful_results)}/{len(modifier_results)}")


def generate_modifier_html_report(results: List[Dict], config: Dict, filename: str):
    """Generate comprehensive HTML report for modifier testing"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Group results by modifier
    by_modifier = {}
    for result in results:
        mod_name = result['modifier']
        if mod_name not in by_modifier:
            by_modifier[mod_name] = []
        by_modifier[mod_name].append(result)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modifier Effectiveness Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            padding: 30px;
        }}

        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}

        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 40px;
        }}

        .config-info {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}

        .modifier-section {{
            margin-bottom: 40px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
        }}

        .modifier-title {{
            font-size: 1.4em;
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: bold;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: center;
        }}

        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        .effect-MINIMAL {{ color: #95a5a6; }}
        .effect-WEAK {{ color: #f39c12; }}
        .effect-MODERATE {{ color: #e67e22; }}
        .effect-STRONG {{ color: #e74c3c; }}
        .effect-EXTREME {{ color: #8e44ad; font-weight: bold; }}
        .effect-ERROR {{ color: #c0392b; font-style: italic; }}

        .positive-delta {{ color: #27ae60; }}
        .negative-delta {{ color: #e74c3c; }}

        .summary-stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }}

        .summary-stat {{
            background: #3498db;
            color: white;
            padding: 15px;
            border-radius: 8px;
            min-width: 120px;
        }}

        .summary-stat h3 {{
            margin: 0 0 5px 0;
            font-size: 1.2em;
        }}

        .summary-stat p {{
            margin: 0;
            font-size: 1.1em;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Modifier Effectiveness Analysis</h1>

        <div class="config-info">
            <strong>Generated:</strong> {timestamp}<br>
            <strong>Level:</strong> {config.get('level', 5)}<br>
            <strong>Battles per test:</strong> {config.get('battles_per_test', 500):,}<br>
            <strong>Total tests:</strong> {len(results):,}<br>
            <strong>Successful tests:</strong> {len([r for r in results if r['status'] == 'SUCCESS']):,}
        </div>

        <div class="summary-stats">
            <div class="summary-stat">
                <h3>Modifiers</h3>
                <p>{len(by_modifier)}</p>
            </div>
            <div class="summary-stat">
                <h3>Tests</h3>
                <p>{len(results):,}</p>
            </div>
            <div class="summary-stat">
                <h3>Battles</h3>
                <p>{len(results) * config.get('battles_per_test', 500):,}</p>
            </div>
        </div>
"""

    # Add individual modifier sections
    for modifier_name in sorted(by_modifier.keys()):
        modifier_results = by_modifier[modifier_name]
        successful_results = [r for r in modifier_results if r['status'] == 'SUCCESS']

        html_content += f"""
        <div class="modifier-section">
            <div class="modifier-title">📊 {modifier_name.replace('_', ' ').title()}</div>
            <p><strong>Tests:</strong> {len(modifier_results)} |
               <strong>Successful:</strong> {len(successful_results)} |
               <strong>Range:</strong> {min(r['value'] for r in modifier_results):+.3f} to {max(r['value'] for r in modifier_results):+.3f}</p>

            <table>
                <thead>
                    <tr>
                        <th>Value</th>
                        <th>Winrate Delta</th>
                        <th>Effect Rating</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Sort results by value
        sorted_results = sorted(modifier_results, key=lambda x: x['value'])

        for result in sorted_results:
            delta = result['winrate_delta']
            delta_class = 'positive-delta' if delta > 0 else 'negative-delta'
            effect_class = f"effect-{result['effect_rating']}"

            html_content += f"""
                    <tr>
                        <td>{result['value']:+.3f}</td>
                        <td class="{delta_class}">{delta:+.2f}%</td>
                        <td class="{effect_class}">{result['effect_rating']}</td>
                        <td>{result['status']}</td>
                    </tr>
"""

        html_content += """
                </tbody>
            </table>
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    # Write to output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)