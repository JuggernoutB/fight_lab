# modes/run_single.py - Single fight mode with detailed logging
"""
Single fight mode for debugging and analysis
"""

import json
from game.run_fight import run_fight

def run_single(config_path):
    """
    Run single fight with configurable logging

    Args:
        config_path: Path to JSON config file
    """
    # Load configuration
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # Extract configuration
    seed = cfg.get("seed", 42)
    log_level = cfg.get("log_level", "release")
    fighter_a = cfg["fighter_a"]
    fighter_b = cfg["fighter_b"]

    print(f"🎲 Seed: {seed}")
    print(f"📋 Log Level: {log_level}")

    # Run the fight
    options = {
        "seed": seed,
        "include_detailed_log": True  # Always get detailed log
    }

    result = run_fight(fighter_a, fighter_b, options)

    # Print fight results
    print_fight_summary(result)

    # Print fight log based on log level
    if result["log"]:
        print(f"\n🎬 FIGHT LOG ({log_level.upper()}):")
        print("=" * 60)

        if log_level == "debug":
            print_debug_log(result["log"])
        else:
            print_release_log(result["log"])

    # Print final analysis
    print_fight_analysis(result)

def print_fight_summary(result):
    """Print basic fight summary"""
    print(f"\n🏆 FIGHT SUMMARY:")
    print("=" * 40)
    print(f"Winner: {result['winner']}")
    print(f"Rounds: {result['rounds']}")
    print(f"API Version: {result.get('api_version', 'N/A')}")
    print(f"Core Version: {result.get('core_version', 'N/A')}")

    # Fighter final states
    fa = result["fighter_a"]
    fb = result["fighter_b"]

    print(f"\n📊 FINAL STATES:")
    print(f"Fighter A ({fa['role']}): {fa['final_hp']:.1f} HP, {fa['final_stamina']} stamina")
    print(f"Fighter B ({fb['role']}): {fb['final_hp']:.1f} HP, {fb['final_stamina']} stamina")

    # Damage summary
    summary = result["summary"]
    print(f"\n💥 DAMAGE SUMMARY:")
    print(f"Damage to A: {summary['total_damage_to_a']:.1f}")
    print(f"Damage to B: {summary['total_damage_to_b']:.1f}")

def print_release_log(log_events):
    """Print human-readable fight log (for players/designers)"""
    for event in log_events:
        round_num = event["round"]
        attacks = event["attacks"]

        print(f"\n📍 Round {round_num}:")

        for attack in attacks:
            attacker = "Fighter A" if attack["attacker"] == "A" else "Fighter B"
            defender = "Fighter B" if attack["defender"] == "B" else "Fighter A"
            zone = attack["zone"]
            damage = attack["damage"]
            event_type = attack["event"]

            # Format event description
            if event_type == "dodge":
                print(f"  {attacker} attacks {defender} ({zone}) - DODGED!")
            elif event_type == "block":
                print(f"  {attacker} attacks {defender} ({zone}) - BLOCKED for {damage:.0f} damage")
            elif event_type == "block_break":
                print(f"  {attacker} BREAKS {defender}'s block ({zone}) for {damage:.0f} damage")
            elif event_type == "crit":
                print(f"  {attacker} CRITS {defender} ({zone}) for {damage:.0f} damage!")
            elif event_type == "hit":
                print(f"  {attacker} hits {defender} ({zone}) for {damage:.0f} damage")
            else:
                print(f"  {attacker} → {defender} ({zone}): {event_type} for {damage:.0f} damage")

def print_debug_log(log_events):
    """Print detailed debug log (for developers)"""
    for event in log_events:
        round_num = event["round"]
        attacks = event["attacks"]

        print(f"\n[Round {round_num}]")
        print("-" * 40)

        for i, attack in enumerate(attacks):
            attacker = attack["attacker"]
            defender = attack["defender"]
            zone = attack["zone"]
            damage = attack["damage"]
            event_type = attack["event"]

            print(f"Attack {i+1}: {attacker} → {defender}")
            print(f"  zone: {zone}")
            print(f"  damage: {damage:.2f}")
            print(f"  event: {event_type}")
            print()

def print_fight_analysis(result):
    """Print detailed fight analysis"""
    print(f"\n🔍 FIGHT ANALYSIS:")
    print("=" * 40)

    # Determine fight outcome
    winner = result["winner"]
    rounds = result["rounds"]

    if winner.startswith("DRAW"):
        print(f"🤝 Draw Result: {winner}")
    elif winner in ["A", "B"]:
        fighter_name = result[f"fighter_{winner.lower()}"]["role"]
        print(f"🏆 Winner: Fighter {winner} ({fighter_name})")

    print(f"📏 Fight Duration: {rounds} rounds")

    # Fight pacing analysis
    if rounds <= 5:
        print("⚡ Very fast fight - high damage output")
    elif rounds <= 10:
        print("🏃 Fast fight - good damage/defense balance")
    elif rounds <= 15:
        print("⚖️ Medium fight - balanced encounter")
    elif rounds <= 20:
        print("🐌 Long fight - defensive/stamina focused")
    else:
        print("🛡️ Very long fight - stamina exhaustion likely")

    # Damage efficiency analysis
    summary = result["summary"]
    total_damage = summary["total_damage_to_a"] + summary["total_damage_to_b"]
    damage_per_round = total_damage / rounds if rounds > 0 else 0

    print(f"💥 Total Damage Dealt: {total_damage:.1f}")
    print(f"📊 Damage Per Round: {damage_per_round:.1f}")

    if damage_per_round > 300:
        print("🔥 High-damage fight")
    elif damage_per_round > 200:
        print("⚔️ Medium-damage fight")
    else:
        print("🛡️ Low-damage fight")