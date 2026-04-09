# Fight Logic V15 - Modular Combat Simulation System
"""
V15 Architecture: Clean separation of concerns

Main entry points:
- simulation.simulator.simulate_fight() - Single fight simulation
- simulation.fight_runner.run_benchmark() - Multiple fight analysis
"""

__version__ = "15.0.0"
__author__ = "Fight Logic Team"

# Main API exports
from simulation.simulator import simulate_fight

__all__ = [
    'simulate_fight'
]