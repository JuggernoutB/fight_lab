# Block Mechanism

## Overview
The block mechanism provides damage reduction when defenders successfully block incoming attacks. The effectiveness of blocking depends on the defender's defense stat compared to the attacker's attack stat, modified by fatigue.

## Core Mechanics

### Block Damage Reduction
When a block occurs, the system calculates damage reduction based on:

```
base_reduction = base_block_reduction + (defense - attack) * def_diff_block_scale
effective_reduction = base_reduction * fatigue_multiplier
reduced_damage = original_damage * (1 - effective_reduction)
```

### Parameters (from CONFIG)
- `base_block_reduction`: 0.26 (26% base damage reduction)
- `def_diff_block_scale`: 0.055 (5.5% per defense advantage)
- `min_block_reduction`: 0.1 (10% minimum reduction)
- `max_block_reduction`: 0.7 (70% maximum reduction)

### Fatigue Effects
Block effectiveness is affected by defender's stamina:
- **Fresh** (≥70 stamina): 100% effectiveness
- **Tired** (25-69 stamina): 70% effectiveness
- **Exhausted** (<25 stamina): 40% effectiveness

## Block Break Mechanism

### Overview
Attackers can attempt to break through blocks using agility. Block break allows dealing partial damage despite a block.

### Calculation
```
base_chance = base_block_break_chance + (agility - defense) * agi_block_break_scale
effective_chance = base_chance * fatigue_multiplier + fatigue_bonus
```

### Parameters
- `base_block_break_chance`: 0.2 (20% base chance)
- `agi_block_break_scale`: 0.1 (10% per agility advantage)
- `min_block_break_chance`: 0.05 (5% minimum)
- `max_block_break_chance`: 0.7 (70% maximum)
- `block_break_damage_ratio`: 0.85 (85% damage on break)

### Fatigue Effects
Block break chance is affected by attacker's stamina using the same fatigue system.

## Analytics & Metrics

### Telemetry Tracking
The system tracks block-related events in telemetry:

#### Event Counters
- `block`: Successful blocks (damage reduced)
- `block_break`: Successful block breaks (partial damage)
- `crit_block`: Critical hits that were blocked
- `crit_block_break`: Critical hits that broke through blocks

#### Damage Categories
- `blocked`: Total damage dealt through blocks (both regular and broken)

### Key Metrics

#### Block Frequency Analysis
- **Block Rate**: `blocks / total_attacks`
- **Block Break Rate**: `block_breaks / total_blocks`
- **Block Effectiveness**: Average damage reduction per block

#### Role-Based Block Analysis
The system tracks block performance by fighter role:
- **Blocks per Fight**: Average blocks per role per fight
- **Blocks per Round**: Average blocks per role per round
- **Block Damage Mitigation**: Damage prevented by blocks per fight/round
- **Block Protection Efficiency**: Effectiveness of block-based damage mitigation

#### Balance Validation
Block mechanics are validated against expected ranges:
- **Block frequency** should be within acceptable range for game balance
- **Block break frequency** prevents blocks from being overpowered
- **Damage distribution** tracks blocked damage vs other damage types

## Implementation Details

### Code Location
- Main logic: `/core/modules/block.py`
- Configuration: `/core/config.py` (BLOCKING section)
- Telemetry: `/telemetry/telemetry.py`

### Function Signatures
```python
def apply_block(dmg: float, atk: int, defense: int, defender_stamina: int) -> float
def block_break(agility: int, defense: int, attacker_stamina: int, attacker_fatigue_bonus: float = 0.0) -> bool
```

## Balance Considerations

### Design Goals
- Blocks should provide meaningful damage reduction without making fights too long
- Defense stat should be valuable but not overpowered
- Agility should provide counterplay through block breaks
- Fatigue should create meaningful stamina management decisions

### Tuning Parameters
Key parameters for balance adjustments:
- `base_block_reduction`: Controls base block strength
- `def_diff_block_scale`: Controls how much defense advantage matters
- `agi_block_break_scale`: Controls agility's block break effectiveness
- `block_break_damage_ratio`: Controls partial damage on block break