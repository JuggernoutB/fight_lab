#!/usr/bin/env python3
"""Debug script for analyzing critical hit rates"""

import random
from state.level_system import create_fighter_by_level
from core.modules.crit import calc_crit_chance_only

def analyze_crit_rates():
    """Analyze critical hit rates across different build types"""

    # Generate 1000 random fighters at level 5
    fighters = []
    roles = ['TANK', 'ASSASSIN', 'BRUISER', 'SKIRMISHER', 'UNIVERSAL']

    for i in range(1000):
        role = random.choice(roles)
        fighter = create_fighter_by_level(5, role)
        fighters.append({
            'agi': fighter.agility,
            'def': fighter.defense,
            'role': role
        })

    print("🔍 CRITICAL HIT ANALYSIS")
    print("=" * 50)

    # Test all possible matchups
    crit_chances = []
    matchup_details = []

    for i, attacker in enumerate(fighters[:100]):  # Limit to 100 for speed
        for j, defender in enumerate(fighters[:100]):
            if i != j:  # Don't fight yourself
                # Calculate crit chance (stamina=100 for no fatigue penalty)
                crit_chance = calc_crit_chance_only(
                    attacker['agi'],
                    defender['def'],
                    100  # Fresh stamina
                )
                crit_chances.append(crit_chance)

                # Detailed analysis
                agi_diff = attacker['agi'] - defender['def']
                base_crit = 0.08  # 8%
                agi_bonus = max(0, agi_diff * 0.015)  # 1.5% per point

                matchup_details.append({
                    'att_agi': attacker['agi'],
                    'def_def': defender['def'],
                    'agi_diff': agi_diff,
                    'base_crit': base_crit,
                    'agi_bonus': agi_bonus,
                    'total_crit': crit_chance,
                    'att_role': attacker['role'],
                    'def_role': defender['role']
                })

    # Statistics
    avg_crit = sum(crit_chances) / len(crit_chances)
    min_crit = min(crit_chances)
    max_crit = max(crit_chances)

    print(f"Average crit chance: {avg_crit:.3f} ({avg_crit*100:.1f}%)")
    print(f"Min crit chance: {min_crit:.3f} ({min_crit*100:.1f}%)")
    print(f"Max crit chance: {max_crit:.3f} ({max_crit*100:.1f}%)")
    print()

    # Distribution analysis
    print("🎯 CRIT CHANCE DISTRIBUTION:")
    ranges = [(0.0, 0.05), (0.05, 0.08), (0.08, 0.10), (0.10, 0.15), (0.15, 1.0)]
    for min_val, max_val in ranges:
        count = len([c for c in crit_chances if min_val <= c < max_val])
        pct = count / len(crit_chances) * 100
        print(f"  {min_val*100:4.1f}%-{max_val*100:4.1f}%: {count:4d} matchups ({pct:5.1f}%)")

    print()

    # Agility difference analysis
    print("⚡ AGILITY DIFFERENCE ANALYSIS:")
    agi_diffs = [m['agi_diff'] for m in matchup_details]
    avg_agi_diff = sum(agi_diffs) / len(agi_diffs)

    negative_count = len([d for d in agi_diffs if d <= 0])
    positive_count = len([d for d in agi_diffs if d > 0])

    print(f"Average AGI - DEF: {avg_agi_diff:.2f}")
    print(f"Negative/Zero differences: {negative_count} ({negative_count/len(agi_diffs)*100:.1f}%)")
    print(f"Positive differences: {positive_count} ({positive_count/len(agi_diffs)*100:.1f}%)")
    print()

    # Show some examples
    print("📋 EXAMPLE MATCHUPS:")
    sorted_matchups = sorted(matchup_details, key=lambda x: x['total_crit'])

    print("Lowest crit chances:")
    for i in range(min(5, len(sorted_matchups))):
        m = sorted_matchups[i]
        print(f"  AGI {m['att_agi']} vs DEF {m['def_def']} → {m['total_crit']*100:.1f}% crit ({m['att_role']} vs {m['def_role']})")

    print("\nHighest crit chances:")
    for i in range(max(0, len(sorted_matchups)-5), len(sorted_matchups)):
        m = sorted_matchups[i]
        print(f"  AGI {m['att_agi']} vs DEF {m['def_def']} → {m['total_crit']*100:.1f}% crit ({m['att_role']} vs {m['def_role']})")

if __name__ == "__main__":
    analyze_crit_rates()