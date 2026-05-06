#!/usr/bin/env python3
# Пример применения damage_base модификатора

from items import Item, EquipmentSlot, Equipment, assemble_fighter_from_state
from state.fighter_factory import create_fighter
from core.modules.combat import process_attack

# 1. Создаём бойца
fighter = create_fighter(hp_stat=10, attack_stat=6, defense_stat=5, agility_stat=8, role="TEST")
print(f"Base fighter ATK: {fighter.attack}")

# 2. Создаём оружие с damage_base
weapon = Item(
    name="Magic Sword +3",
    slot=EquipmentSlot.MAIN_HAND,
    modifiers={"damage_base": 3.0}  # +3 урона
)

# 3. Экипируем оружие
equipment = Equipment()
equipment = equipment.equip_item(weapon)

# 4. Собираем финального бойца
final_stats, final_mods = assemble_fighter_from_state(fighter, equipment)
print(f"Equipment damage bonus: +{final_mods.damage_base}")

# 5. Тестируем урон БЕЗ оружия
print("\n=== БЕЗ ОРУЖИЯ ===")
attacker_dict = {"attack": fighter.attack, "agility": fighter.agility}
defender_dict = {"defense": 3, "agility": 5}

results_no_weapon, _, _ = process_attack(
    attacker_dict, defender_dict,
    attacker_stamina=100, defender_stamina=100,
    atk_zones=["chest"], def_zones=[],
    debug_mode=True,
    attacker_modifiers=None  # НЕТ модификаторов
)

print(f"Урон без оружия: {results_no_weapon['chest']['damage']}")
print(f"Raw damage: {results_no_weapon['chest']['raw']:.2f}")

# 6. Тестируем урон С оружием
print("\n=== С ОРУЖИЕМ (+3 damage) ===")
results_with_weapon, _, _ = process_attack(
    attacker_dict, defender_dict,
    attacker_stamina=100, defender_stamina=100,
    atk_zones=["chest"], def_zones=[],
    debug_mode=True,
    attacker_modifiers=final_mods  # С модификаторами от оружия
)

print(f"Урон с оружием: {results_with_weapon['chest']['damage']}")
print(f"Raw damage: {results_with_weapon['chest']['raw']:.2f}")

# 7. Показываем разницу
damage_increase = results_with_weapon['chest']['raw'] - results_no_weapon['chest']['raw']
print(f"\n🔥 Увеличение урона от оружия: +{damage_increase:.2f}")