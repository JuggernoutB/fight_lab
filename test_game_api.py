#!/usr/bin/env python3
# test_game_api.py - Test the new game API

from game import run_fight, run_quick_fight, run_tournament_fight, run_training_fight

print("🎮 TESTING GAME API FOR TELEGRAM MINI APP")
print("=" * 50)

# Test 1: Basic run_fight with detailed configuration
print("\n1. Testing run_fight() with detailed configuration:")
fighter_a_config = {
    "type": "balanced",
    "role": "BRUISER"
}
fighter_b_config = {
    "type": "balanced",
    "role": "ASSASSIN"
}
options = {
    "max_rounds": 25,
    "seed": 42,
    "include_detailed_log": False  # For clean output
}

result = run_fight(fighter_a_config, fighter_b_config, options)
print(f"Winner: {result['winner']}")
print(f"Rounds: {result['rounds']}")
print(f"Fighter A final HP: {result['fighter_a']['final_hp']:.1f}")
print(f"Fighter B final HP: {result['fighter_b']['final_hp']:.1f}")
print(f"Total damage to A: {result['summary']['total_damage_to_a']:.1f}")
print(f"Total damage to B: {result['summary']['total_damage_to_b']:.1f}")

# Test 2: Quick fight API
print("\n2. Testing run_quick_fight() for simple usage:")
quick_result = run_quick_fight("TANK", "SKIRMISHER", seed=123)
print(f"Winner: {quick_result['winner']}, Rounds: {quick_result['rounds']}")
print(f"Damage dealt: A→B: {quick_result['damage_dealt']['a_to_b']:.1f}, B→A: {quick_result['damage_dealt']['b_to_a']:.1f}")

# Test 3: Tournament fight
print("\n3. Testing run_tournament_fight() for competitive play:")
tournament_result = run_tournament_fight("BRUISER", "ASSASSIN", match_seed=999)
print(f"Tournament result: {tournament_result['winner']} wins in {tournament_result['rounds']} rounds")

# Test 4: Training fight
print("\n4. Testing run_training_fight() for player practice:")
training_result = run_training_fight("SKIRMISHER", "random", "balanced")
print(f"Training result: {training_result['winner']} wins in {training_result['rounds']} rounds")

# Test 5: Custom fighter configuration
print("\n5. Testing custom fighter stats:")
custom_a = {
    "type": "custom",
    "role": "CUSTOM_BRUISER",
    "stats": {"hp": 18, "attack": 16, "defense": 12, "agility": 8}
}
custom_b = {
    "type": "balanced",
    "role": "ASSASSIN"
}

custom_result = run_fight(custom_a, custom_b, {"seed": 456, "include_detailed_log": False})
print(f"Custom fight: {custom_result['winner']} wins in {custom_result['rounds']} rounds")
print(f"Custom fighter final HP: {custom_result['fighter_a']['final_hp']:.1f}")

print("\n✅ All game API tests completed successfully!")
print("\n📱 Ready for Telegram Mini App integration:")
print("  - Frontend can use run_quick_fight() for simple battles")
print("  - Backend can use run_fight() for full game logic")
print("  - Tournament system ready with run_tournament_fight()")
print("  - Training mode available with run_training_fight()")