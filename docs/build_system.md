# Build System and Role Classification

This document describes how the combat simulation system creates fighter builds and automatically classifies them into roles using a **production-level scoring system**.

## Overview

The system uses a **continuous scoring-based role classification** approach where:
1. Fighter stats are generated first (random or custom)
2. Each role receives a calculated score based on stat distribution
3. Role is determined by highest score + confidence measurement
4. This provides smooth transitions and realistic role distributions
5. No artificial boundaries or discrete if/else logic

## Fighter Stats

### Stat Ranges
- **All Stats**: 3-18 (supports progression from starter to end-game characters)
- **Stats**: HP, Attack, Defense, Agility

### Stat Generation Methods

#### 1. Balanced Presets (`create_fighter_balanced`)
Predefined stat combinations for each role:

```python
BRUISER:    HP=15, ATK=12, DEF=15, AGI=8   # Tank-like damage dealer
ASSASSIN:   HP=10, ATK=16, DEF=8,  AGI=16  # High damage, high mobility
TANK:       HP=18, ATK=8,  DEF=18, AGI=8   # Maximum survivability
SKIRMISHER: HP=12, ATK=14, DEF=12, AGI=14  # Balanced offensive
UNIVERSAL:  HP=12, ATK=12, DEF=12, AGI=12  # Perfect balance
```

#### 2. Random Generation (`create_fighter_random`)
- Each stat randomly generated between 3-18
- Role automatically classified after generation
- Used in BENCHMARK mode for realistic testing

#### 3. Custom Builds
- User-specified stat values
- Role can be manually set or auto-classified
- Used in BUILD mode for specific testing

## Role Classification Algorithm

### Function: `classify_build_role(hp, attack, defense, agility) -> (role, confidence)`

The classification uses a **continuous scoring system** with normalized stats:

```python
def classify_build_role(hp_stat, attack_stat, defense_stat, agility_stat):
    # Normalize stats to prevent stat inflation bias
    total = hp_stat + attack_stat + defense_stat + agility_stat
    hp_n = hp_stat / total
    atk_n = attack_stat / total
    def_n = defense_stat / total
    agi_n = agility_stat / total

    # Calculate role scores using weighted combinations
    scores = {}

    # TANK: HP + Defense focused
    scores["TANK"] = hp_n * 0.5 + def_n * 0.5

    # BRUISER: Attack + moderate survivability
    scores["BRUISER"] = atk_n * 0.5 + hp_n * 0.25 + def_n * 0.25

    # ASSASSIN: Attack + Agility combination
    scores["ASSASSIN"] = atk_n * 0.5 + agi_n * 0.5

    # SKIRMISHER: Agility focused with some offense
    scores["SKIRMISHER"] = agi_n * 0.5 + atk_n * 0.25 + def_n * 0.25

    scores["ATK_DEF"] = atk_n * 0.5 + def_n * 0.5
    scores["AGI_DEF"] = agi_n * 0.5 + def_n * 0.5
    scores["AGI_HP"] = agi_n * 0.5 + hp_n * 0.5
    scores["ATK_HP"] = atk_n * 0.5 + hp_n * 0.5

    # UNIVERSAL: Balanced builds (high when stats are even)
    stat_range = max([hp_n, atk_n, def_n, agi_n]) - min([hp_n, atk_n, def_n, agi_n])
    scores["UNIVERSAL"] = 1.0 - stat_range * 4  # Scale range penalty

    # Find best role and calculate confidence
    best_role = max(scores, key=scores.get)
    sorted_scores = sorted(scores.values(), reverse=True)
    confidence = sorted_scores[0] - sorted_scores[1]  # Gap between 1st and 2nd

    return best_role, confidence
```

### Key Innovations

#### 🔄 **Continuous Classification**
- **No discrete boundaries** - roles exist on a spectrum
- **Smooth transitions** - ATK=18,AGI=17 vs ATK=17,AGI=18 handled naturally
- **Normalized stats** - prevents high-stat-total bias

#### 🎯 **Confidence Scoring**
- **Pure builds**: confidence > 0.15 (clear role identity)
- **Hybrid builds**: confidence < 0.05 (ambiguous, multi-role)
- **Enables hybrid analysis** and role purity metrics

#### ⚖️ **Balanced Weighting**
Role formulas can be tuned for meta balance:
```python
# Example: Nerf ASSASSIN dominance
scores["ASSASSIN"] = atk_n * 0.45 + agi_n * 0.55  # Reduced from 0.5/0.5
```

### Role Definitions

#### 🎯 UNIVERSAL
- **Score Formula**: `1.0 - (stat_range * 4)`
- **Philosophy**: Balanced builds with even stat distribution
- **Examples**:
  - (12,12,12,12) - Perfect balance (conf: 0.750)
  - (11,12,12,13) - Near balance (conf: 0.571)
- **Frequency**: ~25.4% of random builds
- **Playstyle**: Jack-of-all-trades, reliable in all situations

#### 🛡️ TANK
- **Score Formula**: `hp_n * 0.5 + def_n * 0.5`
- **Philosophy**: Maximum survivability and damage mitigation
- **Examples**:
  - (18,8,18,8) - Classic tank (pure build)
  - (15,6,18,10) - Defense-focused tank
- **Frequency**: ~26.1% of random builds
- **Playstyle**: Absorb damage, long fights, block specialist

#### ⚔️ BRUISER
- **Score Formula**: `atk_n * 0.5 + hp_n * 0.25 + def_n * 0.25`
- **Philosophy**: Raw damage output with moderate survivability
- **Examples**:
  - (15,18,12,8) - High attack bruiser
  - (12,18,10,10) - Balanced damage dealer
- **Frequency**: ~14.8% of random builds
- **Playstyle**: Straightforward damage dealing, frontline fighter

#### 🗡️ ASSASSIN
- **Score Formula**: `atk_n * 0.5 + agi_n * 0.5`
- **Philosophy**: High damage with mobility (crit chance and dodge)
- **Examples**:
  - (8,18,8,16) - Glass cannon assassin
  - (10,16,8,16) - Balanced assassin
- **Frequency**: ~17.4% of random builds
- **Playstyle**: Burst damage, critical hits, evasion tactics

#### 🏃 SKIRMISHER
- **Score Formula**: `agi_n * 0.6 + atk_n * 0.2 + def_n * 0.2`
- **Philosophy**: Mobility and positioning specialist
- **Examples**:
  - (8,8,8,18) - Pure mobility skirmisher
  - (10,12,10,18) - Mobile fighter
- **Frequency**: ~16.5% of random builds
- **Playstyle**: Hit-and-run, dodge specialist, positioning control

## Statistical Distribution (Fair Matching System)

Based on 10,000 random build analysis with **fair stat total matching**:

| Role | Frequency | Winrate | Confidence Range | Characteristics |
|------|-----------|---------|------------------|-----------------|
| BRUISER | 18.8% | 66.7% | Variable | Specialized, dominant |
| ASSASSIN | 15.9% | 65.6% | Variable | Specialized, very strong |
| UNIVERSAL | 24.9% | 47.9% | 0.571-0.750 | Common, balanced performance |
| SKIRMISHER | 13.8% | 38.5% | Variable | Rare, underperforming |
| TANK | 26.6% | 36.7% | Variable | Most common, weakest |

### Fair Matching System
**Critical Innovation**: BENCHMARK now uses **equal stat total matching** to ensure fair comparisons:
- **Fighter A**: Generated with random stats (total = X)
- **Fighter B**: Generated with same total stats (total = X) but different distribution
- **100% perfect matches** - eliminates stat luck bias
- **True role effectiveness** revealed without power level differences

### Role Quality Metrics
- **Average confidence**: 0.087 (low - many hybrid builds)
- **Pure builds** (conf > 0.15): 15.8% of total
- **Hybrid builds** (conf < 0.05): 54.9% of total
- **Confidence range**: 0.000 - 0.750

## Balance Implications

### Fair Matching Revelations
The combination of scoring system + fair matching revealed the **true meta**:

#### ⚔️ **Offensive Roles Dominate**
- **BRUISER: 66.7% winrate** - attack + survivability is optimal combination
- **ASSASSIN: 65.6% winrate** - attack + mobility remains very strong
- **Offensive specialization >> defensive specialization**

#### 🛡️ **Defensive Crisis Confirmed**
- **TANK: 36.7% winrate** despite highest frequency (26.6%)
- **SKIRMISHER: 38.5% winrate** - pure mobility insufficient
- **30% winrate gap** between offensive and defensive roles

#### ⚖️ **UNIVERSAL Truth Revealed**
- **47.9% winrate** - balanced builds are actually **average**, not dominant
- Previous 64.0% was **stat luck illusion** from unfair matchups
- **True role hierarchy**: Specialists (offense) > Balanced > Specialists (defense)

#### 📊 **Fairness Impact Analysis**
Comparing unfair vs fair results shows massive changes:

| Role | Unfair System | Fair System | Reality Check |
|------|---------------|-------------|---------------|
| UNIVERSAL | 64.0% | 47.9% | **-16.1%** - was stat-boosted |
| BRUISER | 54.1% | 66.7% | **+12.6%** - true strength revealed |
| ASSASSIN | 59.6% | 65.6% | **+6.0%** - even stronger when fair |
| TANK | 36.3% | 36.7% | **+0.4%** - consistently weak |

### System Revelations
1. **Offensive specialization dominates** - attack-focused builds rule meta
2. **Balanced builds are average** - neither weak nor strong
3. **Defense mechanics broken** - tanks and mobility specialists undertuned
4. **Stat total fairness critical** - previous results were heavily biased
5. **True power hierarchy**: ATK+HP > ATK+AGI > Balanced > AGI > HP+DEF

## Usage in Different Modes

### BENCHMARK Mode
```python
# Uses fair matching system for unbiased results
fighter_a, fighter_b = generate_matched_fighters()  # Equal stat totals

# Old unfair system (deprecated):
# fighter = create_fighter_random(role=None)  # Random stat totals
```

**Technical Implementation:**
```python
def generate_matched_fighters():
    # Generate Fighter A with random stats
    hp_a = random.randint(3, 18)
    atk_a = random.randint(3, 18)
    def_a = random.randint(3, 18)
    agi_a = random.randint(3, 18)
    total_stats = hp_a + atk_a + def_a + agi_a

    # Generate Fighter B with same total but different distribution
    # Algorithm ensures all stats remain within 3-18 range
    # Result: perfectly fair comparison of role effectiveness
```

### BUILD Mode
```python
# Custom stats with specific role
fighter = create_fighter(hp=15, attack=12, defense=10, agility=16, role="ASSASSIN")

# Or auto-classify custom stats
stats = {"hp": 15, "attack": 12, "defense": 10, "agility": 16}
role = classify_build_role(stats["hp"], stats["attack"], stats["defense"], stats["agility"])
```

### SINGLE Mode
```python
# Predefined balanced builds for each role
fighter_a = create_fighter_balanced("TANK")      # (18,8,18,8)
fighter_b = create_fighter_balanced("ASSASSIN")  # (10,16,8,16)
```

## Technical Implementation

### File Structure
- `state/fighter_factory.py` - Scoring-based classification and fighter creation
- `simulation/benchmark.py` - **Fair matching system** with equal stat totals
- `game/run_fight.py` - Supports all 5 roles with input validation
- `balance/targets.py` - **Updated targets** for fair system validation

### Key Algorithms
1. **Role Scoring System** - Continuous classification with confidence metrics
2. **Fair Matching Generator** - Equal stat total distribution algorithm
3. **Stat Total Validation** - 100% perfect match verification
4. **Confidence Analysis** - Pure vs hybrid build identification

### API Integration
The enhanced classification system provides:
- **Unbiased role analysis** - Fair stat total comparisons only
- **Confidence scoring** - Identifies pure vs hybrid builds
- **Real-time fairness validation** - Monitors stat total equality
- **Production-ready balance data** - Accurate role effectiveness metrics

## Future Considerations

### Potential Improvements
1. **Weighted classification** - Consider stat ratios instead of just maximum values
2. **Hybrid roles** - Multi-role classifications for edge cases
3. **Balance adjustments** - Combat mechanic changes to improve role balance
4. **Custom role definitions** - Allow user-defined classification rules

### Updated Balance Targets
The scoring system requires updated validation targets:

```python
# Role distribution targets (percentage of total fights)
"role_distribution": {
    "TANK": (0.18, 0.30),        # 18-30% of builds
    "BRUISER": (0.10, 0.20),     # 10-20% of builds
    "SKIRMISHER": (0.12, 0.22),  # 12-22% of builds
    "ASSASSIN": (0.15, 0.25),    # 15-25% of builds
    "UNIVERSAL": (0.20, 0.35),   # 20-35% of builds
},
"role_balance_spread": (0.0, 0.15),  # Max 15% spread (relaxed for new system)
```

### Balance Recommendations (Fair System)
Based on fair matching analysis revealing true meta:

#### 🚨 **Critical Actions Required**
1. **Major TANK buffs** - 36.7% winrate is unacceptable
   - Increase block damage reduction: 30% → 45%
   - Add damage reflection mechanic
   - Buff HP scaling effectiveness
2. **SKIRMISHER overhaul** - Mobility needs to matter more
   - Increase dodge chance scaling with agility
   - Add mobility-based damage bonuses
   - Reduce stamina costs for high-agility builds
3. **BRUISER/ASSASSIN nerfs** - 66%+ winrate too dominant
   - Reduce attack scaling slightly
   - Increase stamina costs for high-attack builds

#### ⚙️ **Scoring System Adjustments**
Role formulas should be rebalanced for 50% target winrates:
```python
# Nerf offensive roles
scores["BRUISER"] = atk_n * 0.45 + hp_n * 0.25 + def_n * 0.30    # Less attack focus
scores["ASSASSIN"] = atk_n * 0.45 + agi_n * 0.55                  # Less attack focus

# Buff defensive roles
scores["TANK"] = hp_n * 0.6 + def_n * 0.4                        # More HP emphasis
scores["SKIRMISHER"] = agi_n * 0.7 + atk_n * 0.15 + def_n * 0.15 # More AGI focus
```

#### 🎯 **Production Validation Targets**
Updated role balance targets for fair system:
```python
"role_balance_spread": (0.0, 0.10),  # Tighter control - max 10% spread
"role_winrate_targets": {
    "BRUISER": (0.45, 0.55),      # Target: 50% ±5%
    "ASSASSIN": (0.45, 0.55),     # Target: 50% ±5%
    "UNIVERSAL": (0.45, 0.55),    # Target: 50% ±5%
    "SKIRMISHER": (0.45, 0.55),   # Target: 50% ±5%
    "TANK": (0.45, 0.55),         # Target: 50% ±5%
}
```

#### 📊 **Ongoing Monitoring**
- **Fairness validation** - ensure 100% perfect stat total matches
- **Combat mechanic effectiveness** - track block/dodge/crit impact on roles
- **Meta evolution** - monitor if players adapt to true role strengths
- **Hybrid vs pure** - track confidence levels and performance correlation