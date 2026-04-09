# demo_separation.py - Demonstration of separation of concerns

from state.fight_state import FighterState, FightState
from simulation.game_engine import simulate_fight as game_engine
from simulation.simulator import simulate_fight as legacy_simulator

print("🧠 SEPARATION OF CONCERNS DEMO")
print("=" * 50)

# Setup same fight
fighter_a = FighterState(hp=1000, stamina=80, role="BRUISER", attack=15, defense=12, agility=8)
fighter_b = FighterState(hp=1000, stamina=80, role="ASSASSIN", attack=18, defense=8, agility=15)
state = FightState(round_id=0, fighter_a=fighter_a, fighter_b=fighter_b)

# ============================================================
# 1. GAME ENGINE - Clean API for games
# ============================================================
print("\n🎮 1. GAME ENGINE (New Minimal API)")
print("-" * 30)

game_result = game_engine(state, seed=42)

print(f"Purpose: Clean game API")
print(f"Returns: Pure game data")
print(f"Winner: {game_result['winner']}")
print(f"Rounds: {game_result['rounds']}")
print(f"Log entries: {len(game_result['log'])}")
print(f"Usage: Frontend, PvP, Mobile games, Web apps")

# ============================================================
# 2. SIMULATOR - Legacy telemetry API
# ============================================================
print("\n📊 2. SIMULATOR (Legacy Telemetry)")
print("-" * 30)

final_state, telemetry = legacy_simulator(state, seed=42)

print(f"Purpose: Analysis and balance testing")
print(f"Returns: (state, telemetry)")
print(f"Winner: computed from final_state")
print(f"Summary: {telemetry.summary()['rounds']} rounds")
print(f"Usage: Benchmarks, balance validation, statistics")

# ============================================================
# 3. USAGE EXAMPLES
# ============================================================
print("\n💡 3. USAGE PATTERNS")
print("-" * 30)

print("\n🎮 Game Frontend (React/Vue/Telegram WebApp):")
print("""
fight = game_engine(state)
animate_fight(fight['log'])
display_winner(fight['winner'])
""")

print("📊 Balance Analysis:")
print("""
final_state, telemetry = legacy_simulator(state)
stats = telemetry.summary()
validate_balance(stats)
""")

print("🔄 Replay System:")
print("""
fight = game_engine(state, seed=saved_seed)
replay_fight(fight['log'])
""")

print("🏆 Tournament System:")
print("""
for match in tournament:
    result = game_engine(match.state)
    tournament.advance_winner(result['winner'])
""")

print("\n✅ BENEFITS:")
print("- Game engine is pure function (no side effects)")
print("- Legacy analysis code unchanged")
print("- Clean separation: game logic vs analytics")
print("- Ready for production game integration")
print("- Enables frontend development")
print("- Supports replay systems")
print("- Maintains all existing functionality")