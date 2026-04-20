# Skip Protection Mechanism

## Overview

Skip Protection is a defensive mechanic that allows fighters with sufficient absorption resource and defense advantage to block enemy special attacks (critical hits, dodges, and block breaks). This mechanic rewards defensive playstyles and creates tactical depth in combat.

## How Absorption Resource is Calculated

### Resource Generation

Absorption resource is generated **only from blocked damage** (dodge damage does not generate resource):

```
if def_defense > opponent_defense:
    effective_absorbed = blocked_damage * absorption_efficiency
    damage_to_resource = (effective_absorbed / opponent_max_hp) * damage_absorption_koef
    absorption_resource = min(1.0, current_resource + damage_to_resource)
```

### Key Parameters

- **`damage_absorption_koef`**: 20.0 (conversion factor)
- **`absorption_efficiency`**: Based on defender's DEF stat
- **`absorption_resource_decay`**: 0.85 (15% resource lost per round)
- **Max resource**: 1.0 (100%)

### Absorption Efficiency Formula

```python
def calculate_absorption_efficiency(defense_stat):
    # Higher defense = better absorption efficiency
    return base_efficiency + (defense_stat * scaling_factor)
```

Fighters with higher DEF stats convert blocked damage to absorption resource more efficiently.

## Skip Protection Activation

### Requirements

Skip Protection activates when **both conditions** are met:

1. **Resource Threshold**: `absorption_resource >= absorption_event_threshold` (0.4)
2. **Defense Advantage**: `defender_defense >= opponent_defense + min_defense_advantage` (1)

### Blocked Mechanics

When Skip Protection is active, it can block:
- **Critical Hits**: Enemy crit attempts are converted to normal hits
- **Dodge**: Enemy dodge attempts are converted to normal hits
- **Block Break**: Enemy block break attempts fail

### Resource Consumption

- **Cost per activation**: 0.4 absorption resource (same as threshold)
- **Multiple uses**: Can activate multiple times per fight as resource regenerates
- **One mechanic per activation**: Each activation blocks one enemy mechanic

## Implementation Details

### Combat Flow Integration

Skip Protection is checked during combat resolution in `core/modules/combat.py`:

```python
# Check if defender has skip protection active
defender_has_skip = (defender_absorption_resource >= config["absorption_event_threshold"])

# Example: Block enemy crit
if is_crit and defender_has_skip and "crit_skip" not in skip_events:
    is_crit = False  # Block the crit
    skip_events["crit_skip"] = True
    defender_absorption_resource -= config["absorption_event_threshold"]
```

### Event Logging

Skip events are logged in the combat log:

```python
{
    "type": "skip_protection",
    "defender": "A",          # Who used skip protection
    "attacker": "B",          # Whose mechanic was blocked
    "blocked_mechanic": "crit" # What was blocked
}
```

## Evaluation Metrics

### Primary Metrics

1. **Blocks per Fight**
   ```
   blocks_per_fight = total_block_events / total_fights
   ```

2. **Blocks per round**
   ```
   blocks_per_round = total_block_events / total_rounds_fought
   ```


3. **Block Absorption per Fight**
   ```
   avg_block_absorption = total_block_absorbed / total_fights
   ```

4. **Block Absorption per round**
   ```
   avg_block_absorption = total_block_absorbed / total_rounds_fought
   ```

5. **Skip Activations per Fight**
   ```
   avg_skip_per_fight = total_skip_events / total_fights
   ```

6. **Skip Protection Efficiency (NEW)**
   ```
   skip_per_round = total_skip_events / total_rounds_fought
   ```

### Benchmark Output Format

```
Skip protection activation rate by role:
  SKIRMISHER : 0.75 avg skip per fight, 0.081 skip per round (85 total events)
  TANK       : 0.74 avg skip per fight, 0.075 skip per round (187 total events)

Skip protection efficiency analysis:
  SKIRMISHER : 0.081 skip/round,   9.2 avg rounds/fight
  TANK       : 0.075 skip/round,   9.9 avg rounds/fight
```

### Metric Calculation Details

#### Skip Per Round Calculation
```python
# Track total rounds per role
results["role_absorption"][role]["total_rounds"] += fight_rounds

# Calculate efficiency
skip_per_round = total_skip_events / total_rounds if total_rounds > 0 else 0
```

#### Skip Event Distribution by Round
```python
# Track when skip events occur during fights
skip_protection_by_round = {
    round_number: event_count
}
```

## Balance Considerations

### Role Effectiveness

- **TANK**: Highest defense → best against most opponents
- **BRUISER**: Medium defense → effective against weaker roles
- **SKIRMISHER**: Lower defense but high efficiency per round
- **ASSASSIN**: Lowest defense → minimal skip protection usage

### Design Goals

1. **Reward defensive investment** (DEF stat importance)
2. **Create tactical depth** (resource management)
3. **Balance offense vs defense** (skip protection vs damage output)
4. **Provide counterplay** (not all roles can use it effectively)

## Configuration Parameters

### Core Settings (`core/config.py`)

```python
"damage_absorption_koef": 20.0,           # Damage to resource conversion
"absorption_resource_decay": 0.85,        # Resource decay per round
"absorption_event_threshold": 0.4,        # Minimum resource for activation
"min_defense_advantage": 1,               # Required defense advantage
```

### Tuning Guidelines

- **Increase `damage_absorption_koef`**: More resource generation
- **Decrease `absorption_resource_decay`**: Longer resource retention
- **Lower `absorption_event_threshold`**: More frequent activations
- **Adjust `min_defense_advantage`**: Change who can use skip protection

## Technical Implementation

### File Locations

- **Core logic**: `core/modules/combat.py`
- **Resource calculation**: `simulation/game_engine.py`
- **Metrics tracking**: `simulation/level_benchmark.py`
- **Event logging**: `telemetry/telemetry.py`

### Integration Points

1. **Combat Resolution**: Skip checks during attack processing
2. **Resource Management**: Accumulation and decay each round
3. **Telemetry**: Event tracking for analysis
4. **Benchmarking**: Performance metrics calculation

---

**Note**: This mechanic replaced the previous stamina transfer system, providing a cleaner and more balanced defensive option focused on blocking enemy special attacks rather than direct stat manipulation.