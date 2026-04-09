# Fight Logic V15 - Modular Combat Simulation System

## 🎯 Overview

V15 представляет собой полный архитектурный рефакторинг боевой системы с четким разделением ответственности между модулями.

## 🏗️ Architecture

```
fight_logicV15/
├── core/          # Pure mathematics and game rules
├── ai/            # Decision making and strategy
├── state/         # State management and tracking
├── simulation/    # Fight orchestration
├── telemetry/     # Data collection and analytics
├── config/        # Balance configuration
└── docs/          # Documentation
```

## 🚀 Quick Start

```python
from simulation.simulator import simulate_fight
from simulation.fight_runner import generate_random_player

# Generate two players
player_a = generate_random_player()
player_b = generate_random_player()

# Run a fight
result = simulate_fight(player_a, player_b)

print(f"Winner: {result.winner}")
print(f"Rounds: {result.rounds}")
print(f"Metrics: {result.metrics}")
```

## 📊 Key Features

- **Clean Architecture**: Strict separation of concerns
- **Modular Design**: Easy to extend and test
- **Rich Analytics**: Comprehensive telemetry and metrics
- **Configurable Balance**: Centralized balance configuration
- **Role-based AI**: Advanced role classification and strategies

## 🔧 Core Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **No Cross-Dependencies**: Modules communicate through simulation layer
3. **Pure Functions**: Deterministic and testable
4. **Data Contracts**: Structured interfaces between layers

## 📋 Modules

### Core Layer
- `combat_core.py` - Pure damage mathematics
- `stamina_core.py` - Stamina and fatigue system
- `damage_model.py` - EHP damage model
- `resolution_engine.py` - Combat mechanics (crit, dodge, block)

### AI Layer
- `role_engine.py` - Role classification and basic strategy
- `action_selector.py` - Advanced action selection algorithms

### State Layer
- `meta_layer.py` - Momentum and phase management
- `fight_state.py` - Complete fight state tracking

### Simulation Layer
- `simulator.py` - Main fight orchestration
- `fight_runner.py` - Utilities and benchmarking

### Telemetry Layer
- `telemetry.py` - Data collection during fights
- `metrics.py` - Analytics and metric calculations

## 🎮 Migration from V14

V15 maintains API compatibility while providing enhanced modularity. See `docs/migration_guide.md` for detailed migration instructions.

## 📚 Documentation

- `docs/architecture.md` - Detailed architecture overview
- `docs/migration_guide.md` - V14 → V15 migration guide

## 🧪 Testing

Each module can be tested independently:

```python
# Test combat core in isolation
from core.combat_core import process_combat_action

result = process_combat_action(...)
assert result.damage_dealt > 0
```

## ⚖️ Balance Configuration

All balance constants are centralized in `config/balance.py`:

```python
from config.balance import get_config

stamina_config = get_config('stamina')
damage_config = get_config('damage')
```

## 🎯 Version 15 Goals

- [x] Complete architectural separation
- [x] Eliminate cross-module dependencies
- [x] Create comprehensive telemetry system
- [x] Centralize balance configuration
- [ ] Implement all TODO functions
- [ ] Complete migration from V14
- [ ] Performance optimization
- [ ] Advanced AI strategies

---

**Fight Logic V15** - Professional, scalable combat simulation architecture ready for production use.