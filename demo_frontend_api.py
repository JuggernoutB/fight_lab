#!/usr/bin/env python3
# demo_frontend_api.py - Telegram Mini App Frontend Demo

"""
This file demonstrates how the game/ API would be used in a Telegram Mini App

Backend (Python): Uses run_fight() for full game logic
Frontend (JavaScript): Receives clean JSON responses
"""

from game import run_fight, run_quick_fight

print("📱 TELEGRAM MINI APP DEMO - FRONTEND API")
print("=" * 50)

print("\n🎮 SCENARIO 1: Player vs AI Quick Match")
print("-" * 40)

# Simple battle for mobile UI
result = run_quick_fight("BRUISER", "ASSASSIN", seed=42)

print("Frontend receives this JSON:")
print(f"""{{
  "winner": "{result['winner']}",
  "rounds": {result['rounds']},
  "damage_dealt": {{
    "player": {result['damage_dealt']['a_to_b']:.1f},
    "ai": {result['damage_dealt']['b_to_a']:.1f}
  }}
}}""")

print("\n💻 Frontend JavaScript would do:")
print(f"""
const battleResult = {result};
if (battleResult.winner === 'A') {{
  showVictoryAnimation();
  updatePlayerStats(battleResult.damage_dealt.player);
}} else {{
  showDefeatAnimation();
}}
updateUI(`Fight lasted ${{battleResult.rounds}} rounds`);
""")

print("\n🏆 SCENARIO 2: Tournament Match with Full Data")
print("-" * 40)

# Full tournament fight with detailed data
fighter_a = {"type": "balanced", "role": "TANK"}
fighter_b = {"type": "balanced", "role": "SKIRMISHER"}
options = {"seed": 123, "include_detailed_log": True}

tournament_result = run_fight(fighter_a, fighter_b, options)

print("Backend sends full tournament data:")
print(f"""{{
  "winner": "{tournament_result['winner']}",
  "rounds": {tournament_result['rounds']},
  "fighters": {{
    "player": {{
      "role": "{tournament_result['fighter_a']['role']}",
      "final_hp": {tournament_result['fighter_a']['final_hp']:.1f}
    }},
    "opponent": {{
      "role": "{tournament_result['fighter_b']['role']}",
      "final_hp": {tournament_result['fighter_b']['final_hp']:.1f}
    }}
  }},
  "battle_log": [{len(tournament_result['log'])} events],
  "damage_summary": {{
    "to_player": {tournament_result['summary']['total_damage_to_a']:.1f},
    "to_opponent": {tournament_result['summary']['total_damage_to_b']:.1f}
  }}
}}""")

print("\n🎥 SCENARIO 3: Replay System (Event Animation)")
print("-" * 40)

if tournament_result['log']:
    print("Frontend can animate the fight step by step:")
    for i, event in enumerate(tournament_result['log'][:3]):  # Show first 3 rounds
        print(f"\nRound {event['round']} Animation:")
        for attack in event['attacks']:
            attacker_name = "Player" if attack['attacker'] == 'A' else "AI"
            defender_name = "Player" if attack['defender'] == 'A' else "AI"
            print(f"  🎬 {attacker_name} attacks {defender_name}: {attack['damage']:.1f} dmg ({attack['event']})")

print("\n🔧 SCENARIO 4: Custom Fighter Creation")
print("-" * 40)

# Custom fighter with player-defined stats
custom_fighter = {
    "type": "custom",
    "role": "PLAYER_CUSTOM",
    "stats": {"hp": 16, "attack": 14, "defense": 13, "agility": 11}
}
standard_opponent = {"type": "balanced", "role": "ASSASSIN"}

custom_result = run_fight(custom_fighter, standard_opponent, {"seed": 456, "include_detailed_log": False})

print(f"Custom fighter battle result: {custom_result['winner']} wins!")
print(f"Player's custom build performed: {custom_result['summary']['total_damage_to_b']:.1f} damage dealt")

print("\n✨ SUMMARY FOR TELEGRAM MINI APP DEVELOPMENT")
print("=" * 50)
print("🎯 Backend Integration Points:")
print("  - run_quick_fight() → Fast battles for mobile")
print("  - run_fight() → Full tournament/ranked matches")
print("  - Custom fighter creation → Player customization")
print("  - Deterministic seeds → Replay system")

print("\n📱 Frontend Features Enabled:")
print("  - Battle animations from event log")
print("  - Real-time damage counters")
print("  - Tournament brackets")
print("  - Player stat tracking")
print("  - Custom fighter builder")
print("  - Fight replay viewer")

print("\n🚀 Ready for Production!")
print("  - Clean JSON API responses")
print("  - No internal game engine exposure")
print("  - Telegram WebApp compatible")
print("  - Scalable for multiplayer tournaments")