import random
from collections import defaultdict

from state.fight_state import FightState
from state.fighter_factory import create_fighter_random
from simulation.simulator import simulate_fight


# ============================================================
# CONFIG
# ============================================================

NUM_FIGHTS = 5000


# ============================================================
# BUILD GENERATION
# ============================================================

ROLES = ["ASSASSIN", "BRUISER", "TANK", "SKIRMISHER", "UNIVERSAL"]


def generate_fighter():
    """Generate fighter with automatic role classification based on stats"""
    return create_fighter_random(role=None)  # Auto-classify based on generated stats


def generate_matched_fighters(use_level_system: bool = False, level: int = 9):
    """Generate two fighters with equal stat totals for fair comparison"""
    if use_level_system:
        # Use new level-based system
        from simulation.level_benchmark import generate_level_matched_fighters
        return generate_level_matched_fighters(level)

    # Legacy random generation system
    from state.fighter_factory import create_fighter, classify_build_role
    import random

    # Generate first fighter normally
    hp_a = random.randint(3, 18)
    atk_a = random.randint(3, 18)
    def_a = random.randint(3, 18)
    agi_a = random.randint(3, 18)

    total_stats = hp_a + atk_a + def_a + agi_a

    # Generate second fighter with same total stats
    # Distribute total_stats randomly but ensure each stat is 3-18
    attempts = 0
    while attempts < 100:  # Safety limit
        # Start with minimum values
        hp_b = random.randint(3, min(18, total_stats - 9))  # Leave room for other stats
        remaining = total_stats - hp_b

        atk_b = random.randint(3, min(18, remaining - 6))
        remaining -= atk_b

        def_b = random.randint(3, min(18, remaining - 3))
        remaining -= def_b

        agi_b = remaining

        # Check if agi_b is valid
        if 3 <= agi_b <= 18:
            break

        attempts += 1

    # Fallback to ensure valid stats
    if not (3 <= agi_b <= 18):
        # Use simple balanced distribution as fallback
        quarter = total_stats // 4
        remainder = total_stats % 4
        hp_b = atk_b = def_b = agi_b = quarter
        # Distribute remainder
        if remainder >= 1: hp_b += 1
        if remainder >= 2: atk_b += 1
        if remainder >= 3: def_b += 1

    # Classify roles
    role_a, _ = classify_build_role(hp_a, atk_a, def_a, agi_a)
    role_b, _ = classify_build_role(hp_b, atk_b, def_b, agi_b)

    # Create fighters
    fighter_a = create_fighter(hp_a, atk_a, def_a, agi_a, role_a)
    fighter_b = create_fighter(hp_b, atk_b, def_b, agi_b, role_b)

    return fighter_a, fighter_b


# ============================================================
# METRIC HELPERS
# ============================================================

def compute_winner(state):
    a = state.fighter_a
    b = state.fighter_b

    if a.hp <= 0 and b.hp <= 0:
        return "DRAW_MUTUAL_DEATH"
    if b.hp <= 0:
        return "A"
    if a.hp <= 0:
        return "B"

    # Other types of draws based on end reason
    if state.end_reason == "stamina_exhaustion":
        return "DRAW_STAMINA"
    elif state.end_reason == "max_rounds":
        return "DRAW_TIMEOUT"
    else:
        return "DRAW_OTHER"


def compute_total_damage(telemetry):
    """Calculate total damage from structured events"""
    total = 0.0
    for event in telemetry.events:
        for attack in event.get("attacks", []):
            total += attack["damage"]
    return total


def compute_dps(total_damage, rounds):
    if rounds == 0:
        return 0
    return total_damage / rounds


# ============================================================
# MAIN BENCHMARK
# ============================================================

def run_benchmark(n=NUM_FIGHTS, use_level_system=False, level=9):

    results = defaultdict(int)
    global_mechanics = defaultdict(int)
    global_damage = defaultdict(float)
    global_stamina_distribution = defaultdict(float)

    rounds_list = []
    dps_list = []
    total_damage_list = []

    # Round distribution tracking
    rounds_distribution = defaultdict(int)

    role_a = []
    role_b = []
    role_confidence_a = []
    role_confidence_b = []

    # Role winrate tracking
    role_results = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0})

    # Build tracking (HP, ATK, DEF, AGI stats)
    builds_used = defaultdict(int)

    # Track builds by fight length
    builds_by_rounds = defaultdict(list)  # rounds -> [(build_a, build_b), ...]

    # Track stat total fairness
    stat_total_differences = []

    for i in range(n):
        if i % 1000 == 0:
            print(f"Progress: {i}/{n}")

        # ------------------------
        # generate matched fighters (equal stat totals for fairness)
        # ------------------------
        a, b = generate_matched_fighters(use_level_system, level)

        # Track builds (stat combinations)
        build_a = (getattr(a, 'hp_stat', '?'), a.attack, a.defense, a.agility)
        build_b = (getattr(b, 'hp_stat', '?'), b.attack, b.defense, b.agility)
        builds_used[build_a] += 1
        builds_used[build_b] += 1

        # Track stat total fairness
        total_a = sum(build_a[1:]) if build_a[0] != '?' else sum(build_a[1:]) + (a.hp // 10)
        total_b = sum(build_b[1:]) if build_b[0] != '?' else sum(build_b[1:]) + (b.hp // 10)
        if build_a[0] != '?' and build_b[0] != '?':
            total_a += build_a[0]
            total_b += build_b[0]
        stat_total_differences.append(abs(total_a - total_b))

        state = FightState(
            round_id=0,
            fighter_a=a,
            fighter_b=b
        )

        # ------------------------
        # simulate with deterministic seed
        # ------------------------
        result_state, telemetry = simulate_fight(state, max_rounds=50, seed=i)

        # ------------------------
        # metrics
        # ------------------------
        winner = compute_winner(result_state)
        results[winner] += 1

        rounds = result_state.round_id
        total_damage = compute_total_damage(telemetry)
        dps = compute_dps(total_damage, rounds)

        rounds_list.append(rounds)
        total_damage_list.append(total_damage)
        dps_list.append(dps)

        # Track round distribution
        rounds_distribution[rounds] += 1

        # Track builds by fight length
        builds_by_rounds[rounds].append((build_a, build_b))

        # Get role and confidence for analysis
        from state.fighter_factory import classify_build_role
        role_a_classified, confidence_a = classify_build_role(
            getattr(a, 'hp_stat', a.hp // 10),  # Estimate hp_stat if not available
            a.attack, a.defense, a.agility
        )
        role_b_classified, confidence_b = classify_build_role(
            getattr(b, 'hp_stat', b.hp // 10),  # Estimate hp_stat if not available
            b.attack, b.defense, b.agility
        )

        role_a.append(a.role)
        role_b.append(b.role)
        role_confidence_a.append(confidence_a)
        role_confidence_b.append(confidence_b)

        # Track role winrates
        role_results[a.role]["total"] += 1
        role_results[b.role]["total"] += 1

        if winner == "A":
            role_results[a.role]["wins"] += 1
            role_results[b.role]["losses"] += 1
        elif winner == "B":
            role_results[a.role]["losses"] += 1
            role_results[b.role]["wins"] += 1
        else:  # Draw
            role_results[a.role]["draws"] += 1
            role_results[b.role]["draws"] += 1

        summary = telemetry.summary()
        for k, v in summary["mechanics"].items():
            global_mechanics[k] += v

        for k, v in summary["damage_split"].items():
            global_damage[k] += v

        for k, v in summary["stamina_distribution"].items():
            global_stamina_distribution[k] += v

        if i == 0:
            print("Sample summary:", summary)

    # ============================================================
    # OUTPUT - ORDERED SECTIONS ONLY
    # ============================================================

    print("\n===== BUILD ANALYSIS =====")
    unique_builds = len(builds_used)
    total_fighters = sum(builds_used.values())
    print(f"Unique builds tested: {unique_builds}")
    print(f"Total fighters generated: {total_fighters}")

    # Stat total fairness analysis
    avg_stat_diff = sum(stat_total_differences) / len(stat_total_differences) if stat_total_differences else 0
    max_stat_diff = max(stat_total_differences) if stat_total_differences else 0
    perfect_matches = len([d for d in stat_total_differences if d == 0])
    perfect_percentage = (perfect_matches / len(stat_total_differences)) * 100 if stat_total_differences else 0

    print(f"\nStat Total Fairness:")
    print(f"  Perfect matches (0 difference): {perfect_matches} ({perfect_percentage:.1f}%)")
    print(f"  Average stat total difference: {avg_stat_diff:.1f}")
    print(f"  Maximum stat total difference: {max_stat_diff}")

    # Find shortest and longest fights
    min_rounds = min(rounds_list)
    max_rounds = max(rounds_list)

    print(f"\nBuilds from shortest fights ({min_rounds} rounds):")
    shortest_builds = set()
    for build_a, build_b in builds_by_rounds[min_rounds]:
        shortest_builds.add(build_a)
        shortest_builds.add(build_b)

    for i, build in enumerate(sorted(shortest_builds), 1):
        hp_stat, atk, def_stat, agi = build
        print(f"  {i:2d}. HP={hp_stat}, ATK={atk}, DEF={def_stat}, AGI={agi}")

    print(f"\nBuilds from longest fights ({max_rounds} rounds):")
    longest_builds = set()
    for build_a, build_b in builds_by_rounds[max_rounds]:
        longest_builds.add(build_a)
        longest_builds.add(build_b)

    for i, build in enumerate(sorted(longest_builds), 1):
        hp_stat, atk, def_stat, agi = build
        print(f"  {i:2d}. HP={hp_stat}, ATK={atk}, DEF={def_stat}, AGI={agi}")

    print("\n===== ROLE DISTRIBUTION =====")
    from collections import Counter
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

    print("\n===== ROLE WINRATE ANALYSIS =====")
    # Calculate winrates for each role (wins + half draws)
    role_winrates = {}
    for role, stats in role_results.items():
        if stats["total"] > 0:
            winrate = (stats["wins"] + 0.5 * stats["draws"]) / stats["total"]
            role_winrates[role] = {
                "winrate": winrate,
                "wins": stats["wins"],
                "losses": stats["losses"],
                "draws": stats["draws"],
                "total": stats["total"]
            }

    # Sort roles by winrate (highest first)
    sorted_roles = sorted(role_winrates.items(), key=lambda x: x[1]["winrate"], reverse=True)

    print("Role performance (winrate = wins + 0.5 * draws):")
    for role, data in sorted_roles:
        winrate = data["winrate"] * 100
        wins = data["wins"]
        losses = data["losses"]
        draws = data["draws"]
        total = data["total"]
        print(f"  {role:11s}: {winrate:5.1f}% ({wins:4d}W/{losses:4d}L/{draws:3d}D) from {total:4d} fights")

    print("\n===== ROLE QUALITY ANALYSIS =====")
    all_confidences = role_confidence_a + role_confidence_b
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0

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

    print("\n===== ROUNDS DISTRIBUTION =====")
    avg_rounds = sum(rounds_list) / n
    print(f"Average fight length: {avg_rounds:.1f} rounds")
    print(f"Range: {min(rounds_list)} - {max(rounds_list)} rounds")
    print("\nDetailed distribution:")
    sorted_rounds = sorted(rounds_distribution.items())
    for rounds, count in sorted_rounds:
        percentage = (count / n) * 100
        print(f"  {rounds:2d} rounds: {count:4d} fights ({percentage:5.1f}%)")

    print("\n===== DRAW ANALYSIS =====")
    total_draws = results.get("DRAW_STAMINA", 0) + results.get("DRAW_TIMEOUT", 0) + results.get("DRAW_MUTUAL_DEATH", 0) + results.get("DRAW_OTHER", 0)
    wins_a = results.get("A", 0)
    wins_b = results.get("B", 0)

    print(f"Total fights: {n}")
    print(f"Fighter A wins: {wins_a:4d} ({(wins_a/n)*100:5.1f}%)")
    print(f"Fighter B wins: {wins_b:4d} ({(wins_b/n)*100:5.1f}%)")
    print(f"Total draws: {total_draws:4d} ({(total_draws/n)*100:5.1f}%)")

    if total_draws > 0:
        stamina_draws = results.get("DRAW_STAMINA", 0)
        timeout_draws = results.get("DRAW_TIMEOUT", 0)
        mutual_death = results.get("DRAW_MUTUAL_DEATH", 0)
        other_draws = results.get("DRAW_OTHER", 0)

        print("Draw breakdown:")
        if stamina_draws > 0:
            print(f"  Stamina exhaustion: {stamina_draws:4d} ({(stamina_draws/n)*100:5.1f}%)")
        if timeout_draws > 0:
            print(f"  Timeout (max rounds): {timeout_draws:4d} ({(timeout_draws/n)*100:5.1f}%)")
        if mutual_death > 0:
            print(f"  Mutual death: {mutual_death:4d} ({(mutual_death/n)*100:5.1f}%)")
        if other_draws > 0:
            print(f"  Other: {other_draws:4d} ({(other_draws/n)*100:5.1f}%)")
    else:
        print("No draws occurred")

    print("\n===== DPS VARIANCE =====")
    avg_dps = sum(dps_list) / n
    var_dps = sum((x - avg_dps) ** 2 for x in dps_list) / n
    std_dps = var_dps ** 0.5
    avg_total_damage = sum(total_damage_list) / n

    print(f"Average DPS: {avg_dps:.1f}")
    print(f"DPS Variance: {var_dps:.1f}")
    print(f"DPS Std Dev: {std_dps:.1f}")
    print(f"Average total damage: {avg_total_damage:.1f}")
    print(f"DPS Range: {min(dps_list):.1f} - {max(dps_list):.1f}")

    # =========================
    # RETURN DATA FOR VALIDATION
    # =========================
    avg_total_damage = sum(total_damage_list) / n
    avg_dps_calculated = sum(dps_list) / n

    # Calculate role balance spread for validation
    role_winrates_for_validation = []
    for role, stats in role_results.items():
        if stats["total"] > 0:
            winrate = (stats["wins"] + 0.5 * stats["draws"]) / stats["total"]
            role_winrates_for_validation.append(winrate)

    role_balance_spread = 0.0
    if len(role_winrates_for_validation) >= 2:
        role_balance_spread = max(role_winrates_for_validation) - min(role_winrates_for_validation)

    summary_data = {
        "mechanics": {k: v / n for k, v in global_mechanics.items()},
        "damage_split": {k: v / n for k, v in global_damage.items()},
        "stamina_distribution": {k: v / n for k, v in global_stamina_distribution.items()},
        "avg_total_damage": avg_total_damage,
        "avg_dps": avg_dps_calculated,
        "role_balance_spread": role_balance_spread
    }

    return results, summary_data, rounds_list
