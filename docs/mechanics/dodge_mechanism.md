# Dodge Mechanism

## Overview
The dodge mechanism allows defenders to completely avoid incoming attacks, resulting in zero damage. Dodge effectiveness primarily depends on the agility difference between attacker and defender, modified by fatigue.

## Core Mechanics

### Dodge Calculation
The dodge system uses agility comparison for determining dodge chance:

```
# Modern approach (agility vs agility)
agi_diff = defender_agility - attacker_agility
agi_bonus = max(0, agi_diff) * agi_diff_dodge_scale
base_chance = base_dodge_chance + agi_bonus

# Fallback approach (agility vs attack)
agi_bonus = max(0, defender_agility - attacker_attack) * agi_diff_dodge_scale
base_chance = base_dodge_chance + agi_bonus

effective_chance = base_chance * fatigue_multiplier
```

### Parameters (from CONFIG)
- `base_dodge_chance`: 0.1 (10% base dodge chance)
- `agi_diff_dodge_scale`: 0.05 (5% per agility advantage)
- `min_dodge_chance`: 0.05 (5% minimum chance)
- `max_dodge_chance`: 0.55 (55% maximum chance)

### Fatigue Effects
Dodge effectiveness is affected by defender's stamina:
- **Fresh** (≥70 stamina): 100% effectiveness
- **Tired** (25-69 stamina): 70% effectiveness
- **Exhausted** (<25 stamina): 40% effectiveness

## Dodge Outcomes

### Full Dodge
When dodge succeeds:
- **Damage dealt**: 0.0
- **Event type**: "dodge" or "crit_dodge" (if crit was rolled)
- **Result**: Complete attack negation

### No Dodge
When dodge fails:
- **Damage dealt**: Full calculated damage
- **Event type**: "hit", "crit", "block", etc.
- **Result**: Normal damage resolution

## Legacy vs Modern System

### Historical Changes
The system has evolved from a complex glance/dodge system to a simplified binary outcome:

#### Old System (Deprecated)
- Partial dodges ("glance") with reduced damage
- Complex damage ratio calculations
- Multiple dodge outcome types

#### Current System
- Binary outcome: full dodge (0 damage) or full hit
- Simplified logic for better balance
- Combined old dodge + glance chances into single dodge chance

## Analytics & Metrics

### Telemetry Tracking
The system tracks dodge-related events in telemetry:

#### Event Counters
- `dodge`: Successful full dodges
- `crit_dodge`: Critical hits that were dodged
- `hit`: Attacks that were not dodged

#### Damage Absorption
- `damage_absorbed["dodge"]`: Total damage prevented by dodging

### Key Metrics

#### Dodge Frequency Analysis
- **Dodge Rate**: `dodges / total_attacks`
- **Effective Dodge Rate**: Dodge rate accounting for fatigue states
- **Agility Advantage Impact**: Correlation between agility difference and dodge success

#### Crit Interaction Analysis
- **Crit Dodge Rate**: Rate of critical hits being dodged
- **Crit vs Regular Dodge**: Comparison of dodge rates for different attack types

#### Stamina Correlation
- **Dodge by Stamina State**: Dodge rates in fresh/tired/exhausted states
- **Stamina Cost**: Stamina consumption for successful dodges (3 points per CONFIG)

### Role-Based Dodge Analysis
Different fighter roles show varying dodge patterns:
- **ASSASSIN**: Typically high agility, high dodge rates
- **SKIRMISHER**: Moderate agility, situational dodging
- **TANK**: Low agility, relies more on blocking than dodging
- **BRUISER**: Balanced approach to avoidance
- **UNIVERSAL**: Variable dodge performance

## Implementation Details

### Code Location
- Main logic: `/core/modules/dodge.py`
- Configuration: `/core/config.py` (DODGE section)
- Telemetry: `/telemetry/telemetry.py`

### Function Signatures
```python
def apply_dodge(
    dmg: float,
    atk_attack: int,
    def_agility: int,
    defender_stamina: int,
    atk_agility: int = None
) -> Tuple[float, str]
```

### Return Values
- `(0.0, "dodge")`: Successful dodge, no damage
- `(original_damage, "hit")`: No dodge, full damage

## Balance Considerations

### Design Goals
- Agility should provide meaningful avoidance without being overpowered
- High-agility fighters should be evasive but not untouchable
- Fatigue should create meaningful stamina management
- Dodge should be predictable enough for tactical planning

### Interaction with Other Mechanics
- **vs Blocking**: Dodge prevents all damage, block reduces damage
- **vs Critical Hits**: Critical hits can be dodged (crit_dodge events)
- **vs Skip Protection**: Dodge happens before skip protection checks
- **vs Fatigue**: Heavy fatigue makes dodging much less reliable

### Tuning Parameters
Key parameters for balance adjustments:
- `base_dodge_chance`: Controls baseline evasiveness
- `agi_diff_dodge_scale`: Controls how much agility advantage matters
- `max_dodge_chance`: Prevents excessive dodge rates
- `min_dodge_chance`: Ensures some baseline dodge chance

## Strategic Implications

### For High-Agility Builds
- Prioritize maintaining stamina for consistent dodging
- Use agility advantage to avoid high-damage attacks
- Balance between offense and evasion

### For Low-Agility Builds
- Rely more on blocking and absorption mechanics
- Focus on stamina efficiency over pure avoidance
- Use defense-based skip protection as alternative

### Counterplay Options
- High attack stats can partially offset agility disadvantage (fallback mode)
- Fatigue management can reduce opponent's dodge effectiveness
- Multiple attack zones can increase hit probability