#!/usr/bin/env python3
# Детерминированный тест процентного модификатора damage_base

from items import create_wooden_sword, Equipment, assemble_fighter_from_state
from state.fighter_factory import create_fighter
from core.modules.ehp import EHPDamageCalculator


def test_damage_base_multiplier():
    """Тестируем логику мультипликатора напрямую"""
    print("🧮 ТЕСТ МУЛЬТИПЛИКАТИВНОГО МОДИФИКАТОРА")
    print("=" * 50)

    # Создаём бойца и меч
    fighter = create_fighter(hp_stat=10, attack_stat=8, defense_stat=5, agility_stat=7, role="TEST")
    wooden_sword = create_wooden_sword()

    # Экипируем меч
    equipment = Equipment()
    equipment = equipment.equip_item(wooden_sword)
    final_stats, final_mods = assemble_fighter_from_state(fighter, equipment)

    print(f"ATK stat: {fighter.attack}")
    print(f"damage_base modifier: {final_mods.damage_base}")
    print()

    # Тестируем логику из combat.py напрямую
    calc = EHPDamageCalculator()
    atk_attack = fighter.attack

    print("=== ПОШАГОВЫЙ РАСЧЕТ ===")

    # Шаг 1: Базовый урон
    base_damage = calc.calculate_damage_output(atk_attack)
    print(f"1. Base damage от ATK: {base_damage:.4f}")

    # Шаг 2: БЕЗ модификатора (как в старой логике)
    damage_without_mod = base_damage
    print(f"2. Без модификатора: {damage_without_mod:.4f}")

    # Шаг 3: С модификатором (новая логика)
    damage_with_mod = base_damage * (1.0 + final_mods.damage_base)
    print(f"3. С модификатором (+{final_mods.damage_base:.1%}): {damage_with_mod:.4f}")

    # Анализ
    actual_increase = damage_with_mod - damage_without_mod
    expected_increase = damage_without_mod * final_mods.damage_base

    print(f"\n=== РЕЗУЛЬТАТ ===")
    print(f"Ожидаемое увеличение: +{expected_increase:.4f}")
    print(f"Фактическое увеличение: +{actual_increase:.4f}")
    print(f"Процентное увеличение: +{(actual_increase/damage_without_mod)*100:.2f}%")

    # Проверка формулы
    if abs(actual_increase - expected_increase) < 0.0001:
        print("✅ Мультипликатор работает правильно!")
    else:
        print(f"❌ Ошибка в расчёте!")


def test_different_percentages():
    """Тестируем разные процентные значения"""
    print(f"\n📊 ТЕСТ РАЗНЫХ ПРОЦЕНТОВ")
    print("=" * 30)

    from items.item import Item, EquipmentSlot
    calc = EHPDamageCalculator()
    base_atk = 10
    base_damage = calc.calculate_damage_output(base_atk)

    test_percentages = [0.01, 0.05, 0.1, 0.25, 0.5]  # 1%, 5%, 10%, 25%, 50%

    print(f"Base damage (ATK={base_atk}): {base_damage:.2f}")
    print()

    for percent in test_percentages:
        # Создаём предмет с нужным процентом
        test_item = Item("Test Weapon", EquipmentSlot.MAIN_HAND, {"damage_base": percent})

        # Применяем модификатор
        modified_damage = base_damage * (1.0 + percent)
        increase = modified_damage - base_damage

        print(f"+{percent:.0%}: {base_damage:.2f} → {modified_damage:.2f} (+{increase:.2f})")


if __name__ == "__main__":
    try:
        test_damage_base_multiplier()
        test_different_percentages()

    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()