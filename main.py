# main.py

from state.fight_state import FightState
from state.fighter_factory import create_fighter_balanced, print_fighter_stats
from simulation.simulator import simulate_fight
from simulation.benchmark import run_benchmark


# ============================================================
# MODE SWITCH
# ============================================================

MODE = "BENCHMARK"   # "SINGLE" or "BENCHMARK"


# ============================================================
# SINGLE FIGHT
# ============================================================

def run_single():

    # Create fighters using proper stat-based system
    a = create_fighter_balanced("BRUISER")
    b = create_fighter_balanced("ASSASSIN")

    state = FightState(
        round_id=0,
        fighter_a=a,
        fighter_b=b
    )

    # Deterministic fight for testing/debugging (seed=42)
    result_state, telemetry = simulate_fight(state, max_rounds=25, seed=42)

    print("\n===== V15 SINGLE RESULT =====")
    print("=== Fighter A (BRUISER) ===")
    print_fighter_stats(a)
    print(f"Final: HP={result_state.fighter_a.hp:.1f}, Stamina={result_state.fighter_a.stamina}")

    print("\n=== Fighter B (ASSASSIN) ===")
    print_fighter_stats(b)
    print(f"Final: HP={result_state.fighter_b.hp:.1f}, Stamina={result_state.fighter_b.stamina}")

    print(f"\nRounds: {result_state.round_id}")

    print("\n===== META =====")
    print("Momentum:", result_state.momentum)
    print("Deadlock:", result_state.deadlock_pressure)

    print("\n===== TELEMETRY =====")
    print("Events:", len(telemetry.events))
    print("Summary:", telemetry.summary())


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
    elif MODE == "BENCHMARK":
        run_mass_sim()
    else:
        print("Unknown MODE")


if __name__ == "__main__":
    run()