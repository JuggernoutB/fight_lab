# modes/run_single.py - Single fight mode with detailed logging
"""
Single fight mode for debugging and analysis
"""

import json
from game.run_fight import run_fight

def format_fatigue_level(level):
    """Format fatigue level with color indicators"""
    if level == 0:
        return "🟢 FRESH"
    elif level == 1:
        return "🟡 TIRED"
    else:
        return "🔴 EXHAUSTED"

def format_event(event_type, damage, absorbed=None):
    """Format event with visual highlights for key moments"""
    if event_type == "crit":
        return f"💥 CRIT {damage:.1f}"
    elif event_type == "dodge":
        return "💨 DODGE"
    elif event_type == "block":
        absorbed_text = ""
        if absorbed and (absorbed.get("block", 0) > 0 or absorbed.get("dodge", 0) > 0):
            total_absorbed = absorbed.get("block", 0) + absorbed.get("dodge", 0)
            absorbed_text = f" / -{total_absorbed:.1f}"
        return f"🛡️ BLOCK {damage:.1f}{absorbed_text}"
    else:
        return f"⚔️ HIT {damage:.1f}"

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
    level = cfg.get("level", 12)  # Default level 12 if not specified
    fighter_a = cfg["fighter_a"].copy()
    fighter_b = cfg["fighter_b"].copy()

    # Add level to fighter configs if specified globally
    if level != 12:
        fighter_a["level"] = level
        fighter_b["level"] = level

    print(f"🎲 Seed: {seed}")
    print(f"📋 Log Level: {log_level}")
    if level != 12:
        print(f"⚡ Level: {level}")

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
        elif log_level == "compact":
            print_compact_log(result["log"])
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

    # Fighter initial states and stats
    fa = result["fighter_a"]
    fb = result["fighter_b"]

    print(f"\n📊 FIGHTER STATS:")
    # Calculate total stats for validation
    fa_total = fa['stats']['hp'] + fa['stats']['attack'] + fa['stats']['defense'] + fa['stats']['agility']
    fb_total = fb['stats']['hp'] + fb['stats']['attack'] + fb['stats']['defense'] + fb['stats']['agility']

    print(f"Fighter A ({fa['role']}):")
    print(f"  Stats: HP={fa['stats']['hp']}, ATK={fa['stats']['attack']}, DEF={fa['stats']['defense']}, AGI={fa['stats']['agility']} (Total: {fa_total})")
    print(f"  Initial: {fa['initial_hp']:.1f} HP, {fa['initial_stamina']} stamina")
    print(f"Fighter B ({fb['role']}):")
    print(f"  Stats: HP={fb['stats']['hp']}, ATK={fb['stats']['attack']}, DEF={fb['stats']['defense']}, AGI={fb['stats']['agility']} (Total: {fb_total})")
    print(f"  Initial: {fb['initial_hp']:.1f} HP, {fb['initial_stamina']} stamina")

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
        print("-" * 60)

        # Show fighter states at start of round
        if "fighters_pre_round" in event:
            fighters = event["fighters_pre_round"]
            print("Fighter States:")
            for fighter_id, state in fighters.items():
                fatigue_str = format_fatigue_level(state["fatigue_level"])
                print(f"  {fighter_id}: HP={state['hp']:.1f} | Stamina={state['stamina']} | {fatigue_str}")
            print()

        # Show attacks
        for i, attack in enumerate(attacks):
            attacker = attack["attacker"]
            defender = attack["defender"]
            zone = attack["zone"]
            damage = attack["damage"]
            event_type = attack["event"]

            absorbed = attack.get("absorbed")
            event_str = format_event(event_type, damage, absorbed)
            print(f"Attack {i+1}: {attacker} → {defender} ({zone}) → {event_str}")

        # Show absorption events if any (DISABLED for cleaner log)
        # if "absorption_events" in event:
        #     print("Absorption Events:")
        #     for abs_event in event["absorption_events"]:
        #         fighter_id = abs_event["fighter"]
        #         resource_before = abs_event["resource_before"]
        #         resource_after = abs_event["resource_after"]
        #         probability = abs_event["probability"]
        #         print(f"  🔮 Fighter {fighter_id}: Absorption Event! ({resource_before:.3f} → {resource_after:.3f}, prob={probability:.3f})")

        # Skip protection events display removed

        print()

def print_compact_log(log_events):
    """Print compact debug log for quick analysis"""
    for event in log_events:
        round_num = event["round"]
        attacks = event["attacks"]

        # Show fighter states compactly
        if "fighters_pre_round" in event:
            fighters = event["fighters_pre_round"]
            a_state = fighters["A"]
            b_state = fighters["B"]
            a_fatigue = format_fatigue_level(a_state["fatigue_level"])
            b_fatigue = format_fatigue_level(b_state["fatigue_level"])
            print(f"R{round_num}: A[{a_state['hp']:.0f}HP {a_state['stamina']}ST {a_fatigue}] B[{b_state['hp']:.0f}HP {b_state['stamina']}ST {b_fatigue}]")

        # Show attacks in one line
        attack_strs = []
        for attack in attacks:
            attacker = attack["attacker"]
            defender = attack["defender"]
            zone = attack["zone"]
            damage = attack["damage"]
            event_type = attack["event"]

            absorbed = attack.get("absorbed")
            event_str = format_event(event_type, damage, absorbed)
            attack_strs.append(f"{attacker}→{defender}({zone}) {event_str}")

        attacks_line = " | ".join(attack_strs)
        print(f"     {attacks_line}")
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