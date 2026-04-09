# Migration Guide V14 → V15

## Overview

Данное руководство описывает миграцию с архитектуры V14 на новую модульную архитектуру V15.

## Key Changes

### 1. File Structure
```
V14 (Monolithic)              V15 (Modular)
├── combat_core.py           ├── core/
├── role_engine.py           │   ├── combat_core.py
├── meta_layer.py            │   ├── stamina_core.py
├── simulator_v14.py         │   ├── damage_model.py
├── simulation.py            │   └── resolution_engine.py
└── telemetry (mixed)        ├── ai/
                             │   ├── role_engine.py
                             │   └── action_selector.py
                             ├── state/
                             │   ├── meta_layer.py
                             │   └── fight_state.py
                             ├── simulation/
                             │   ├── simulator.py
                             │   └── fight_runner.py
                             ├── telemetry/
                             │   ├── telemetry.py
                             │   └── metrics.py
                             └── config/
                                 └── balance.py
```

### 2. Responsibility Separation

| V14 Function | V15 Location | New Responsibility |
|-------------|--------------|-------------------|
| `process_attack_damage()` | `core/combat_core.py` | Pure damage math only |
| `simulate_fight()` | `simulation/simulator.py` | Orchestration only |
| Metrics calculation | `telemetry/metrics.py` | Dedicated analytics |
| Role decisions | `ai/role_engine.py` | AI decisions only |
| Balance constants | `config/balance.py` | Centralized config |

### 3. API Changes

#### V14 Combat Function
```python
# V14
def process_attack_damage(
    attacker_stats, defender_stats,
    attacker_stamina, defender_stamina,
    attacker_zones, defender_zones
) -> Dict[str, Tuple[float, str]]:
```

#### V15 Combat Function
```python
# V15
def process_combat_action(
    attacker_stats, defender_stats,
    attacker_stamina, defender_stamina,
    attack_zones, defend_zones
) -> CombatResult:
```

### 4. Data Structure Migration

#### V14 Result Format
```python
# V14 - Raw dictionary
{
    "head": (damage, "crit"),
    "chest": (damage, "hit"),
    ...
}
```

#### V15 Result Format
```python
# V15 - Structured data
CombatResult(
    damage_dealt=total_damage,
    events=[
        CombatEvent(zone="head", event_type="crit", damage=damage),
        CombatEvent(zone="chest", event_type="hit", damage=damage),
        ...
    ],
    stamina_cost=cost
)
```

## Migration Steps

### Step 1: Extract Core Mathematics
1. Move damage calculation formulas to `core/damage_model.py`
2. Extract stamina logic to `core/stamina_core.py`
3. Separate combat mechanics to `core/resolution_engine.py`
4. Create unified `core/combat_core.py`

### Step 2: Restructure AI Layer
1. Move role classification to `ai/role_engine.py`
2. Create advanced action selection in `ai/action_selector.py`
3. Remove combat math from AI decisions

### Step 3: Create State Management
1. Extract meta layer to `state/meta_layer.py`
2. Create comprehensive fight state in `state/fight_state.py`
3. Implement proper state transitions

### Step 4: Build Telemetry System
1. Create data collection in `telemetry/telemetry.py`
2. Move all metrics to `telemetry/metrics.py`
3. Remove metrics from simulation logic

### Step 5: Centralize Configuration
1. Extract all constants to `config/balance.py`
2. Group by logical systems
3. Create configuration access interface

### Step 6: Rebuild Simulation
1. Rewrite `simulation/simulator.py` as pure orchestrator
2. Create utilities in `simulation/fight_runner.py`
3. Implement clean data flow

## Compatibility Layer

Для облегчения миграции можно создать compatibility wrapper:

```python
# compatibility.py
def simulate_fight_v14_compat(player_a, player_b):
    """V14 compatible interface"""
    from simulation.simulator import simulate_fight

    result = simulate_fight(player_a, player_b)

    # Convert V15 result to V14 format
    return {
        'winner': result.winner,
        'rounds': result.rounds,
        'dps_a': result.metrics['dps_a'],
        'dps_b': result.metrics['dps_b'],
        # ... other V14 fields
    }
```

## Testing Strategy

### 1. Unit Testing
Каждый модуль тестируется изолированно:
```python
# test_combat_core.py
def test_damage_calculation():
    result = process_combat_action(...)
    assert result.damage_dealt > 0
    assert len(result.events) > 0
```

### 2. Integration Testing
Тестирование взаимодействия модулей:
```python
# test_integration.py
def test_full_fight_flow():
    result = simulate_fight(player_a, player_b)
    assert result.winner in ['A', 'B', 'DRAW']
    assert result.telemetry is not None
```

### 3. Regression Testing
Сравнение результатов V14 vs V15:
```python
def test_v14_v15_compatibility():
    # Run same fight in both versions
    v14_result = simulate_fight_v14(player_a, player_b)
    v15_result = simulate_fight_v15(player_a, player_b)

    # Results should be statistically similar
    assert abs(v14_result.dps - v15_result.metrics['dps']) < threshold
```

## Performance Considerations

### V15 Performance Benefits
1. **Reduced coupling**: Меньше circular dependencies
2. **Better caching**: Изолированные pure functions
3. **Parallel testing**: Независимые модули
4. **Memory efficiency**: Structured data instead of dictionaries

### Potential Overhead
1. **Function call overhead**: Больше слоев вызовов
2. **Data copying**: Структурированные данные vs raw dicts
3. **Initial complexity**: Больше файлов для загрузки

## Rollback Plan

Если миграция вызовет проблемы:

1. **Keep V14**: Сохранить V14 код в отдельной ветке
2. **Feature flags**: Переключение между V14/V15 логикой
3. **Gradual migration**: Поэтапная замена модулей
4. **A/B testing**: Сравнение производительности

## Success Criteria

Миграция считается успешной если:

- ✅ Все V14 тесты проходят на V15
- ✅ Performance не деградирует более чем на 10%
- ✅ New features легко добавляются
- ✅ Code coverage не снижается
- ✅ Balance остается стабильным