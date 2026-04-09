# main.py - Fight Logic V15 Entry Point
"""
Fight Logic V15 - Main simulation runner

Available modes:
- SINGLE: Single deterministic fight for debugging
- BUILD: Test specific stat builds against all archetypes
- BENCHMARK: Mass simulation with balance validation (5000 fights)

Usage:
1. Change MODE variable below to select mode
2. For BUILD mode: modify test_build stats in run_build_test()
3. Run: python3 main.py
"""

from state.fight_state import FightState
from state.fighter_factory import create_fighter_balanced, print_fighter_stats
from simulation.simulator import simulate_fight
from simulation.benchmark import run_benchmark


# ============================================================
# MODE SWITCH
# ============================================================

MODE = "SINGLE"   # "SINGLE", "BUILD", or "BENCHMARK"


# ============================================================
# SINGLE FIGHT
# ============================================================

def run_single():
    """Single deterministic fight for debugging and analysis"""

    print("⚔️ SINGLE FIGHT MODE")
    print("=" * 50)

    # Create fighters using proper stat-based system
    a = create_fighter_balanced("BRUISER")
    b = create_fighter_balanced("ASSASSIN")

    print("\n📊 FIGHTER SETUP:")
    print("=== Fighter A (BRUISER) ===")
    print_fighter_stats(a)

    print("\n=== Fighter B (ASSASSIN) ===")
    print_fighter_stats(b)

    state = FightState(
        round_id=0,
        fighter_a=a,
        fighter_b=b
    )

    # Deterministic fight for testing/debugging (seed=42)
    print(f"\n🎲 Running deterministic fight (seed=42)...")
    result_state, telemetry = simulate_fight(state, max_rounds=25, seed=42)

    print("\n🏆 FIGHT RESULTS:")
    print("=" * 50)

    # Determine winner
    winner = "DRAW"
    if result_state.fighter_a.hp <= 0 and result_state.fighter_b.hp <= 0:
        winner = "DRAW (Mutual Death)"
    elif result_state.fighter_b.hp <= 0:
        winner = "Fighter A (BRUISER) WINS!"
    elif result_state.fighter_a.hp <= 0:
        winner = "Fighter B (ASSASSIN) WINS!"
    elif result_state.end_reason == "stamina_exhaustion":
        winner = "DRAW (Stamina Exhaustion)"
    elif result_state.end_reason == "max_rounds":
        winner = "DRAW (Timeout)"

    print(f"🥇 Winner: {winner}")
    print(f"📏 Fight Length: {result_state.round_id} rounds")
    print(f"🔚 End Reason: {result_state.end_reason}")

    print(f"\n📈 FINAL STATE:")
    initial_hp_a = a.hp
    initial_hp_b = b.hp
    damage_to_a = initial_hp_a - result_state.fighter_a.hp
    damage_to_b = initial_hp_b - result_state.fighter_b.hp

    print(f"Fighter A: {result_state.fighter_a.hp:.1f}/{initial_hp_a:.0f} HP ({damage_to_a:.0f} damage taken)")
    print(f"         : {result_state.fighter_a.stamina}/100 Stamina")
    print(f"Fighter B: {result_state.fighter_b.hp:.1f}/{initial_hp_b:.0f} HP ({damage_to_b:.0f} damage taken)")
    print(f"         : {result_state.fighter_b.stamina}/100 Stamina")

    print(f"\n🎭 META STATE:")
    print(f"Momentum: {result_state.momentum}")
    print(f"Deadlock Pressure: {result_state.deadlock_pressure}")

    print(f"\n📊 COMBAT METRICS:")
    summary = telemetry.summary()

    if "total_damage" in summary:
        print(f"Total Damage Dealt: {summary['total_damage']:.1f}")
    if "rounds" in summary:
        print(f"Rounds Tracked: {summary['rounds']}")
    if "mechanics_distribution" in summary:
        mechanics = summary["mechanics_distribution"]
        print(f"Combat Events: Crit={mechanics.get('crit', 0)} | Dodge={mechanics.get('dodge', 0)} | Block={mechanics.get('block', 0)}")

    print(f"\n🔍 TELEMETRY:")
    print(f"Events Recorded: {len(telemetry.events)}")
    print("Full Summary:", summary)


# ============================================================
# BUILD TESTING
# ============================================================

def run_build_test():
    """Test specific fighter build against various opponents"""
    from state.fighter_factory import create_fighter, create_fighter_balanced
    import random

    print("🛠️ BUILD TESTING MODE")
    print("=" * 50)

    # Define test build (you can modify these stats)
    test_build = {
        "hp": 16,       # HP stat (8-18)
        "attack": 14,   # Attack stat (8-18)
        "defense": 12,  # Defense stat (8-18)
        "agility": 10   # Agility stat (8-18)
    }

    print(f"\n📊 TESTING BUILD:")
    print(f"  HP: {test_build['hp']} | Attack: {test_build['attack']} | Defense: {test_build['defense']} | Agility: {test_build['agility']}")

    # Create test fighter
    test_fighter = create_fighter(
        hp_stat=test_build["hp"],
        attack_stat=test_build["attack"],
        defense_stat=test_build["defense"],
        agility_stat=test_build["agility"],
        role="CUSTOM_BUILD"
    )

    print(f"  → Actual HP: {test_fighter.hp:.0f} | Actual Stamina: {test_fighter.stamina}")

    # Test against different opponent archetypes
    opponent_builds = {
        "BRUISER": create_fighter_balanced("BRUISER"),
        "ASSASSIN": create_fighter_balanced("ASSASSIN"),
        "TANK": create_fighter_balanced("TANK"),
        "SKIRMISHER": create_fighter_balanced("SKIRMISHER")
    }

    print(f"\n🥊 MATCHUP RESULTS:")
    print("-" * 50)

    total_wins = 0
    total_fights = 0
    results_summary = {}

    for opponent_name, opponent in opponent_builds.items():
        wins = 0
        draws = 0
        losses = 0
        total_rounds = 0
        total_damage_dealt = 0
        total_damage_taken = 0

        # Run multiple fights against this opponent
        num_tests = 20
        for i in range(num_tests):
            # Create fresh copies for each fight
            fighter_a = create_fighter(
                hp_stat=test_build["hp"],
                attack_stat=test_build["attack"],
                defense_stat=test_build["defense"],
                agility_stat=test_build["agility"],
                role="CUSTOM_BUILD"
            )

            fighter_b = create_fighter_balanced(opponent_name)

            state = FightState(0, fighter_a, fighter_b)

            # Use different seed for each test
            result_state, telemetry = simulate_fight(state, max_rounds=25, seed=i)

            # Track results
            initial_hp_a = fighter_a.hp
            initial_hp_b = fighter_b.hp
            damage_dealt = initial_hp_b - result_state.fighter_b.hp
            damage_taken = initial_hp_a - result_state.fighter_a.hp

            total_damage_dealt += damage_dealt
            total_damage_taken += damage_taken
            total_rounds += result_state.round_id

            # Determine winner
            if result_state.fighter_a.hp <= 0 and result_state.fighter_b.hp <= 0:
                draws += 1
            elif result_state.fighter_b.hp <= 0:
                wins += 1
            elif result_state.fighter_a.hp <= 0:
                losses += 1
            else:
                # Draw (timeout/stamina)
                draws += 1

        # Calculate percentages
        win_rate = (wins / num_tests) * 100
        draw_rate = (draws / num_tests) * 100
        loss_rate = (losses / num_tests) * 100
        avg_rounds = total_rounds / num_tests
        avg_damage_dealt = total_damage_dealt / num_tests
        avg_damage_taken = total_damage_taken / num_tests

        # Store results
        results_summary[opponent_name] = {
            "win_rate": win_rate,
            "draw_rate": draw_rate,
            "loss_rate": loss_rate,
            "avg_rounds": avg_rounds,
            "avg_damage_dealt": avg_damage_dealt,
            "avg_damage_taken": avg_damage_taken
        }

        total_wins += wins
        total_fights += num_tests

        # Print matchup results
        status = "✅" if win_rate >= 60 else "⚠️" if win_rate >= 40 else "❌"
        print(f"{status} vs {opponent_name:12}: {win_rate:5.1f}% WR | {avg_rounds:4.1f} rounds | {avg_damage_dealt:5.0f} dmg dealt")

    # Overall summary
    overall_win_rate = (total_wins / total_fights) * 100
    print(f"\n📈 OVERALL PERFORMANCE:")
    print(f"  Win Rate: {overall_win_rate:.1f}% ({total_wins}/{total_fights})")

    # Find best/worst matchups
    best_matchup = max(results_summary.items(), key=lambda x: x[1]["win_rate"])
    worst_matchup = min(results_summary.items(), key=lambda x: x[1]["win_rate"])

    print(f"  Best Matchup: {best_matchup[0]} ({best_matchup[1]['win_rate']:.1f}% WR)")
    print(f"  Worst Matchup: {worst_matchup[0]} ({worst_matchup[1]['win_rate']:.1f}% WR)")

    # Build assessment
    print(f"\n🎯 BUILD ASSESSMENT:")
    if overall_win_rate >= 70:
        print("  🔥 OVERPOWERED - Consider nerfs")
    elif overall_win_rate >= 60:
        print("  💪 STRONG - Good competitive build")
    elif overall_win_rate >= 40:
        print("  ⚖️ BALANCED - Fair matchups")
    elif overall_win_rate >= 30:
        print("  🤔 WEAK - Needs buffs")
    else:
        print("  💀 UNDERPOWERED - Major rework needed")


# ============================================================
# BENCHMARK
# ============================================================

def run_mass_sim():
    from balance.validator import validate

    # Run benchmark (outputs all sections: BUILD, ROLE, ROUNDS, DRAW, DPS)
    results, summary, rounds_list = run_benchmark(5000)

    # Final section: BALANCE VALIDATION (most important)
    failed, report = validate(results, summary, rounds_list, n=5000)

    print("\n===== BALANCE VALIDATION =====")
    print(report)

    if failed:
        print("\n❌ BALANCE TEST FAILED")
        exit(1)
    else:
        print("\n✅ BALANCE TEST PASSED")


# ============================================================
# ENTRY
# ============================================================

def run():
    if MODE == "SINGLE":
        run_single()
    elif MODE == "BUILD":
        run_build_test()
    elif MODE == "BENCHMARK":
        run_mass_sim()
    else:
        print(f"Unknown MODE: {MODE}")
        print("Available modes: SINGLE, BUILD, BENCHMARK")


if __name__ == "__main__":
    run()