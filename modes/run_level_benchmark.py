# modes/run_level_benchmark.py - Level-based benchmark mode

import sys
from simulation.level_benchmark import (
    run_level_benchmark,
    print_level_benchmark_results,
    compare_levels
)


def run_level_benchmark_mode(level: int = 9, num_fights: int = 5000):
    """Run level-based benchmark mode"""
    print("🎯 LEVEL BENCHMARK MODE")
    print("=" * 50)
    print(f"Level: {level}")
    print(f"Fights: {num_fights}")
    print()

    # Run benchmark
    results = run_level_benchmark(level, num_fights)

    # Print results
    print_level_benchmark_results(results)

    return results


def run_level_comparison_mode():
    """Compare different levels"""
    print("📊 LEVEL COMPARISON MODE")
    print("=" * 50)

    compare_levels()

    # Run quick benchmarks for multiple levels
    for level in [5, 7, 9, 11]:
        print(f"\n{'='*20} LEVEL {level} QUICK TEST {'='*20}")
        results = run_level_benchmark(level, num_fights=1000)

        # Quick summary
        summary = results["summary"]
        role_analysis = results["role_analysis"]

        print(f"Avg rounds: {summary['avg_rounds']:.1f}")

        if role_analysis:
            sorted_roles = sorted(role_analysis.items(), key=lambda x: x[1]["winrate"], reverse=True)
            best = sorted_roles[0]
            worst = sorted_roles[-1]
            spread = best[1]["winrate"] - worst[1]["winrate"]
            print(f"Role spread: {spread*100:.1f}% ({best[0]} vs {worst[0]})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "compare":
            run_level_comparison_mode()
        else:
            level = int(sys.argv[1])
            num_fights = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
            run_level_benchmark_mode(level, num_fights)
    else:
        run_level_benchmark_mode()