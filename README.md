# Fight Logic V15 - Production Combat Simulation System

## 🎯 Overview

V15 - производственная боевая система с CLI интерфейсом, JSON конфигурациями, level-based прогрессией и стабильным API.

🔥 **NEW in V15.8**: Level-based fighter creation system с научно-точным балансированием!

## 🏗️ Architecture

```
fight_logicV15/
├── core/           # Core combat mechanics and API
├── state/          # Fighter state management + Level system
│   ├── level_system.py    # 🆕 Level-based fighter creation
│   └── fighter_factory.py # Legacy + balanced presets
├── simulation/     # Fight orchestration and game engine
│   ├── level_benchmark.py # 🆕 Level-based benchmarking
│   └── benchmark.py       # Legacy + level integration
├── telemetry/      # Analytics and metrics
├── game/           # Game API layer for frontends
├── modes/          # CLI simulation modes
├── configs/        # JSON configuration files
├── balance/        # Balance validation system
└── docs/           # Documentation
```

## 🚀 Quick Start

### CLI Interface

```bash
# 🆕 LEVEL-BASED BENCHMARKING (RECOMMENDED)
python main.py benchmark_level 9 5000     # Level 9, 5000 fights
python main.py benchmark_level 5 1000     # Level 5, 1000 fights
python main.py benchmark_level            # Default: Level 9, 5000 fights

# SINGLE FIGHT ANALYSIS
python main.py single                      # Debug mode (technical details)
python main.py single configs/release_single.json  # Human-readable
python main.py single configs/compact_single.json  # Quick analysis

# BUILD TESTING
python main.py build configs/default_build.json    # 1v1 build comparison

# LEGACY BENCHMARKING
python main.py benchmark                   # Old random system (unfair)

# HELP
python main.py --help
```

### API Integration

```python
from game.run_fight import run_fight

# Quick frontend integration
result = run_fight(
    {"type": "balanced", "role": "BRUISER"},
    {"type": "balanced", "role": "ASSASSIN"},
    {"seed": 42, "include_detailed_log": True}
)

print(f"Winner: {result['winner']}")
print(f"Rounds: {result['rounds']}")
print(f"API Version: {result['api_version']}")
```

## 📊 Key Features

- **🆕 Level-Based System**: Scientific fighter progression with perfect fairness
- **CLI Interface**: Production-ready command line interface
- **JSON Configuration**: Flexible, version-controlled configuration files
- **Dual Logging**: Release mode for designers, debug mode for developers
- **Build Analysis**: Test custom builds against multiple archetypes
- **Balance Validation**: Automated balance testing with PASS/FAIL reporting
- **Game API**: Clean frontend integration for Telegram Mini Apps
- **Deterministic Testing**: Seed-based reproducible fights

## 🎯 Level-Based Fighter System (NEW!)

### Concept
Бойцы создаются на основе **уровня** вместо hardcoded статов, что обеспечивает:
- ✅ **Perfect Fairness**: Все бои с одинаковым stat budget
- ✅ **Scientific Balance**: Честные измерения без "stat luck"
- ✅ **Game Progression**: Готовая система уровней для игроков
- ✅ **Scaling Analysis**: Понимание как роли ведут себя на разных уровнях

### Level Formula
```
Level 1:  12 stat points (базовые 3 в каждом стате)
Level N:  12 + (N-1) × 5 stat points

Examples:
Level 5:  32 points
Level 9:  52 points (эквивалент текущих presets)
Level 11: 62 points
```

### Role Weights (Percentages instead of absolute numbers)
```python
TANK:       HP=35%, DEF=35%, ATK=15%, AGI=15%    # Maximum survivability
BRUISER:    HP=30%, ATK=30%, DEF=25%, AGI=15%    # Balanced damage dealer
ASSASSIN:   ATK=40%, AGI=40%, HP=10%, DEF=10%    # Glass cannon
SKIRMISHER: AGI=40%, ATK=25%, DEF=20%, HP=15%    # Mobile fighter
UNIVERSAL:  HP=25%, ATK=25%, DEF=25%, AGI=25%    # Perfect balance
```

### Usage Examples
```bash
# Compare roles at different levels
python main.py benchmark_level 5 1000    # Early game balance
python main.py benchmark_level 9 5000    # Mid game balance (current presets)
python main.py benchmark_level 11 2000   # End game balance

# API usage for game development
from state.level_system import create_fighter_by_level
tank_lvl9 = create_fighter_by_level(9, "TANK")     # 52 stat points
assassin_lvl5 = create_fighter_by_level(5, "ASSASSIN")  # 32 stat points
```

## 🎮 Simulation Modes

### Single Fight Mode
Detailed analysis of individual fights for debugging and design:
```bash
python main.py single configs/default_single.json     # Debug logging (default)
python main.py single configs/release_single.json    # Human-readable logging
```

### Build Analysis Mode
Test custom fighter builds against all archetypes:
```bash
python main.py build configs/default_build.json      # Standard build
python main.py build configs/tank_build.json         # Tank specialist
```

### Benchmark Mode
Mass simulation for balance validation:
```bash
python main.py benchmark                             # 5000 fights + validation
```

## ⚙️ Configuration System

### JSON Configuration Files
- `configs/default_single.json` - Single fight with debug logging (default)
- `configs/release_single.json` - Single fight with human-readable logging
- `configs/default_build.json` - Build analysis configuration
- `configs/tank_build.json` - Example tank build analysis

### Custom Fighter Configuration
```json
{
  "fighter_a": {
    "type": "custom",
    "role": "BRUISER",
    "stats": {
      "hp": 16,
      "attack": 14,
      "defense": 12,
      "agility": 10
    }
  }
}
```

## 🎯 Production Architecture

### Core API (`core/api.py`)
```python
from core.api import process_attack, get_config, CORE_VERSION

# Stable combat engine with version tracking
result = process_attack(attacker, defender, ...)
config = get_config()  # Read-only configuration access
```

### Game Layer (`game/run_fight.py`)
```python
from game.run_fight import run_fight, run_quick_fight

# Frontend-ready JSON responses
result = run_fight(fighter_a, fighter_b, options)
# Returns: {"winner": "A", "rounds": 12, "api_version": "1.0", ...}
```

### Balance System (`balance/`)
- `balance/targets.py` - Expected metrics ranges
- `balance/validator.py` - Automated validation with PASS/FAIL

## 🔬 Testing & Validation

### Manual Testing
```bash
# Test single fight mode
python main.py single configs/default_single.json

# Test build analysis
python main.py build configs/default_build.json

# Test balance validation
python main.py benchmark
```

### API Testing
```python
# Test game API stability
python test_api_stability.py

# Test deterministic behavior
python test_determinism.py

# Test event system
python test_event_system.py
```

## 🏗️ Development

### Creating Custom Configurations
```json
{
  "seed": 42,
  "iterations": 20,
  "fighter_a": {
    "type": "custom",
    "role": "ASSASSIN",
    "stats": {"hp": 12, "attack": 18, "defense": 8, "agility": 16}
  },
  "opponents": [
    {"name": "BRUISER", "type": "balanced", "role": "BRUISER"},
    {"name": "TANK", "type": "balanced", "role": "TANK"}
  ]
}
```

### Extension Points
- Add new simulation modes in `modes/`
- Create custom configurations in `configs/`
- Extend balance targets in `balance/targets.py`
- Add frontend integrations using `game/run_fight.py`

## 📊 Balance Validation System

Automated PASS/FAIL validation for:
- ✅ Fight length distribution (rounds)
- ✅ DPS balance (damage per round)
- ✅ Draw rates (stamina exhaustion vs mutual death)
- ✅ Combat mechanics (crit/dodge/block rates)
- ✅ Stamina state distribution (fresh/tired/exhausted)

```bash
python main.py benchmark
# Output: ✅ ALL TESTS PASSING - Combat system balanced
```

## 🎯 Production Status

### ✅ Completed Features
- [x] Production-ready CLI interface
- [x] JSON configuration system
- [x] Dual logging modes (release/debug)
- [x] Build analysis system
- [x] Balance validation framework
- [x] Game API for frontend integration
- [x] Deterministic testing support
- [x] Comprehensive documentation

### 🚀 Ready for Production
- ✅ Telegram Mini App integration
- ✅ Backend API deployment
- ✅ Automated balance testing
- ✅ Version tracking and compatibility

---

**Fight Logic V15** - Production-ready combat simulation system with enterprise-grade CLI interface and JSON configuration management.