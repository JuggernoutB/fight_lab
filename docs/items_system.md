# Items System Architecture

## Overview

Система предметов в fight lab реализована по принципу **data-driven** архитектуры с четким разделением слоёв. Combat engine не знает про предметы и работает только с финальными статами и модификаторами.

## Architecture Layers

```
Items (data layer)
    ↓
CombatModifiers (modifiers layer)
    ↓
CombatStats (stats layer)
    ↓
Combat Engine (calculation layer)
```

### Layer Separation

1. **Combat Engine НЕ знает про Items**
2. **Items влияют только через Modifiers**
3. **Modifiers - это чистые аддитивные бонусы**
4. **Stats остаются отделёнными от Items**

## Equipment Slots

Каждый игрок имеет **7 слотов** для предметов:

```python
class EquipmentSlot(Enum):
    HELM = "helm"           # 1. Защита головы
    CUIRASS = "cuirass"     # 2. Защита груди
    MIDPLATE = "midplate"   # 3. Защита живота
    WAISTGUARD = "waistguard" # 4. Защита бёдер
    GREAVES = "greaves"     # 5. Защита ног
    MAIN_HAND = "main_hand" # 6. Основное оружие
    OFF_HAND = "off_hand"   # 7. Второе оружие/щит
```

## Combat Modifiers

**13 типов модификаторов**, влияющих на боевые расчеты:

### Zone Protection (5 типов)
- `head_protection` - снижает урон по голове
- `chest_protection` - снижает урон по груди
- `abdomen_protection` - снижает урон по животу
- `hips_protection` - снижает урон по бёдрам
- `legs_protection` - снижает урон по ногам

**Механика**: `final_multiplier = base_multiplier - protection`
```python
# Пример: legs имеет базовый мультипликатор 0.95
# С защитой 0.01 финальный мультипликатор: 0.95 - 0.01 = 0.94
```

### Combat Bonuses (8 типов)
- `damage_base` - плоский бонус к урону
- `crit_chance` - дополнительный шанс крита
- `block_break_chance` - дополнительный шанс пробития блока
- `dodge_chance` - дополнительный шанс уворота
- `crit_power` - дополнительная мощность крита
- `block_break_power` - дополнительная мощность пробития
- `block_power` - дополнительная эффективность блока
- `fatigue_efficiency` - устойчивость к усталости

## Build Assembly Pipeline

```python
def assemble_fighter(base_stats: CombatStats, equipment: Equipment):
    # 1. Начинаем с базовых статов
    final_stats = base_stats

    # 2. Начинаем с пустых модификаторов
    final_modifiers = create_default_modifiers()

    # 3. Применяем каждый предмет
    for item in equipment.get_items():
        final_modifiers = apply_item_to_modifiers(final_modifiers, item)

    return final_stats, final_modifiers
```

## Example Items

```python
# Защитный шлем
helm = Item(
    name="Steel Helm",
    slot=EquipmentSlot.HELM,
    modifiers={"head_protection": 0.05}  # +5% защиты головы
)

# Критическое оружие
weapon = Item(
    name="Keen Blade",
    slot=EquipmentSlot.MAIN_HAND,
    modifiers={
        "damage_base": 2.0,      # +2 к базовому урону
        "crit_chance": 0.1,      # +10% к шансу крита
        "crit_power": 0.2        # +20% к мощности крита
    }
)

# Лёгкие ботинки (с негативными эффектами)
boots = Item(
    name="Swift Boots",
    slot=EquipmentSlot.GREAVES,
    modifiers={
        "dodge_chance": 0.15,      # +15% к шансу уворота
        "legs_protection": -0.02   # -2% к защите ног
    }
)
```

## Integration with Combat

### Old Combat API:
```python
process_attack(attacker_dict, defender_dict, ...)
```

### New Combat API:
```python
process_attack(
    attacker_stats, attacker_modifiers,
    defender_stats, defender_modifiers,
    ...
)
```

### Combat Engine Changes

1. **Zone damage calculation**:
```python
# Before
raw_damage = base * ZONE_MULTIPLIERS[zone]

# After
zone_multiplier = get_zone_multiplier(zone, defender_modifiers)
raw_damage = base * zone_multiplier
```

2. **Crit calculation**:
```python
# Before
base_chance = CONFIG["base_crit_chance"] + agi_bonus

# After
base_chance = CONFIG["base_crit_chance"] + agi_bonus
if attacker_modifiers:
    base_chance += attacker_modifiers.crit_chance
```

3. **Damage application**:
```python
# Before
base = calc.calculate_damage_output(atk_attack)

# After
base = calc.calculate_damage_output(atk_attack)
if attacker_modifiers:
    base += attacker_modifiers.damage_base
```

## Backward Compatibility

Все существующие fighters автоматически получают **пустые модификаторы** (`CombatModifiers()` со значениями 0.0), что обеспечивает полную обратную совместимость.

```python
# Legacy fighter
fighter = create_fighter(hp_stat=12, attack_stat=10, ...)
final_stats, final_mods = assemble_fighter_from_state(fighter)
# final_mods = CombatModifiers() с нулевыми значениями
```

## Testing

Система протестирована в `test_items_system.py`:

- ✅ Создание предметов и валидация модификаторов
- ✅ Сборка equipment и применение модификаторов
- ✅ Комбинирование модификаторов от нескольких предметов
- ✅ Zone protection механика
- ✅ Интеграция с боевой системой

## Future Extensions

Система спроектирована для расширения:

- **Наборы предметов** (set bonuses)
- **Зачарования** (enchantments)
- **Временные эффекты** (buffs/debuffs)
- **Процентные модификаторы** статов
- **Условные модификаторы** (против определённых ролей)

Архитектура позволяет добавлять новые типы модификаторов без изменения combat engine.