# modes/run_build.py - Build analysis mode
"""
Build analysis mode for testing custom fighter builds
"""

import json
from game.run_fight import run_fight

def run_build(config_path):
    """
    Run build analysis against multiple opponents

    Args:
        config_path: Path to JSON config file
    """
    # Load configuration
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # Extract configuration
    seed = cfg.get("seed", 42)
    iterations = cfg.get("iterations", 20)
    fighter_a = cfg["fighter_a"]
    opponents = cfg.get("opponents", [])

    # Print build info
    print_build_info(fighter_a, iterations, seed)

    # Test against each opponent
    overall_wins = 0
    overall_fights = 0
    matchup_results = {}

    for opponent in opponents:
        opponent_name = opponent["name"]
        print(f"\n🥊 TESTING VS {opponent_name}")
        print("-" * 40)

        # Run multiple fights
        wins = 0
        draws = 0
        losses = 0
        total_rounds = 0
        total_damage_dealt = 0
        total_damage_taken = 0

        for i in range(iterations):
            # Use incremental seed for each fight
            fight_seed = seed + i if seed else None

            options = {
                "seed": fight_seed,
                "include_detailed_log": False
            }

            result = run_fight(fighter_a, opponent, options)

            # Track results
            winner = result["winner"]
            rounds = result["rounds"]
            damage_to_a = result["summary"]["total_damage_to_a"]
            damage_to_b = result["summary"]["total_damage_to_b"]

            total_rounds += rounds
            total_damage_dealt += damage_to_b
            total_damage_taken += damage_to_a

            # Count outcomes
            if winner == "A":
                wins += 1
            elif winner == "B":
                losses += 1
            else:
                draws += 1

        # Calculate statistics
        win_rate = (wins / iterations) * 100
        draw_rate = (draws / iterations) * 100
        loss_rate = (losses / iterations) * 100
        avg_rounds = total_rounds / iterations
        avg_damage_dealt = total_damage_dealt / iterations
        avg_damage_taken = total_damage_taken / iterations

        # Store results
        matchup_results[opponent_name] = {
            "win_rate": win_rate,
            "draw_rate": draw_rate,
            "loss_rate": loss_rate,
            "avg_rounds": avg_rounds,
            "avg_damage_dealt": avg_damage_dealt,
            "avg_damage_taken": avg_damage_taken
        }

        # Print matchup results
        status_emoji = get_matchup_emoji(win_rate)
        print(f"{status_emoji} Win Rate: {win_rate:5.1f}% ({wins}W/{draws}D/{losses}L)")
        print(f"   Avg Rounds: {avg_rounds:4.1f}")
        print(f"   Damage Dealt: {avg_damage_dealt:5.0f}")
        print(f"   Damage Taken: {avg_damage_taken:5.0f}")

        overall_wins += wins
        overall_fights += iterations

    # Print overall analysis
    print_build_analysis(matchup_results, overall_wins, overall_fights, fighter_a)

def print_build_info(fighter_config, iterations, seed):
    """Print build configuration info"""
    print(f"🛠️ BUILD CONFIGURATION:")

    if fighter_config["type"] == "custom":
        stats = fighter_config["stats"]
        print(f"Custom Build: HP={stats['hp']} | ATK={stats['attack']} | DEF={stats['defense']} | AGI={stats['agility']}")
    else:
        print(f"Preset Build: {fighter_config['type']} {fighter_config['role']}")

    print(f"Iterations per matchup: {iterations}")
    print(f"Base seed: {seed if seed else 'Random'}")

def get_matchup_emoji(win_rate):
    """Get emoji based on win rate"""
    if win_rate >= 70:
        return "🔥"  # Dominating
    elif win_rate >= 60:
        return "✅"  # Favorable
    elif win_rate >= 50:
        return "⚖️"  # Even
    elif win_rate >= 40:
        return "⚠️"  # Unfavorable
    else:
        return "❌"  # Bad matchup

def print_build_analysis(results, total_wins, total_fights, fighter_config):
    """Print comprehensive build analysis"""
    print(f"\n📈 OVERALL ANALYSIS:")
    print("=" * 50)

    overall_win_rate = (total_wins / total_fights) * 100 if total_fights > 0 else 0
    print(f"Overall Win Rate: {overall_win_rate:.1f}% ({total_wins}/{total_fights})")

    # Find best/worst matchups
    if results:
        best_matchup = max(results.items(), key=lambda x: x[1]["win_rate"])
        worst_matchup = min(results.items(), key=lambda x: x[1]["win_rate"])

        print(f"Best Matchup: {best_matchup[0]} ({best_matchup[1]['win_rate']:.1f}%)")
        print(f"Worst Matchup: {worst_matchup[0]} ({worst_matchup[1]['win_rate']:.1f}%)")

        # Calculate matchup spread
        win_rates = [r["win_rate"] for r in results.values()]
        spread = max(win_rates) - min(win_rates)
        print(f"Matchup Spread: {spread:.1f}%")

    # Build power assessment
    print(f"\n🎯 BUILD ASSESSMENT:")
    if overall_win_rate >= 75:
        print("  🔥 OVERPOWERED - Consider nerfs")
        print("  This build dominates most matchups")
    elif overall_win_rate >= 65:
        print("  💪 VERY STRONG - Top tier competitive")
        print("  Excellent performance across most matchups")
    elif overall_win_rate >= 55:
        print("  ✅ STRONG - Good competitive viability")
        print("  Above average with some favorable matchups")
    elif overall_win_rate >= 45:
        print("  ⚖️ BALANCED - Fair competitive standing")
        print("  Even matchups, skill-dependent outcomes")
    elif overall_win_rate >= 35:
        print("  ⚠️ WEAK - Needs improvements")
        print("  Below average, limited competitive viability")
    else:
        print("  💀 UNDERPOWERED - Major rework needed")
        print("  Struggles in most matchups")

    # Tactical recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if fighter_config["type"] == "custom":
        stats = fighter_config["stats"]
        print_stat_recommendations(stats, overall_win_rate, results)
    else:
        print("  Use custom builds to test specific stat allocations")

def print_stat_recommendations(stats, win_rate, results):
    """Print recommendations based on stats and performance"""
    hp = stats["hp"]
    attack = stats["attack"]
    defense = stats["defense"]
    agility = stats["agility"]

    if win_rate < 45:
        # Underperforming build
        if hp < 12:
            print("  • Consider increasing HP for survivability")
        if attack < 12:
            print("  • Consider increasing Attack for damage output")
        if defense < 12 and attack >= 14:
            print("  • Consider balancing with more Defense")
        if agility < 10:
            print("  • Consider increasing Agility for dodge/crit")

    elif win_rate > 65:
        # Overperforming build
        if attack > 15:
            print("  • Attack might be too high, consider reducing")
        if hp > 16:
            print("  • HP might be excessive, consider reallocation")

    # Specific tactical advice
    total_stats = hp + attack + defense + agility
    if total_stats > 60:
        print("  • High total stats - consider more balanced allocation")
    elif total_stats < 50:
        print("  • Low total stats - build has room for improvement")

    # Analyze stat distribution
    max_stat = max(hp, attack, defense, agility)
    min_stat = min(hp, attack, defense, agility)
    if max_stat - min_stat > 8:
        print("  • Very specialized build - vulnerable to counter-builds")