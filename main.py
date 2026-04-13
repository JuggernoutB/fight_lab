#!/usr/bin/env python3
# main.py - Fight Logic V15 CLI Entry Point
"""
Fight Logic V15 - Production CLI Interface

Usage:
  python main.py                    # Default: benchmark mode
  python main.py benchmark          # Mass simulation (5000 fights) - legacy random
  python main.py benchmark_level [level] [fights]  # Level-based benchmark (default level=9)
  python main.py single             # Single fight (debug log - default)
  python main.py single configs/release_single.json  # Human-readable log
  python main.py single configs/compact_single.json  # Compact analysis log
  python main.py single configs/custom_single.json
  python main.py build              # Build analysis (default config)
  python main.py build configs/custom_build.json

Examples:
  python main.py single                               # Debug single fight (default)
  python main.py single configs/release_single.json  # Human-readable fight
  python main.py single configs/compact_single.json  # Compact analysis
  python main.py build                               # Test default build
  python main.py build configs/tank_build.json       # Test custom build
"""

import sys
import os

def print_usage():
    """Print usage information"""
    print(__doc__)

def run_benchmark():
    """Run benchmark mode (5000 fights)"""
    from simulation.benchmark import run_benchmark as benchmark
    from balance.validator import validate

    print("📊 BENCHMARK MODE - Mass Simulation")
    print("=" * 50)

    # Run benchmark (outputs all sections: BUILD, ROLE, ROUNDS, DRAW, DPS)
    results, summary, rounds_list = benchmark(5000)

    # Final section: BALANCE VALIDATION (most important)
    failed, report = validate(results, summary, rounds_list, n=5000)

    print("\n===== BALANCE VALIDATION =====")
    print(report)

    if failed:
        print("\n❌ BALANCE TEST FAILED")
        sys.exit(1)
    else:
        print("\n✅ BALANCE TEST PASSED")


def run_level_benchmark(level=9, num_fights=5000):
    """Run level-based benchmark mode"""
    from simulation.level_benchmark import run_level_benchmark, print_level_benchmark_results

    print("🎯 LEVEL-BASED BENCHMARK MODE")
    print("=" * 50)
    print(f"Level: {level}")
    print(f"Fights: {num_fights}")
    print()

    # Run level benchmark
    results = run_level_benchmark(level, num_fights)

    # Print results
    print_level_benchmark_results(results)

    # Simple balance check
    role_analysis = results.get("role_analysis", {})
    if role_analysis:
        sorted_roles = sorted(role_analysis.items(), key=lambda x: x[1]["winrate"], reverse=True)
        if len(sorted_roles) >= 2:
            best = sorted_roles[0][1]["winrate"]
            worst = sorted_roles[-1][1]["winrate"]
            spread = best - worst

            print(f"\n📈 LEVEL {level} BALANCE CHECK:")
            if spread < 0.15:
                print(f"✅ Role spread {spread*100:.1f}% - GOOD BALANCE")
                sys.exit(0)
            else:
                print(f"❌ Role spread {spread*100:.1f}% - NEEDS REBALANCING")
                sys.exit(1)


def run_single_mode(config_path=None, debug=False):
    """Run single fight mode"""
    from modes.run_single import run_single

    # Determine config path
    if config_path is None:
        if debug:
            config_path = "configs/debug_single.json"
        else:
            config_path = "configs/default_single.json"

    # Validate config file exists
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    print(f"⚔️ SINGLE MODE - {config_path}")
    print("=" * 50)

    run_single(config_path)

def run_build_mode(config_path=None):
    """Run build analysis mode"""
    from modes.run_build import run_build

    # Determine config path
    if config_path is None:
        config_path = "configs/default_build.json"

    # Validate config file exists
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    print(f"🛠️ BUILD MODE - {config_path}")
    print("=" * 50)

    run_build(config_path)

def main():
    """Main CLI router"""
    args = sys.argv[1:] if len(sys.argv) > 1 else ["benchmark"]

    if not args or args[0] in ["-h", "--help", "help"]:
        print_usage()
        return

    mode = args[0].lower()

    try:
        if mode == "benchmark":
            run_benchmark()

        elif mode == "benchmark_level":
            # Parse level benchmark arguments
            level = 9  # Default level
            num_fights = 5000  # Default fights

            if len(args) >= 2:
                try:
                    level = int(args[1])
                except ValueError:
                    print(f"❌ Level must be an integer: {args[1]}")
                    sys.exit(1)

            if len(args) >= 3:
                try:
                    num_fights = int(args[2])
                except ValueError:
                    print(f"❌ Number of fights must be an integer: {args[2]}")
                    sys.exit(1)

            run_level_benchmark(level, num_fights)

        elif mode == "single":
            # Parse single mode arguments
            if len(args) == 1:
                # Default single mode
                run_single_mode()
            elif len(args) == 2:
                if args[1] == "debug":
                    # Debug single mode
                    run_single_mode(debug=True)
                elif args[1].endswith('.json'):
                    # Custom config
                    run_single_mode(args[1])
                else:
                    print(f"❌ Unknown single mode argument: {args[1]}")
                    print("Valid options: debug, or path to .json config")
                    sys.exit(1)
            elif len(args) == 3 and args[1] == "debug":
                # Debug mode with custom config
                run_single_mode(args[2], debug=True)
            else:
                print("❌ Too many arguments for single mode")
                print("Usage: single [debug] [config.json]")
                sys.exit(1)

        elif mode == "build":
            # Parse build mode arguments
            if len(args) == 1:
                # Default build mode
                run_build_mode()
            elif len(args) == 2:
                if args[1].endswith('.json'):
                    # Custom config
                    run_build_mode(args[1])
                else:
                    print(f"❌ Build config must be a .json file: {args[1]}")
                    sys.exit(1)
            else:
                print("❌ Too many arguments for build mode")
                print("Usage: build [config.json]")
                sys.exit(1)

        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: benchmark, benchmark_level, single, build")
            print("Use --help for more information")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()