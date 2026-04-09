#!/usr/bin/env python3
# demo_simulation_modes.py - Demonstration of all simulation modes

"""
Demonstration of Fight Logic V15 simulation modes
"""

import main

def demo_all_modes():
    """Demonstrate all three simulation modes"""

    print("🎮 FIGHT LOGIC V15 - SIMULATION MODES DEMO")
    print("=" * 60)

    modes = ["SINGLE", "BUILD", "BENCHMARK"]

    for i, mode in enumerate(modes):
        print(f"\n🔄 DEMO {i+1}/3: {mode} MODE")
        print("=" * 60)

        # Update mode
        original_mode = main.MODE
        main.MODE = mode

        # Run the mode
        if mode == "SINGLE":
            print("📋 Single deterministic fight for debugging...")
            main.run_single()

        elif mode == "BUILD":
            print("🛠️ Testing specific build against all archetypes...")
            print("(Testing HP=16, ATK=14, DEF=12, AGI=10 build)")
            main.run_build_test()

        elif mode == "BENCHMARK":
            print("📊 Mass simulation with balance validation...")
            print("(Running first 100 fights as demo - full run is 5000)")
            # Temporarily reduce fight count for demo
            original_num = main.simulation.benchmark.NUM_FIGHTS
            main.simulation.benchmark.NUM_FIGHTS = 100
            main.run_mass_sim()
            main.simulation.benchmark.NUM_FIGHTS = original_num

        # Restore original mode
        main.MODE = original_mode

        if i < len(modes) - 1:
            input("\n⏸️ Press Enter to continue to next mode...")

    print("\n🎉 DEMO COMPLETE!")
    print("\nTo use any mode:")
    print("1. Edit MODE variable in main.py")
    print("2. Run: python3 main.py")


if __name__ == "__main__":
    demo_all_modes()