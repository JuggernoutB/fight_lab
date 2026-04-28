# Skip Protection Mechanism

## Overview

Skip Protection is a **defense-based** defensive mechanic that allows fighters with higher DEFENSE stats to block enemy special attacks (critical hits, dodges, and block breaks). This mechanic directly rewards investment in the DEFENSE stat and creates tactical depth in combat.

## How Skip Protection Works

### Defense Advantage System

Skip Protection is based purely on **DEFENSE stat comparison**:

```
defender_skip_activations = max(0, defender_defense - attacker_defense)
```

**Key Points:**
- Each point of DEFENSE advantage gives **1 skip activation** for the entire fight
- No resource generation or management required
- Activations are calculated once at fight start and consumed as used
- Simple, direct relationship between DEFENSE investment and defensive capability

### Example Calculations

```
Fighter A: DEF=12, Fighter B: DEF=8
→ Fighter A gets max(0, 12-8) = 4 skip activations when defending
→ Fighter B gets max(0, 8-12) = 0 skip activations when defending

Fighter C: DEF=10, Fighter D: DEF=10
→ Both fighters get 0 skip activations (no advantage)
```

## Skip Protection Activation

### Requirements

Skip Protection activates when:

1. **Defense Advantage**: Defender has higher DEFENSE than attacker
2. **Activations Remaining**: Fighter still has unused activations for this fight
3. **Eligible Mechanic**: Enemy attempts crit, dodge, or block break

### Blocked Mechanics

Each activation can block one of these enemy mechanics:
- **Critical Hits**: Enemy crit attempts are converted to normal hits
- **Dodge**: Enemy dodge attempts are converted to normal hits
- **Block Break**: Enemy block break attempts fail

### Activation Consumption

- **Cost per use**: 1 activation consumed per blocked mechanic
- **Fight duration**: Activations last the entire fight (no decay)
- **One mechanic per activation**: Each activation blocks exactly one enemy mechanic
- **No restoration**: Once used, activations are gone for that fight

## Implementation Details

### Combat Flow Integration

Skip Protection is checked during combat resolution in `core/modules/combat.py`:

```python
# Defense-based skip protection system
skip_activations_remaining = defender_skip_activations  # Passed from game engine

# Example: Block enemy crit
if is_crit and skip_activations_remaining > 0:
    is_crit = False  # Block the crit
    skip_events.append("crit_skip")
    skip_activations_remaining -= 1  # Consume one activation
```

### Fight Initialization

Skip activations are calculated once at the start of each fight in `simulation/game_engine.py`:

```python
# Initialize defense-based skip protection activations for the entire fight
a.skip_activations_remaining = max(0, a.defense - b.defense)  # A's advantage over B
b.skip_activations_remaining = max(0, b.defense - a.defense)  # B's advantage over A
```

### Event Logging

Skip events are logged in the combat log:

```python
{
    "type": "skip_protection",
    "defender": "A",          # Who used skip protection
    "attacker": "B",          # Whose mechanic was blocked
    "blocked_mechanic": "crit" # What was blocked (crit/dodge/block_break)
}
```

## Evaluation Metrics

### Primary Metrics

1. **Skip Activations per Fight**
   ```
   avg_skip_per_fight = total_skip_events / total_fights
   ```
   This shows how many defensive mechanics each role blocks on average per fight.

2. **Skip Protection Efficiency**
   ```
   skip_per_round = total_skip_events / total_rounds_fought
   ```
   This shows the rate of skip usage relative to fight duration.

3. **Block Absorption per Fight**
   ```
   avg_block_absorption = total_block_absorbed / total_fights
   ```
   Shows how much damage is mitigated through blocking (separate from skip protection).

4. **Block Absorption per round**
   ```
   avg_block_absorption = total_block_absorbed / total_rounds_fought
   ```
   Block mitigation rate relative to fight duration.

### Benchmark Output Format

```
===== SKIP PROTECTION ANALYSIS =====
Skip Activations per Fight:
  TANK       :  1.30
  SKIRMISHER :  1.50
  UNIVERSAL  :  0.75
  BRUISER    :  0.80
  ASSASSIN   :  0.10

Skip Protection Efficiency:
  TANK       : 0.138
  SKIRMISHER : 0.167
  UNIVERSAL  : 0.085
  BRUISER    : 0.090
  ASSASSIN   : 0.011
```

## Balance Considerations

### Role Effectiveness

The new defense-based system creates clear role differentiation:

- **TANK**: Highest DEFENSE → most skip activations → best against aggressive roles
- **BRUISER**: Medium-high DEFENSE → moderate skip protection → balanced defensive capability
- **UNIVERSAL**: Balanced DEFENSE → some skip activations against lower-defense opponents
- **SKIRMISHER**: Medium DEFENSE but efficient usage due to longer fights
- **ASSASSIN**: Lowest DEFENSE → minimal skip protection → relies on offense

### Design Goals

1. **Direct DEFENSE reward** - Higher DEFENSE immediately provides more defensive options
2. **Simple and predictable** - No complex resource management or timing
3. **Fight-long strategy** - Players must manage finite activations throughout the fight
4. **Clear role identity** - Defensive roles get more defensive tools

### Strategic Implications

- **Investment clarity**: Each DEFENSE point directly translates to defensive capability
- **Build optimization**: High-DEFENSE builds become more viable against offensive builds
- **Counter-play**: Offensive builds can overwhelm defensive ones by forcing multiple activations
- **Role balance**: DEFENSE-focused roles get meaningful advantages without being overpowered

## Configuration Parameters

### Core Settings (`core/config.py`)

The defense-based system requires no special configuration parameters - it uses only the base DEFENSE stats.

**Removed Parameters** (from old resource-based system):
- ~~`damage_absorption_koef`~~ - No resource generation needed
- ~~`absorption_resource_decay`~~ - No resource decay needed
- ~~`absorption_event_threshold`~~ - No threshold needed
- ~~`min_defense_advantage`~~ - Built into the formula

### Tuning Guidelines

To adjust skip protection behavior:

- **Role stat distributions**: Modify DEFENSE ranges in role definitions
- **Level scaling**: Adjust how DEFENSE scales with fighter level
- **Combat mechanics**: Modify which mechanics can be blocked

## Technical Implementation

### File Locations

- **Core logic**: `core/modules/combat.py` - Skip protection checks
- **Fight initialization**: `simulation/game_engine.py` - Activation calculation
- **Metrics tracking**: `simulation/level_benchmark.py` - Performance analysis
- **Fighter state**: `state/fight_state.py` - Skip activations storage

### Integration Points

1. **Fight Start**: Calculate skip activations based on DEFENSE difference
2. **Combat Resolution**: Check and consume activations for each mechanic
3. **Event Logging**: Track which mechanics were blocked
4. **Metrics**: Aggregate skip usage across roles and fights

---

**Note**: This defense-based system replaced the previous resource-based system, providing a simpler and more direct relationship between DEFENSE investment and defensive capability. The new system eliminates complex resource management while maintaining tactical depth through finite activation management.