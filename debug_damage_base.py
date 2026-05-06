#!/usr/bin/env python3
# Отладка damage_base модификатора

from items import Item, EquipmentSlot, Equipment, assemble_fighter_from_state, create_default_modifiers
from state.fighter_factory import create_fighter
from core.modules.ehp import EHPDamageCalculator

# 1. Базовая проверка расчёта урона
calc = EHPDamageCalculator()
atk_stat = 6

print("=== БАЗОВАЯ ПРОВЕРКА ===")
base_damage = calc.calculate_damage_output(atk_stat)
print(f"ATK stat: {atk_stat}")
print(f"Base damage from EHP: {base_damage}")

# 2. Проверка модификаторов
print("\n=== ПРОВЕРКА МОДИФИКАТОРОВ ===")

# Пустые модификаторы
empty_mods = create_default_modifiers()
print(f"Empty modifiers damage_base: {empty_mods.damage_base}")

# Модификаторы с оружием
weapon = Item("Test Weapon", EquipmentSlot.MAIN_HAND, {"damage_base": 3.0})
equipment = Equipment()
equipment = equipment.equip_item(weapon)

fighter = create_fighter(hp_stat=10, attack_stat=6, defense_stat=5, agility_stat=8, role="TEST")
final_stats, final_mods = assemble_fighter_from_state(fighter, equipment)
print(f"With weapon damage_base: {final_mods.damage_base}")

# 3. Пошаговая симуляция logic из combat.py
print("\n=== ПОШАГОВАЯ СИМУЛЯЦИЯ ===")

# БЕЗ модификаторов
print("БЕЗ оружия:")
base1 = calc.calculate_damage_output(atk_stat)
print(f"  1. Base from ATK: {base1}")
# attacker_modifiers = None, поэтому damage_base не добавляется
print(f"  2. After damage_base: {base1} (no modifiers)")
base1 /= 1  # 1 зона
print(f"  3. After zone division: {base1}")

# С модификаторами
print("\nС оружием:")
base2 = calc.calculate_damage_output(atk_stat)
print(f"  1. Base from ATK: {base2}")
if final_mods:
    base2 += final_mods.damage_base
    print(f"  2. After damage_base (+{final_mods.damage_base}): {base2}")
base2 /= 1  # 1 зона
print(f"  3. After zone division: {base2}")

print(f"\n🔥 Разница в базовом уроне: +{base2 - base1}")

# 4. Проверим что происходит дальше в combat.py
print("\n=== ДАЛЬНЕЙШАЯ ОБРАБОТКА ===")
print("После базового расчёта урон проходит через:")
print("- Fatigue multiplier")
print("- Zone multiplier")
print("- Crit/dodge/block логику")
print("- Defense reduction")
print("- Damage variance")
print("- Probabilistic rounding")
print("\nВозможно проблема в одном из этих шагов!")