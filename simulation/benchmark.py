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

ROLES = ["ASSASSIN", "BRUISER", "TANK", "SKIRMISHER"]


def generate_fighter():
    """Generate fighter with proper stat-based system"""
    role = random.choice(ROLES)
    return create_fighter_random(role)


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

def run_benchmark(n=NUM_FIGHTS):

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

    # Build tracking (HP, ATK, DEF, AGI stats)
    builds_used = defaultdict(int)

    # Track builds by fight length
    builds_by_rounds = defaultdict(list)  # rounds -> [(build_a, build_b), ...]

    for i in range(n):
        if i % 1000 == 0:
            print(f"Progress: {i}/{n}")

        # ------------------------
        # generate fighters
        # ------------------------
        a = generate_fighter()
        b = generate_fighter()

        # Track builds (stat combinations)
        build_a = (getattr(a, 'hp_stat', '?'), a.attack, a.defense, a.agility)
        build_b = (getattr(b, 'hp_stat', '?'), b.attack, b.defense, b.agility)
        builds_used[build_a] += 1
        builds_used[build_b] += 1

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

        role_a.append(a.role)
        role_b.append(b.role)

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

    summary_data = {
        "mechanics": {k: v / n for k, v in global_mechanics.items()},
        "damage_split": {k: v / n for k, v in global_damage.items()},
        "stamina_distribution": {k: v / n for k, v in global_stamina_distribution.items()},
        "avg_total_damage": avg_total_damage,
        "avg_dps": avg_dps_calculated
    }

    return results, summary_data, rounds_list
