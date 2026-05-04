#!/usr/bin/env python3
# main.py - Fight Logic V15 CLI Entry Point
"""
Fight Logic V15 - Production CLI Interface

Usage:
  python main.py                    # Default: benchmark mode
  python main.py benchmark          # Mass simulation (5000 fights) - legacy random
  python main.py benchmark_level [level] [fights] [action_mode]  # Level-based benchmark (default level=9, action_mode=normal)
  python main.py single             # Single fight (debug log - default)
  python main.py single configs/release_single.json  # Human-readable log
  python main.py single configs/compact_single.json  # Compact analysis log
  python main.py single configs/custom_single.json
  python main.py build              # Build analysis (default config)
  python main.py build configs/custom_build.json
  python main.py test               # System test (levels 1-10, 100k fights each, AI mode)

Action modes:
  normal  # Equal behavior: 50% 1-2 attack zones, 33.3% 0-2 defense zones (default)
  ai      # AI behavior based on stamina/damage thresholds

Examples:
  python main.py single                               # Debug single fight (default)
  python main.py single configs/release_single.json  # Human-readable fight
  python main.py single configs/compact_single.json  # Compact analysis
  python main.py build                               # Test default build
  python main.py build configs/tank_build.json       # Test custom build
  python main.py test                                # Comprehensive system test
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


def run_level_benchmark(level=9, num_fights=5000, action_mode="normal"):
    """Run level-based benchmark mode"""
    from simulation.level_benchmark import run_level_benchmark, print_level_benchmark_results

    print("🎯 LEVEL-BASED BENCHMARK MODE")
    print("=" * 50)
    print(f"Level: {level}")
    print(f"Fights: {num_fights}")
    print(f"Action Mode: {action_mode}")
    print()

    # Run level benchmark
    results = run_level_benchmark(level, num_fights, action_mode)

    # Print results (includes BALANCE VALIDATION)
    print_level_benchmark_results(results)


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


def run_system_test():
    """Run comprehensive system test across all levels (1-10)"""
    import os
    from datetime import datetime
    from simulation.level_benchmark import run_level_benchmark, print_level_benchmark_results
    from output.html_export import export_benchmark_to_html

    print("🔬 SYSTEM TEST MODE")
    print("=" * 50)
    print("Running comprehensive test across levels 1-10")
    print("Each level: 100,000 fights with AI action mode")
    print()

    # Create test results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = f"output/test_{timestamp}"
    os.makedirs(test_dir, exist_ok=True)
    print(f"📁 Test reports will be saved to: {test_dir}")
    print()

    # Track test results
    test_results = []
    failed_levels = []

    # Test each level from 1 to 10
    for level in range(1, 11):
        print(f"🎯 TESTING LEVEL {level}")
        print("-" * 30)

        try:
            # Run level benchmark
            results = run_level_benchmark(level, 100000, "ai")

            # Print results (includes balance validation)
            print_level_benchmark_results(results)

            # Get balance test result
            balance_passed = results.get("balance_test_passed", False)

            # Generate HTML report in test directory
            html_filename = f"level_{level}_100000_ai_{timestamp}.html"
            html_path = os.path.join(test_dir, html_filename)
            export_benchmark_to_html(results, level, 100000, "ai", html_path)

            # Store test result
            test_result = {
                "level": level,
                "passed": balance_passed,
                "html_report": html_path
            }
            test_results.append(test_result)

            if not balance_passed:
                failed_levels.append(level)

            status = "✅ PASSED" if balance_passed else "❌ FAILED"
            print(f"\nLevel {level} balance test: {status}")
            print(f"HTML report: {html_path}")

        except Exception as e:
            print(f"\n❌ ERROR testing level {level}: {e}")
            failed_levels.append(level)
            test_results.append({
                "level": level,
                "passed": False,
                "error": str(e)
            })

        print("\n" + "=" * 50)
        print()

    # Print comprehensive summary
    print("📊 SYSTEM TEST SUMMARY")
    print("=" * 50)

    total_levels = len(test_results)
    passed_levels = [r for r in test_results if r.get("passed", False)]
    passed_count = len(passed_levels)

    print(f"Total levels tested: {total_levels}")
    print(f"Levels passed: {passed_count}")
    print(f"Levels failed: {len(failed_levels)}")
    print()

    if failed_levels:
        print("❌ FAILED LEVELS:")
        for level in failed_levels:
            result = next((r for r in test_results if r["level"] == level), {})
            if "error" in result:
                print(f"  Level {level}: ERROR - {result['error']}")
            else:
                print(f"  Level {level}: Balance validation failed")
        print()

    # Overall verdict
    all_passed = len(failed_levels) == 0
    if all_passed:
        print("🎉 OVERALL VERDICT: ✅ SYSTEM TEST PASSED")
        print("All levels passed balance validation!")
    else:
        print("💥 OVERALL VERDICT: ❌ SYSTEM TEST FAILED")
        print(f"{len(failed_levels)} out of {total_levels} levels failed balance validation.")

    print(f"\n📁 All test reports saved in: {test_dir}")
    print("\nTest completed!")


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
            action_mode = "normal"  # Default action mode

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

            if len(args) >= 4:
                action_mode = args[3].lower()
                if action_mode not in ["normal", "ai"]:
                    print(f"❌ Action mode must be 'normal' or 'ai': {args[3]}")
                    sys.exit(1)

            run_level_benchmark(level, num_fights, action_mode)

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

        elif mode == "test":
            # Comprehensive system test across all levels
            run_system_test()

        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: benchmark, benchmark_level, single, build, test")
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