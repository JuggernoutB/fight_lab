# simulation/level_benchmark.py - Level-based benchmark system

import random
from typing import Dict, List, Tuple
from state.level_system import (
    create_fighter_by_level,
    level_to_stat_budget,
    distribute_stats_by_weights,
    ROLE_WEIGHTS,
    analyze_level_distribution
)
from state.fight_state import FighterState, FightState
from .simulator import simulate_fight


def generate_random_fighter_at_level(level: int, force_role: str = None) -> FighterState:
    """Generate random fighter at specific level"""
    total_stats = level_to_stat_budget(level)

    if force_role:
        # Use role-based weights
        weights = ROLE_WEIGHTS[force_role]
        stats = distribute_stats_by_weights(total_stats, weights)
        role = force_role
    else:
        # Generate completely random distribution
        base_stats = {"hp": 3, "atk": 3, "def": 3, "agi": 3}
        remaining = total_stats - 12

        # Random distribution of remaining points
        for _ in range(remaining):
            stat = random.choice(["hp", "atk", "def", "agi"])
            base_stats[stat] += 1

        stats = base_stats

        # Classify role based on stats (import here to avoid circular import)
        from state.fighter_factory import classify_build_role
        role, _ = classify_build_role(stats["hp"], stats["atk"], stats["def"], stats["agi"])

    # Create fighter
    from state.fighter_factory import create_fighter
    fighter = create_fighter(
        hp_stat=stats["hp"],
        attack_stat=stats["atk"],
        defense_stat=stats["def"],
        agility_stat=stats["agi"],
        role=role
    )

    return fighter


def generate_level_matched_fighters(level: int) -> Tuple[FighterState, FighterState]:
    """Generate two fighters with identical level/stat budget"""
    fighter_a = generate_random_fighter_at_level(level)
    fighter_b = generate_random_fighter_at_level(level)

    # Verify fairness
    hp_a = getattr(fighter_a, 'hp_stat', 0)
    total_a = hp_a + fighter_a.attack + fighter_a.defense + fighter_a.agility

    hp_b = getattr(fighter_b, 'hp_stat', 0)
    total_b = hp_b + fighter_b.attack + fighter_b.defense + fighter_b.agility

    expected = level_to_stat_budget(level)

    if total_a != expected or total_b != expected:
        raise RuntimeError(f"Level fairness violation: Level {level} should have {expected} stats, got A={total_a}, B={total_b}")

    return fighter_a, fighter_b


def run_level_benchmark(level: int, num_fights: int = 5000) -> Dict:
    """Run benchmark at specific level"""
    print(f"📊 LEVEL {level} BENCHMARK - {level_to_stat_budget(level)} stat points")
    print(f"Running {num_fights} fights...")
    print("=" * 50)

    results = {
        "fights": [],
        "role_stats": {},
        "level_info": {
            "level": level,
            "stat_budget": level_to_stat_budget(level)
        },
        "builds_used": {},  # Track all unique builds
        "role_confidences": [],  # Track role classification confidence
        "mechanics_data": {},  # Track combat mechanics
        "damage_data": {},  # Track damage statistics
        "stamina_data": {},  # Track stamina distribution
        "dps_data": [],  # Track DPS values
        "total_damage_data": [],  # Track total damage values
        "rounds_distribution": {},  # Track detailed round distribution
        "role_absorption": {}  # Track damage absorption by role
    }

    # Progress tracking
    for i in range(num_fights):
        if i % 1000 == 0:
            print(f"Progress: {i}/{num_fights}")

        # Generate level-matched fighters
        fighter_a, fighter_b = generate_level_matched_fighters(level)

        # Simulate fight
        initial_state = FightState(0, fighter_a, fighter_b)
        final_state, telemetry = simulate_fight(initial_state, seed=i)

        # Track builds
        build_a = (getattr(fighter_a, 'hp_stat', 0), fighter_a.attack, fighter_a.defense, fighter_a.agility)
        build_b = (getattr(fighter_b, 'hp_stat', 0), fighter_b.attack, fighter_b.defense, fighter_b.agility)
        results["builds_used"][build_a] = results["builds_used"].get(build_a, 0) + 1
        results["builds_used"][build_b] = results["builds_used"].get(build_b, 0) + 1

        # Track role confidence
        from state.fighter_factory import classify_build_role
        _, confidence_a = classify_build_role(
            getattr(fighter_a, 'hp_stat', 0), fighter_a.attack, fighter_a.defense, fighter_a.agility
        )
        _, confidence_b = classify_build_role(
            getattr(fighter_b, 'hp_stat', 0), fighter_b.attack, fighter_b.defense, fighter_b.agility
        )
        results["role_confidences"].extend([confidence_a, confidence_b])

        # Calculate metrics
        rounds = final_state.round_id
        summary = telemetry.summary()

        # Track combat mechanics
        for k, v in summary["mechanics"].items():
            results["mechanics_data"][k] = results["mechanics_data"].get(k, 0) + v

        # Track damage data
        for k, v in summary["damage_split"].items():
            results["damage_data"][k] = results["damage_data"].get(k, 0) + v

        # Track stamina data
        for k, v in summary["stamina_distribution"].items():
            results["stamina_data"][k] = results["stamina_data"].get(k, 0) + v

        # Calculate DPS and total damage
        from simulation.benchmark import compute_total_damage, compute_dps
        total_damage = compute_total_damage(telemetry)
        dps = compute_dps(total_damage, rounds)
        results["dps_data"].append(dps)
        results["total_damage_data"].append(total_damage)

        # Track round distribution
        results["rounds_distribution"][rounds] = results["rounds_distribution"].get(rounds, 0) + 1

        # Track absorption by role
        if "damage_absorbed" in summary:
            absorbed = summary["damage_absorbed"]
            # Track for fighter A
            if fighter_a.role not in results["role_absorption"]:
                results["role_absorption"][fighter_a.role] = {"dodge": 0.0, "block": 0.0, "fights": 0}
            results["role_absorption"][fighter_a.role]["dodge"] += absorbed["dodge"]
            results["role_absorption"][fighter_a.role]["block"] += absorbed["block"]
            results["role_absorption"][fighter_a.role]["fights"] += 1

            # Track for fighter B
            if fighter_b.role not in results["role_absorption"]:
                results["role_absorption"][fighter_b.role] = {"dodge": 0.0, "block": 0.0, "fights": 0}
            results["role_absorption"][fighter_b.role]["dodge"] += absorbed["dodge"]
            results["role_absorption"][fighter_b.role]["block"] += absorbed["block"]
            results["role_absorption"][fighter_b.role]["fights"] += 1

        # Store result
        fight_result = {
            "fighter_a": {
                "role": fighter_a.role,
                "hp_stat": getattr(fighter_a, 'hp_stat', 0),
                "atk": fighter_a.attack,
                "def": fighter_a.defense,
                "agi": fighter_a.agility
            },
            "fighter_b": {
                "role": fighter_b.role,
                "hp_stat": getattr(fighter_b, 'hp_stat', 0),
                "atk": fighter_b.attack,
                "def": fighter_b.defense,
                "agi": fighter_b.agility
            },
            "winner": determine_winner(final_state),
            "rounds": final_state.round_id,
            "telemetry": telemetry.summary()
        }

        results["fights"].append(fight_result)

    # Analyze results
    results.update(analyze_level_results(results["fights"]))

    return results


def determine_winner(final_state: FightState) -> str:
    """Determine fight winner from final state"""
    a_alive = final_state.fighter_a.hp > 0
    b_alive = final_state.fighter_b.hp > 0

    if a_alive and b_alive:
        return "DRAW_TIMEOUT"
    elif a_alive and not b_alive:
        return "A"
    elif not a_alive and b_alive:
        return "B"
    else:
        return "DRAW_MUTUAL_DEATH"


def analyze_level_results(fights: List[Dict]) -> Dict:
    """Analyze results from level benchmark"""
    total_fights = len(fights)

    # Winner analysis
    winners = {"A": 0, "B": 0, "DRAW_TIMEOUT": 0, "DRAW_MUTUAL_DEATH": 0}
    for fight in fights:
        winners[fight["winner"]] += 1

    # Role analysis
    role_results = {}
    role_matchups = {}  # Track role vs role matchups
    for fight in fights:
        role_a = fight["fighter_a"]["role"]
        role_b = fight["fighter_b"]["role"]
        winner = fight["winner"]

        # Track role A results
        if role_a not in role_results:
            role_results[role_a] = {"wins": 0, "losses": 0, "draws": 0, "fights": 0}

        role_results[role_a]["fights"] += 1
        if winner == "A":
            role_results[role_a]["wins"] += 1
        elif winner == "B":
            role_results[role_a]["losses"] += 1
        else:
            role_results[role_a]["draws"] += 1

        # Track role B results
        if role_b not in role_results:
            role_results[role_b] = {"wins": 0, "losses": 0, "draws": 0, "fights": 0}

        role_results[role_b]["fights"] += 1
        if winner == "B":
            role_results[role_b]["wins"] += 1
        elif winner == "A":
            role_results[role_b]["losses"] += 1
        else:
            role_results[role_b]["draws"] += 1

        # Track role vs role matchups
        matchup_key = f"{role_a}_vs_{role_b}"
        reverse_matchup_key = f"{role_b}_vs_{role_a}"

        if matchup_key not in role_matchups:
            role_matchups[matchup_key] = {"wins": 0, "losses": 0, "draws": 0, "total": 0}
        if reverse_matchup_key not in role_matchups:
            role_matchups[reverse_matchup_key] = {"wins": 0, "losses": 0, "draws": 0, "total": 0}

        role_matchups[matchup_key]["total"] += 1
        role_matchups[reverse_matchup_key]["total"] += 1

        if winner == "A":
            # A wins vs B
            role_matchups[matchup_key]["wins"] += 1
            role_matchups[reverse_matchup_key]["losses"] += 1
        elif winner == "B":
            # B wins vs A
            role_matchups[matchup_key]["losses"] += 1
            role_matchups[reverse_matchup_key]["wins"] += 1
        else:  # Draw
            # Both get draws
            role_matchups[matchup_key]["draws"] += 1
            role_matchups[reverse_matchup_key]["draws"] += 1

    # Calculate winrates
    for role, stats in role_results.items():
        winrate = (stats["wins"] + 0.5 * stats["draws"]) / stats["fights"]
        stats["winrate"] = winrate

    # Fight length analysis
    rounds_list = [fight["rounds"] for fight in fights]
    avg_rounds = sum(rounds_list) / len(rounds_list)

    return {
        "summary": {
            "total_fights": total_fights,
            "winners": winners,
            "avg_rounds": avg_rounds,
            "min_rounds": min(rounds_list),
            "max_rounds": max(rounds_list)
        },
        "role_analysis": role_results,
        "role_matchups": role_matchups
    }


def print_level_benchmark_results(results: Dict):
    """Print formatted benchmark results (unified with legacy benchmark format)"""
    level = results["level_info"]["level"]
    stat_budget = results["level_info"]["stat_budget"]
    summary = results["summary"]
    total = summary["total_fights"]

    print(f"\n===== BUILD ANALYSIS =====")
    unique_builds = len(results["builds_used"])
    total_fighters = sum(results["builds_used"].values())
    print(f"Unique builds tested: {unique_builds}")
    print(f"Total fighters generated: {total_fighters}")
    print(f"Level {level} ({stat_budget} stat points) - Perfect fairness guaranteed")

    print(f"\n===== ROLE DISTRIBUTION =====")
    # Count roles from fight data
    from collections import Counter
    role_a = [fight["fighter_a"]["role"] for fight in results["fights"]]
    role_b = [fight["fighter_b"]["role"] for fight in results["fights"]]

    role_counter_a = Counter(role_a)
    role_counter_b = Counter(role_b)
    total_fighters_a = sum(role_counter_a.values())
    total_fighters_b = sum(role_counter_b.values())

    print("Fighter A roles:")
    for role, count in role_counter_a.items():
        percentage = (count / total_fighters_a) * 100
        print(f"  {role}: {count:4d} times ({percentage:5.1f}%)")

    print("Fighter B roles:")
    for role, count in role_counter_b.items():
        percentage = (count / total_fighters_b) * 100
        print(f"  {role}: {count:4d} times ({percentage:5.1f}%)")

    print(f"\n===== ROLE WINRATE MATRIX =====")

    role_analysis = results["role_analysis"]
    role_matchups = results["role_matchups"]

    # Get all roles that appear in fights
    all_roles = set(role_analysis.keys())
    sorted_roles_list = sorted(all_roles)

    # Calculate overall winrates for each role
    overall_winrates = {}
    for role, stats in role_analysis.items():
        overall_winrates[role] = {
            "winrate": stats["winrate"],
            "total": stats["fights"]
        }

    # Create winrate matrix
    def get_matchup_winrate(role_a, role_b):
        if role_a == role_b:
            return "N/A"

        matchup_key = f"{role_a}_vs_{role_b}"
        if matchup_key in role_matchups:
            stats = role_matchups[matchup_key]
            if stats["total"] > 0:
                winrate = (stats["wins"] + 0.5 * stats["draws"]) / stats["total"]
                return f"{winrate*100:5.1f}%"
        return "  0.0%"

    # Print header
    header = "                "
    for role in sorted_roles_list:
        header += f"  vs {role:8s}"
    header += "  | Overall"
    print(header)

    # Print matrix rows
    for role_a in sorted_roles_list:
        row = f"{role_a:12s}  :"
        for role_b in sorted_roles_list:
            winrate_str = get_matchup_winrate(role_a, role_b)
            row += f"    {winrate_str:>7s}"

        # Add overall winrate
        if role_a in overall_winrates:
            overall = overall_winrates[role_a]
            row += f"  |  {overall['winrate']*100:5.1f}% ({overall['total']} fights)"
        else:
            row += f"  |    0.0% (0 fights)"

        print(row)

    print(f"\n===== ROLE QUALITY ANALYSIS =====")
    all_confidences = results["role_confidences"]
    if all_confidences:
        avg_confidence = sum(all_confidences) / len(all_confidences)

        # Categorize builds by confidence
        pure_builds = len([c for c in all_confidences if c > 0.15])  # Clear role identity
        hybrid_builds = len([c for c in all_confidences if c < 0.05])  # Ambiguous role
        total_builds = len(all_confidences)

        pure_percentage = (pure_builds / total_builds) * 100 if total_builds > 0 else 0
        hybrid_percentage = (hybrid_builds / total_builds) * 100 if total_builds > 0 else 0

        print(f"Average confidence: {avg_confidence:.3f}")
        print(f"Pure builds (confidence > 0.15): {pure_builds:4d} ({pure_percentage:5.1f}%)")
        print(f"Hybrid builds (confidence < 0.05): {hybrid_builds:4d} ({hybrid_percentage:5.1f}%)")
        print(f"Confidence range: {min(all_confidences):.3f} - {max(all_confidences):.3f}")

    print(f"\n===== ROUNDS DISTRIBUTION =====")
    print(f"Average fight length: {summary['avg_rounds']:.1f} rounds")
    print(f"Range: {summary['min_rounds']} - {summary['max_rounds']} rounds")
    print("\nDetailed distribution:")
    sorted_rounds = sorted(results["rounds_distribution"].items())
    for rounds, count in sorted_rounds:
        percentage = (count / total) * 100
        print(f"  {rounds:2d} rounds: {count:4d} fights ({percentage:5.1f}%)")

    print(f"\n===== DRAW ANALYSIS =====")
    winners = summary["winners"]
    total_draws = winners.get("DRAW_TIMEOUT", 0) + winners.get("DRAW_MUTUAL_DEATH", 0)
    wins_a = winners.get("A", 0)
    wins_b = winners.get("B", 0)

    print(f"Total fights: {total}")
    print(f"Fighter A wins: {wins_a:4d} ({(wins_a/total)*100:5.1f}%)")
    print(f"Fighter B wins: {wins_b:4d} ({(wins_b/total)*100:5.1f}%)")
    print(f"Total draws: {total_draws:4d} ({(total_draws/total)*100:5.1f}%)")

    if total_draws > 0:
        timeout_draws = winners.get("DRAW_TIMEOUT", 0)
        mutual_death = winners.get("DRAW_MUTUAL_DEATH", 0)

        print("Draw breakdown:")
        if timeout_draws > 0:
            print(f"  Timeout (max rounds): {timeout_draws:4d} ({(timeout_draws/total)*100:5.1f}%)")
        if mutual_death > 0:
            print(f"  Mutual death: {mutual_death:4d} ({(mutual_death/total)*100:5.1f}%)")
    else:
        print("No draws occurred")

    print(f"\n===== DPS VARIANCE =====")
    if results["dps_data"]:
        dps_list = results["dps_data"]
        total_damage_list = results["total_damage_data"]

        avg_dps = sum(dps_list) / len(dps_list)
        var_dps = sum((x - avg_dps) ** 2 for x in dps_list) / len(dps_list)
        std_dps = var_dps ** 0.5
        avg_total_damage = sum(total_damage_list) / len(total_damage_list)

        print(f"Average DPS: {avg_dps:.1f}")
        print(f"DPS Variance: {var_dps:.1f}")
        print(f"DPS Std Dev: {std_dps:.1f}")
        print(f"Average total damage: {avg_total_damage:.1f}")
        print(f"DPS Range: {min(dps_list):.1f} - {max(dps_list):.1f}")

    print(f"\n===== DAMAGE ABSORPTION ANALYSIS =====")
    role_absorption = results.get("role_absorption", {})
    if role_absorption:
        print("Average damage absorbed per fight by role:")

        # Sort roles by total absorption (highest first)
        sorted_absorption = []
        for role, data in role_absorption.items():
            if data["fights"] > 0:
                avg_dodge = data["dodge"] / data["fights"]
                avg_block = data["block"] / data["fights"]
                total_avg = avg_dodge + avg_block
                sorted_absorption.append((role, avg_dodge, avg_block, total_avg, data["fights"]))

        sorted_absorption.sort(key=lambda x: x[3], reverse=True)  # Sort by total absorption

        for role, avg_dodge, avg_block, total_avg, fights in sorted_absorption:
            print(f"  {role:11s}: {total_avg:5.1f} total ({avg_dodge:4.1f} dodge + {avg_block:4.1f} block) from {fights} fights")
    else:
        print("No absorption data available")

    # Full balance validation (like legacy benchmark)
    print(f"\n===== BALANCE VALIDATION =====")

    # Prepare validation data
    num_fights = total

    # Calculate metrics for validation
    mechanics_avg = {}
    if results.get("mechanics_data"):
        for k, v in results["mechanics_data"].items():
            mechanics_avg[k] = v / num_fights

    damage_avg = {}
    if results.get("damage_data"):
        for k, v in results["damage_data"].items():
            damage_avg[k] = v / num_fights

    stamina_avg = {}
    if results.get("stamina_data"):
        for k, v in results["stamina_data"].items():
            stamina_avg[k] = v / num_fights

    # Calculate additional metrics
    avg_rounds = summary['avg_rounds']
    avg_dps = sum(results["dps_data"]) / len(results["dps_data"]) if results["dps_data"] else 0
    draw_rate = (winners.get("DRAW_TIMEOUT", 0) + winners.get("DRAW_MUTUAL_DEATH", 0)) / total

    # Calculate role balance spread (using overall winrates from matrix)
    role_balance_spread = 0.0
    if overall_winrates:
        winrates = [data["winrate"] for data in overall_winrates.values()]
        if len(winrates) >= 2:
            role_balance_spread = max(winrates) - min(winrates)

    # Import validation logic
    from balance.validator import validate_single_metric

    # Run validation checks
    print(f"[{'OK' if validate_single_metric('rounds_avg', avg_rounds) else 'FAIL'}]   rounds_avg: {avg_rounds:.4f}")
    print(f"[{'OK' if validate_single_metric('dps_avg', avg_dps) else 'FAIL'}]   dps_avg: {avg_dps:.4f}")

    draw_result = validate_single_metric('draw_rate', draw_rate)
    print(f"[{'OK' if draw_result else 'FAIL'}]   draw_rate: {draw_rate:.4f}" + ("" if draw_result else " not in (0.08, 0.16)"))

    # Mechanics validation
    if mechanics_avg:
        for metric in ['crit', 'dodge', 'block', 'block_break', 'hit']:
            if metric in mechanics_avg:
                result = validate_single_metric(metric, mechanics_avg[metric])
                print(f"[{'OK' if result else 'FAIL'}]   {metric}: {mechanics_avg[metric]:.4f}")

    # Damage validation
    if damage_avg:
        for metric in ['crit_dmg', 'normal_dmg', 'blocked_dmg']:
            metric_key = metric.replace('_dmg', '')
            if metric_key in damage_avg:
                result = validate_single_metric(metric, damage_avg[metric_key])
                print(f"[{'OK' if result else 'FAIL'}]   {metric}: {damage_avg[metric_key]:.4f}")

    # Stamina validation
    if stamina_avg:
        for metric in ['stamina_high', 'stamina_mid', 'stamina_low']:
            stamina_key = metric.replace('stamina_', '')
            if stamina_key in stamina_avg:
                result = validate_single_metric(metric, stamina_avg[stamina_key])
                range_text = ""
                if not result:
                    if metric == 'stamina_mid':
                        range_text = " not in (0.4, 0.55)"
                print(f"[{'OK' if result else 'FAIL'}]   {metric}: {stamina_avg[stamina_key]:.4f}{range_text}")

    # Role balance validation
    role_result = validate_single_metric('role_balance_spread', role_balance_spread)
    range_text = "" if role_result else " not in (0.0, 0.15)"
    print(f"[{'OK' if role_result else 'FAIL'}]   role_balance_spread: {role_balance_spread:.4f}{range_text}")

    # Final result
    all_passed = (validate_single_metric('rounds_avg', avg_rounds) and
                  validate_single_metric('dps_avg', avg_dps) and
                  validate_single_metric('draw_rate', draw_rate) and
                  role_result)

    # Add mechanics validation to final check
    if mechanics_avg:
        for metric in ['crit', 'dodge', 'block', 'block_break', 'hit']:
            if metric in mechanics_avg:
                all_passed = all_passed and validate_single_metric(metric, mechanics_avg[metric])

    # Add damage validation to final check
    if damage_avg:
        for metric in ['crit_dmg', 'normal_dmg', 'blocked_dmg']:
            metric_key = metric.replace('_dmg', '')
            if metric_key in damage_avg:
                all_passed = all_passed and validate_single_metric(metric, damage_avg[metric_key])

    # Add stamina validation to final check
    if stamina_avg:
        for metric in ['stamina_high', 'stamina_mid', 'stamina_low']:
            stamina_key = metric.replace('stamina_', '')
            if stamina_key in stamina_avg:
                all_passed = all_passed and validate_single_metric(metric, stamina_avg[stamina_key])

    if all_passed:
        print(f"\n✅ BALANCE TEST PASSED")
    else:
        print(f"\n❌ BALANCE TEST FAILED")


def compare_levels():
    """Compare different levels for scaling analysis"""
    print("=== LEVEL COMPARISON ===")
    print()

    for level in [5, 7, 9, 11]:
        print(f"Level {level} ({level_to_stat_budget(level)} stats):")
        for role in ["TANK", "BRUISER", "ASSASSIN"]:
            fighter = create_fighter_by_level(level, role)
            hp_stat = getattr(fighter, 'hp_stat', 0)
            print(f"  {role:9s}: HP={hp_stat:2d} ATK={fighter.attack:2d} DEF={fighter.defense:2d} AGI={fighter.agility:2d}")
        print()