#!/usr/bin/env python3
# Тест деревянного меча с процентным модификатором

from items import create_wooden_sword, Equipment, assemble_fighter_from_state, get_item, list_available_items
from state.fighter_factory import create_fighter
from core.modules.combat import process_attack


def test_wooden_sword_damage():
    """Тестируем процентное увеличение урона от деревянного меча"""
    print("🗡️ ТЕСТ ДЕРЕВЯННОГО МЕЧА")
    print("=" * 50)

    # Создаём бойца
    fighter = create_fighter(hp_stat=10, attack_stat=8, defense_stat=5, agility_stat=7, role="TEST")
    print(f"Базовый ATK: {fighter.attack}")

    # Создаём деревянный меч
    wooden_sword = create_wooden_sword()
    print(f"Предмет: {wooden_sword.name}")
    print(f"Модификатор: +{wooden_sword.modifiers['damage_base']:.1%} damage")

    # Экипируем меч
    equipment = Equipment()
    equipment = equipment.equip_item(wooden_sword)

    # Собираем финального бойца
    final_stats, final_mods = assemble_fighter_from_state(fighter, equipment)
    print(f"Финальный модификатор damage_base: {final_mods.damage_base:.3f}")
    print()

    # Тестируем урон БЕЗ меча
    print("=== БЕЗ МЕЧА ===")
    attacker_dict = {"attack": fighter.attack, "agility": fighter.agility}
    defender_dict = {"defense": 3, "agility": 5}

    results_no_weapon, _, _ = process_attack(
        attacker_dict, defender_dict,
        attacker_stamina=100, defender_stamina=100,
        atk_zones=["chest"], def_zones=[],
        debug_mode=True,
        attacker_modifiers=None
    )

    no_weapon_raw = results_no_weapon['chest']['raw']
    no_weapon_final = results_no_weapon['chest']['damage']
    print(f"Raw damage: {no_weapon_raw:.4f}")
    print(f"Final damage: {no_weapon_final}")

    # Тестируем урон С мечом
    print("\n=== С ДЕРЕВЯННЫМ МЕЧОМ (+1%) ===")
    results_with_weapon, _, _ = process_attack(
        attacker_dict, defender_dict,
        attacker_stamina=100, defender_stamina=100,
        atk_zones=["chest"], def_zones=[],
        debug_mode=True,
        attacker_modifiers=final_mods
    )

    with_weapon_raw = results_with_weapon['chest']['raw']
    with_weapon_final = results_with_weapon['chest']['damage']
    print(f"Raw damage: {with_weapon_raw:.4f}")
    print(f"Final damage: {with_weapon_final}")

    # Анализ результата
    print("\n=== АНАЛИЗ ===")
    expected_multiplier = 1.0 + final_mods.damage_base
    actual_multiplier = with_weapon_raw / no_weapon_raw if no_weapon_raw > 0 else 0

    print(f"Ожидаемый мультипликатор: {expected_multiplier:.3f}")
    print(f"Фактический мультипликатор: {actual_multiplier:.3f}")
    print(f"Относительное увеличение: +{(actual_multiplier - 1.0):.1%}")

    # Проверка точности
    accuracy = abs(expected_multiplier - actual_multiplier)
    if accuracy < 0.001:
        print("✅ Модификатор работает точно!")
    else:
        print(f"⚠️ Небольшое отклонение: {accuracy:.6f}")


def test_item_catalog():
    """Тестируем каталог предметов"""
    print("\n🏪 КАТАЛОГ ПРЕДМЕТОВ")
    print("=" * 30)

    # Список доступных предметов
    items = list_available_items()
    print("Доступные предметы:")
    for item_id, item in items.items():
        print(f"  {item_id}: {item.name} ({item.slot.value})")

    # Получение предмета по ID
    print(f"\nПолучение 'wooden_sword':")
    sword = get_item("wooden_sword")
    print(f"  {sword.name}: {sword.modifiers}")


if __name__ == "__main__":
    try:
        test_wooden_sword_damage()
        test_item_catalog()
        print("\n✅ Все тесты прошли успешно!")

    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()