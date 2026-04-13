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
        }
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
        "role_analysis": role_results
    }


def print_level_benchmark_results(results: Dict):
    """Print formatted benchmark results"""
    level = results["level_info"]["level"]
    stat_budget = results["level_info"]["stat_budget"]
    summary = results["summary"]

    print(f"\n📊 LEVEL {level} RESULTS ({stat_budget} stat points)")
    print("=" * 50)

    # Fight outcomes
    total = summary["total_fights"]
    winners = summary["winners"]

    print("🏆 FIGHT OUTCOMES:")
    print(f"  Fighter A wins: {winners['A']:4d} ({winners['A']/total*100:.1f}%)")
    print(f"  Fighter B wins: {winners['B']:4d} ({winners['B']/total*100:.1f}%)")
    print(f"  Draws:          {winners['DRAW_TIMEOUT'] + winners['DRAW_MUTUAL_DEATH']:4d} ({(winners['DRAW_TIMEOUT'] + winners['DRAW_MUTUAL_DEATH'])/total*100:.1f}%)")

    # Round stats
    print(f"\n⚔️ FIGHT LENGTH:")
    print(f"  Average: {summary['avg_rounds']:.1f} rounds")
    print(f"  Range: {summary['min_rounds']}-{summary['max_rounds']} rounds")

    # Role analysis
    print(f"\n🎭 ROLE PERFORMANCE:")
    role_analysis = results["role_analysis"]
    sorted_roles = sorted(role_analysis.items(), key=lambda x: x[1]["winrate"], reverse=True)

    for role, stats in sorted_roles:
        print(f"  {role:11s}: {stats['winrate']*100:5.1f}% ({stats['wins']}W/{stats['losses']}L/{stats['draws']}D) from {stats['fights']} fights")

    # Balance check
    if len(sorted_roles) >= 2:
        best_role = sorted_roles[0][1]["winrate"]
        worst_role = sorted_roles[-1][1]["winrate"]
        spread = best_role - worst_role

        print(f"\n📈 BALANCE:")
        print(f"  Role spread: {spread*100:.1f}% ({'✅ Good' if spread < 0.15 else '❌ Imbalanced'})")


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