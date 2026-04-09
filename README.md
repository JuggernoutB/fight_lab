# Fight Logic V15 - Production Combat Simulation System

## 🎯 Overview

V15 - производственная боевая система с CLI интерфейсом, JSON конфигурациями и стабильным API.

## 🏗️ Architecture

```
fight_logicV15/
├── core/          # Core combat mechanics and API
├── state/         # Fighter state management
├── simulation/    # Fight orchestration and game engine
├── telemetry/     # Analytics and metrics
├── game/          # Game API layer for frontends
├── modes/         # CLI simulation modes
├── configs/       # JSON configuration files
├── balance/       # Balance validation system
└── docs/          # Documentation
```

## 🚀 Quick Start

### CLI Interface

```bash
# Single fight with detailed analysis
python main.py single configs/default_single.json

# Debug mode with technical details
python main.py single configs/debug_single.json

# Build analysis against multiple opponents
python main.py build configs/default_build.json

# Mass simulation for balance validation
python main.py benchmark

# Help and available commands
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

- **CLI Interface**: Production-ready command line interface
- **JSON Configuration**: Flexible, version-controlled configuration files
- **Dual Logging**: Release mode for designers, debug mode for developers
- **Build Analysis**: Test custom builds against multiple archetypes
- **Balance Validation**: Automated balance testing with PASS/FAIL reporting
- **Game API**: Clean frontend integration for Telegram Mini Apps
- **Deterministic Testing**: Seed-based reproducible fights

## 🎮 Simulation Modes

### Single Fight Mode
Detailed analysis of individual fights for debugging and design:
```bash
python main.py single configs/default_single.json     # Release logging
python main.py single configs/debug_single.json      # Debug logging
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
- `configs/default_single.json` - Standard single fight setup
- `configs/debug_single.json` - Single fight with debug logging
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