# Critical Hit Mechanism

## Overview
The critical hit mechanism allows attackers to deal amplified damage when they land critical strikes. Critical hit chance is primarily determined by the attacker's agility compared to the defender's defense, modified by fatigue and fatigue bonuses.

## Core Mechanics

### Critical Hit Chance Calculation
The system calculates critical hit probability using:

```
base_chance = base_crit_chance + max(0, (attacker_agility - defender_defense) * agi_diff_crit_scale)
effective_chance = base_chance * fatigue_multiplier + fatigue_bonus
crit_success = random.random() < effective_chance
```

### Parameters (from CONFIG)
- `base_crit_chance`: 0.1 (10% base critical chance)
- `agi_diff_crit_scale`: 0.02 (2% per agility advantage over defense)
- `crit_damage_multiplier`: 1.4 (140% damage multiplier)
- `min_crit_chance`: 0.005 (0.5% minimum chance)
- `max_crit_chance`: 0.3 (30% maximum chance)

### Fatigue Effects
Critical hit chance is affected by attacker's stamina:
- **Fresh** (≥70 stamina): 100% effectiveness
- **Tired** (25-69 stamina): 70% effectiveness
- **Exhausted** (<25 stamina): 40% effectiveness

### Fatigue Bonuses
Additional bonuses can be applied:
- **Fatigue bonus**: Flat percentage added to final critical chance
- **Action-based bonuses**: Situational modifiers from special abilities

## Critical Hit Outcomes

### Damage Calculation
When a critical hit occurs:
```
critical_damage = base_damage * crit_damage_multiplier
final_damage = critical_damage * (1.4 = 140% damage)
```

### Event Types
Critical hits create specific telemetry events:
- `crit`: Standard critical hit
- `crit_block`: Critical hit that was blocked (reduced damage)
- `crit_block_break`: Critical hit that broke through block (partial damage)

## Advanced Critical Analysis

### Dual Rate Tracking
The system tracks two distinct critical hit rates:

#### Raw Critical Rate
- **Definition**: Percentage of attack rolls that result in critical success
- **Calculation**: `crit_rolls / total_rolls`
- **Purpose**: Measures the underlying critical hit mechanics

#### Effective Critical Rate
- **Definition**: Percentage of successful hits that are critical
- **Calculation**: `crit_hits / successful_hits`
- **Purpose**: Measures practical critical hit impact (excludes dodged crits)

### Critical Damage Ratio
- **Definition**: Percentage of total fight damage from critical hits
- **Calculation**: `crit_damage / total_damage`
- **Purpose**: Measures critical hits' contribution to overall damage output

## Analytics & Metrics

### Telemetry Tracking
The system comprehensively tracks critical hit statistics:

#### Enhanced Crit Statistics
```python
crit_stats = {
    "total_rolls": 0,      # Total times crit was checked
    "crit_rolls": 0,       # Times crit succeeded (raw crit rate)
    "successful_hits": 0,  # Hits that dealt damage (for effective rate)
    "crit_hits": 0,        # Crits that dealt damage
}
```

#### Event Processing
- **Non-blocked attacks**: All attacks except pure blocks check for critical hits
- **Dodged attacks**: Critical status is tracked even when dodged (`crit_rolled` field)
- **Blocked attacks**: Critical hits can still occur and break through blocks

### Key Metrics

#### Critical Hit Performance
- **Raw Crit Rate**: Base mechanical critical chance
- **Effective Crit Rate**: Practical critical hit rate in actual combat
- **Crit Damage Ratio**: Critical hits' share of total damage output
- **Crit vs Defense**: Correlation between agility-defense difference and crit rate

#### Role-Based Critical Analysis
Different roles show varying critical patterns:
- **ASSASSIN**: High agility, high crit rates, burst damage focus
- **SKIRMISHER**: Moderate crit rates, mobility-based crits
- **BRUISER**: Balanced crit rates, sustained damage
- **TANK**: Lower crit rates, defensive focus
- **UNIVERSAL**: Variable critical performance

#### Stamina Interaction
- **Crit by Stamina State**: Critical rates across fresh/tired/exhausted states
- **Stamina Cost**: Stamina consumption for critical hits (3 points per CONFIG)
- **Fatigue Impact**: How fatigue affects critical reliability

## Implementation Details

### Code Location
- Main logic: `/core/modules/crit.py`
- Configuration: `/core/config.py` (CRITICAL HITS section)
- Telemetry: `/telemetry/telemetry.py`

### Function Signatures
```python
def calc_crit(
    att_agi: int,
    def_def: int,
    attacker_stamina: int,
    attacker_fatigue_bonus: float = 0.0
) -> bool

def calc_crit_chance_only(
    att_agi: int,
    def_def: int,
    attacker_stamina: int
) -> float
```

### Legacy Support
- `calc_crit_chance_only`: Backward compatibility function for chance-only calculations
- Maintains compatibility with older analysis code

## Balance Considerations

### Design Goals
- Critical hits should provide exciting damage spikes without being overpowered
- Agility should be valuable for critical chance without making defense worthless
- Fatigue should create meaningful stamina management decisions
- Critical hits should reward tactical positioning and timing

### Interaction with Other Mechanics
- **vs Dodging**: Critical hits can be completely negated by dodging
- **vs Blocking**: Critical hits can break through blocks more easily
- **vs Skip Protection**: Critical hits occur before skip protection checks
- **vs Zone Targeting**: Critical hits apply to all targeted zones

### Tuning Parameters
Key parameters for balance adjustments:
- `base_crit_chance`: Controls baseline critical frequency
- `agi_diff_crit_scale`: Controls how much agility advantage matters
- `crit_damage_multiplier`: Controls critical hit damage impact
- `max_crit_chance`: Prevents excessive critical rates

### Balance Validation Targets
The system validates critical hit balance:
- **Critical frequency**: Should be high enough to be impactful, low enough to be special
- **Damage distribution**: Critical damage should be meaningful but not dominant
- **Role balance**: All roles should have viable critical hit strategies

## Strategic Implications

### For High-Agility Attackers
- Focus on maintaining stamina for consistent critical chances
- Target opponents with lower defense for maximum critical rate
- Time attacks for optimal critical hit opportunities

### For High-Defense Defenders
- Use defense stat to reduce incoming critical rates
- Force attackers into fatigue to reduce their critical effectiveness
- Prioritize blocking to mitigate critical hit damage

### Tactical Considerations
- **Multi-zone attacks**: Spread critical chance across multiple zones
- **Fatigue management**: Balance offensive pressure with stamina conservation
- **Target selection**: Prioritize low-defense targets for critical hits