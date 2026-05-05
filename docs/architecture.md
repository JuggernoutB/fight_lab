# Fight Logic - Architecture Documentation

## Overview

Модульная боевая система с чистым разделением ответственности между компонентами. Система построена на принципах функционального программирования с минимальными побочными эффектами.

## Architecture Principles

### 1. Separation of Concerns
Каждый модуль имеет единственную ответственность:
- **core/**: Боевые механики и математические расчеты
- **ai/**: Принятие решений и стратегии
- **state/**: Управление состоянием боя и бойцов
- **simulation/**: Оркестрация боевого процесса
- **telemetry/**: Сбор и анализ данных
- **balance/**: Валидация баланса системы

### 2. Clean API Structure
Внешние модули взаимодействуют с core через единый API интерфейс, скрывающий внутреннюю структуру.

### 3. Deterministic Combat
Система поддерживает детерминированное поведение через seed-based рандомизацию для надежного тестирования.

## Project Structure

```
fight_logicV15/
├── core/                   # Core combat mechanics (Backend Engine)
│   ├── api.py             # Unified API interface
│   ├── config.py          # Centralized configuration
│   └── modules/           # Implementation modules
│       ├── combat.py      # Main combat engine
│       ├── stamina.py     # Stamina system
│       ├── fatigue.py     # Fatigue mechanics
│       ├── crit.py        # Critical hit system
│       ├── dodge.py       # Dodge mechanics
│       ├── block.py       # Blocking system
│       ├── ehp.py         # Effective HP calculations
│       └── zones.py       # Combat zone definitions
├── game/                  # Frontend/Game API (Telegram Mini App)
│   ├── __init__.py        # Package exports
│   └── run_fight.py       # Clean game API for frontend
├── state/                 # State management
│   ├── fight_state.py     # Fight state structures
│   ├── fighter_factory.py # Fighter creation
│   └── meta_layer.py      # Meta game mechanics
├── ai/                    # AI decision making
│   └── role_engine.py     # Role-based AI
├── simulation/            # Combat orchestration
│   ├── game_engine.py     # Clean game loop
│   ├── simulator.py       # Legacy compatibility
│   └── benchmark.py       # Mass simulation
├── telemetry/             # Data collection
│   └── telemetry.py       # Fight telemetry
├── balance/               # Balance validation
│   ├── targets.py         # Expected metrics
│   └── validator.py       # Validation logic
├── docs/                  # Documentation
│   └── architecture.md    # This file
└── main.py               # Entry point
```

## Core Layer (`core/`)

### API Interface (`api.py`)
- **Назначение**: Единая точка доступа к core функциональности
- **Экспорты**: process_attack, get_initial_stamina, apply_stamina, get_config, CORE_VERSION
- **Принцип**: Скрывает внутреннюю структуру core модулей
- **Безопасность**: Read-only CONFIG access, защита от runtime mutations

### Configuration (`config.py`)
- **Назначение**: Централизованная конфигурация всех боевых параметров
- **Секции**: ENGINE, CRITICAL HITS, DODGE, BLOCKING, FATIGUE, STAMINA, EHP
- **Использование**: Единый источник истины для балансных настроек

### Combat Engine (`modules/combat.py`)
- **Назначение**: Основной боевой движок
- **Функция**: process_attack() - обработка атак с применением всех механик
- **Ответственность**: Координация crit/dodge/block механик, расчет итогового урона
- **Безопасность**: Data normalization, защита от typos в fighter данных

### Stamina System (`modules/stamina.py`)
- **Назначение**: Система стамины и затрат на действия
- **Функции**: get_initial_stamina(), apply_stamina(), calculate_action_cost()
- **Ответственность**: Управление ресурсом стамины, costs/regen расчеты

### Fatigue System (`modules/fatigue.py`)
- **Назначение**: Система усталости и штрафов
- **Функции**: get_stamina_level(), get_fatigue_multiplier()
- **Уровни**: FRESH, TIRED, EXHAUSTED с соответствующими multipliers

### EHP Calculator (`modules/ehp.py`)
- **Назначение**: Effective Health Points модель
- **Класс**: EHPDamageCalculator с методами: calculate_base_hp(), calculate_damage_output(), calculate_defense_multiplier(), apply_defense_reduction()
- **Ответственность**: Преобразование статов в игровые значения и применение защиты
- **Совместимость**: Предоставляет convenience functions для обратной совместимости

## Game Layer (`game/`) - Frontend API

### Run Fight API (`run_fight.py`)
- **Назначение**: Clean API для интеграции с Telegram Mini App
- **Функции**: run_fight(), run_quick_fight(), run_tournament_fight(), run_training_fight()
- **Форматы**: Структурированные JSON responses для frontend
- **Использование**:
  - Frontend: run_quick_fight() для быстрых боев
  - Backend: run_fight() для полной игровой логики
  - Tournaments: Детерминированные matches с replay data
  - Custom fighters: Player customization support

### Package Exports (`__init__.py`)
- **Назначение**: Чистые exports для простого импорта
- **Принцип**: Скрывает внутреннюю структуру game модуля

## State Layer (`state/`)

### Fight State (`fight_state.py`)
- **Назначение**: Определение структур состояния боя
- **Классы**: FighterState, FightState
- **Ответственность**: Хранение HP, stamina, статов, метаданных боя

### Fighter Factory (`fighter_factory.py`)
- **Назначение**: Создание бойцов на основе статов
- **Функции**: create_fighter(), create_fighter_balanced(), create_fighter_random()
- **Архитектура**: stats (8-18) → EHP formulas → actual game values

### Meta Layer (`meta_layer.py`)
- **Назначение**: Мета-игровые механики (momentum, deadlock pressure)
- **Функции**: update_meta()
- **Ответственность**: Глобальная динамика боя

## AI Layer (`ai/`)

### Role Engine (`role_engine.py`)
- **Назначение**: AI принятие решений на основе ролей
- **Функции**: choose_action()
- **Роли**: BRUISER, ASSASSIN, TANK, SKIRMISHER
- **Ответственность**: Генерация действий (attack/defense zones) по ролевой логике

## Simulation Layer (`simulation/`)

### Game Engine (`game_engine.py`)
- **Назначение**: Чистый игровой движок
- **Функция**: simulate_fight() - возвращает pure data без side effects
- **Формат**: {winner, rounds, log, final_state}
- **Использование**: Интеграция с фронтендом, replay системы

### Simulator (`simulator.py`)
- **Назначение**: Legacy wrapper для обратной совместимости
- **Ответственность**: Адаптация новой архитектуры к старому telemetry API
- **Функции**: Реконструкция stamina trajectory для корректной телеметрии

### Benchmark (`benchmark.py`)
- **Назначение**: Массовое тестирование и анализ
- **Функции**: run_benchmark() - запуск N боев с детальной статистикой
- **Выводы**: BUILD ANALYSIS, ROLE DISTRIBUTION, ROUNDS DISTRIBUTION, DRAW ANALYSIS, DPS VARIANCE

## Telemetry Layer (`telemetry/`)

### Telemetry (`telemetry.py`)
- **Назначение**: Сбор и обработка данных о боях
- **Функции**: record(), summary()
- **Метрики**: rounds, total_damage, mechanics distribution, stamina distribution
- **Ответственность**: Конвертация structured events в аналитические метрики

## Balance Layer (`balance/`)

### Targets (`targets.py`)
- **Назначение**: Определение ожидаемых диапазонов для всех метрик
- **Структура**: TARGETS словарь с (min, max) значениями
- **Метрики**: rounds_avg, dps_avg, draw_rate, mechanics rates, damage splits

### Validator (`validator.py`)
- **Назначение**: Автоматическая валидация баланса системы
- **Функции**: validate() - возвращает PASS/FAIL с детальным отчетом
- **Использование**: CI/CD pipeline, regression testing

## Data Flow

### Backend/Core Flow
```
Fighter Stats → Fighter Factory → FighterState
                                      ↓
Action Selection ← AI Layer ← Fight Context
        ↓
Combat Engine ← Core API ← Combat Actions
        ↓
Combat Results → State Update → Telemetry
        ↓
Game Loop → Fight Completion → Balance Validation
```

### Frontend/Game API Flow
```
Frontend Request → Game API → Fighter Factory
        ↓                         ↓
    JSON Config → Game Engine → Structured Events
        ↓                         ↓
   Clean JSON ← Summary Stats ← Fight Result
        ↓
Telegram Mini App → UI Animation
```

## Key Data Structures

### FighterState
```python
class FighterState:
    hp: float              # Current health points
    stamina: int          # Current stamina
    role: str            # Fighter role (BRUISER, ASSASSIN, etc.)
    attack: int          # Base attack stat (8-18)
    defense: int         # Base defense stat (8-18)
    agility: int         # Base agility stat (8-18)
```

### Fight Result
```python
{
    "winner": "A" | "B" | "DRAW_*",
    "rounds": int,
    "log": [event_stream],
    "final_state": FightState
}
```

### Event Stream
```python
{
    "round": 1,
    "attacks": [
        {
            "attacker": "A",
            "defender": "B",
            "zone": "head",
            "damage": 120.0,
            "event": "crit"
        }
    ]
}
```

### Game API Response
```python
{
    "winner": "A" | "B" | "DRAW_*",
    "rounds": int,
    "fighter_a": {
        "role": str,
        "final_hp": float,
        "final_stamina": int
    },
    "fighter_b": {
        "role": str,
        "final_hp": float,
        "final_stamina": int
    },
    "log": [events...] | None,
    "summary": {
        "total_damage_to_a": float,
        "total_damage_to_b": float,
        "fight_length": int
    }
}
```

### Fighter Configuration
```python
{
    "type": "balanced" | "random" | "custom",
    "role": "BRUISER" | "ASSASSIN" | "TANK" | "SKIRMISHER",
    "stats": {  # Optional for custom type
        "hp": 15,
        "attack": 12,
        "defense": 15,
        "agility": 8
    }
}
```

## Configuration Management

Все балансные параметры централизованы в `core/config.py`:

- **ENGINE**: Block break ratios
- **CRITICAL HITS**: Base chances, scaling, multipliers
- **DODGE**: Dodge mechanics and damage ratios
- **BLOCKING**: Block reduction and break chances
- **FATIGUE**: Stamina thresholds and effectiveness multipliers
- **STAMINA**: Costs, regeneration, limits
- **EHP SCALING**: Health, damage, defense formulas

## Testing and Validation

### Deterministic Testing
- Seed-based randomization для воспроизводимых результатов
- Автоматические regression tests через balance validator
- Structured events для debugging и replay

### Balance Validation
- Автоматическая проверка всех ключевых метрик
- PASS/FAIL статус для CI/CD integration
- Детальные отчеты о состоянии баланса

## Benefits

1. **Modularity**: Легко добавлять новые механики без влияния на существующий код
2. **Testability**: Каждый компонент тестируется изолированно
3. **Maintainability**: Четкое разделение ответственности
4. **Scalability**: Архитектура готова к расширению функционала
5. **Reliability**: Детерминированное поведение и автоматическая валидация
6. **Integration Ready**: Clean API для frontend интеграции
7. **Production Security**: Read-only CONFIG, data validation, protected API surface
8. **Game Ready**: Telegram Mini App compatible with structured JSON responses
9. **Multi-Platform**: Separation между core engine (backend) и game API (frontend)
10. **Developer Experience**: Простые imports, четкие interfaces, comprehensive testing