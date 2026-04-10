# modes/run_build.py - Build analysis mode
"""
Build comparison mode for testing two builds against each other
"""

import json
from game.run_fight import run_fight

def run_build(config_path):
    """
    Run build comparison between two custom builds

    Args:
        config_path: Path to JSON config file
    """
    # Load configuration
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # Extract configuration
    seed = cfg.get("seed", 42)
    iterations = cfg.get("iterations", 5000)
    fighter_a = cfg["fighter_a"]
    fighter_b = cfg["fighter_b"]

    # Print build comparison info
    print_build_comparison_info(fighter_a, fighter_b, iterations, seed)

    print(f"\n🥊 RUNNING {iterations:,} SIMULATIONS")
    print("=" * 60)

    # Run multiple fights between the two builds
    wins_a = 0
    wins_b = 0
    draws = 0
    total_rounds = 0
    total_damage_to_a = 0
    total_damage_to_b = 0

    # Progress tracking
    progress_milestones = [i for i in range(0, iterations + 1, max(1, iterations // 10))]

    for i in range(iterations):
        # Show progress
        if i in progress_milestones:
            progress_pct = (i / iterations) * 100
            print(f"Progress: {i:,}/{iterations:,} ({progress_pct:.1f}%)")

        # Use incremental seed for reproducibility
        fight_seed = seed + i if seed else None

        options = {
            "seed": fight_seed,
            "include_detailed_log": False
        }

        result = run_fight(fighter_a, fighter_b, options)

        # Track results
        winner = result["winner"]
        rounds = result["rounds"]
        damage_to_a = result["summary"]["total_damage_to_a"]
        damage_to_b = result["summary"]["total_damage_to_b"]

        total_rounds += rounds
        total_damage_to_a += damage_to_a
        total_damage_to_b += damage_to_b

        # Count outcomes
        if winner == "A":
            wins_a += 1
        elif winner == "B":
            wins_b += 1
        else:
            draws += 1

    # Show final progress
    print(f"Progress: {iterations:,}/{iterations:,} (100.0%)")

    # Calculate final statistics
    win_rate_a = (wins_a / iterations) * 100
    win_rate_b = (wins_b / iterations) * 100
    draw_rate = (draws / iterations) * 100
    avg_rounds = total_rounds / iterations
    avg_damage_to_a = total_damage_to_a / iterations
    avg_damage_to_b = total_damage_to_b / iterations

    # Calculate DPS
    dps_by_a = avg_damage_to_b / avg_rounds if avg_rounds > 0 else 0
    dps_by_b = avg_damage_to_a / avg_rounds if avg_rounds > 0 else 0

    # Print build comparison results
    print_build_comparison_results(
        fighter_a, fighter_b, iterations,
        wins_a, wins_b, draws,
        avg_rounds, avg_damage_to_a, avg_damage_to_b,
        dps_by_a, dps_by_b
    )

def print_build_comparison_info(fighter_a, fighter_b, iterations, seed):
    """Print build comparison configuration info"""
    print(f"🛠️ BUILD COMPARISON:")
    print("=" * 50)

    # Fighter A info
    if fighter_a["type"] == "custom":
        stats_a = fighter_a["stats"]
        print(f"Fighter A ({fighter_a['role']}):")
        print(f"  HP={stats_a['hp']} | ATK={stats_a['attack']} | DEF={stats_a['defense']} | AGI={stats_a['agility']}")
    else:
        print(f"Fighter A: {fighter_a['type']} {fighter_a['role']}")

    # Fighter B info
    if fighter_b["type"] == "custom":
        stats_b = fighter_b["stats"]
        print(f"Fighter B ({fighter_b['role']}):")
        print(f"  HP={stats_b['hp']} | ATK={stats_b['attack']} | DEF={stats_b['defense']} | AGI={stats_b['agility']}")
    else:
        print(f"Fighter B: {fighter_b['type']} {fighter_b['role']}")

    print(f"\nSimulations: {iterations:,}")
    print(f"Base seed: {seed if seed else 'Random'}")

def print_build_comparison_results(fighter_a, fighter_b, iterations, wins_a, wins_b, draws,
                                   avg_rounds, avg_damage_to_a, avg_damage_to_b, dps_by_a, dps_by_b):
    """Print comprehensive build comparison results"""

    win_rate_a = (wins_a / iterations) * 100
    win_rate_b = (wins_b / iterations) * 100
    draw_rate = (draws / iterations) * 100

    print(f"\n📈 BUILD COMPARISON RESULTS:")
    print("=" * 50)

    # Overall Results
    print(f"\n🏆 FIGHT OUTCOMES ({iterations:,} simulations):")
    print(f"  Fighter A wins: {wins_a:,} ({win_rate_a:.1f}%)")
    print(f"  Fighter B wins: {wins_b:,} ({win_rate_b:.1f}%)")
    print(f"  Draws: {draws:,} ({draw_rate:.1f}%)")

    # Performance Metrics
    print(f"\n⚔️ COMBAT METRICS:")
    print(f"  Average fight length: {avg_rounds:.1f} rounds")
    print(f"  DPS by A: {dps_by_a:.1f}")
    print(f"  DPS by B: {dps_by_b:.1f}")

    # Damage Analysis
    print(f"\n💥 DAMAGE ANALYSIS:")
    print(f"  Damage to A: {avg_damage_to_a:.1f} avg")
    print(f"  Damage to B: {avg_damage_to_b:.1f} avg")

    # Determine winner and advantage
    if win_rate_a > win_rate_b:
        advantage = win_rate_a - win_rate_b
        print(f"\n🎯 RESULT: Fighter A dominates with {advantage:.1f}% advantage")
        if advantage > 20:
            print(f"  💪 STRONG ADVANTAGE - Fighter A significantly superior")
        elif advantage > 10:
            print(f"  ✅ MODERATE ADVANTAGE - Fighter A clearly better")
        else:
            print(f"  ⚖️ SLIGHT ADVANTAGE - Close but Fighter A edges out")
    elif win_rate_b > win_rate_a:
        advantage = win_rate_b - win_rate_a
        print(f"\n🎯 RESULT: Fighter B dominates with {advantage:.1f}% advantage")
        if advantage > 20:
            print(f"  💪 STRONG ADVANTAGE - Fighter B significantly superior")
        elif advantage > 10:
            print(f"  ✅ MODERATE ADVANTAGE - Fighter B clearly better")
        else:
            print(f"  ⚖️ SLIGHT ADVANTAGE - Close but Fighter B edges out")
    else:
        print(f"\n🎯 RESULT: Perfect balance - both builds equally strong")