#!/usr/bin/env python3
# test_items_system.py - Test the new items system

from items import Item, EquipmentSlot, Equipment, CombatStats, assemble_fighter, create_default_modifiers, create_basic_equipment
from state.fighter_factory import create_fighter


def test_basic_item_creation():
    """Test creating basic items"""
    print("=== Testing Basic Item Creation ===")

    # Create a helm with head protection
    helm = Item(
        name="Steel Helm",
        slot=EquipmentSlot.HELM,
        modifiers={"head_protection": 0.05}
    )
    print(f"Created: {helm}")
    print(f"Head protection: {helm.get_modifier('head_protection')}")
    print()

    # Create a weapon with damage and crit
    sword = Item(
        name="Keen Blade",
        slot=EquipmentSlot.MAIN_HAND,
        modifiers={"damage_base": 2.0, "crit_chance": 0.1, "crit_power": 0.2}
    )
    print(f"Created: {sword}")
    print(f"Damage bonus: +{sword.get_modifier('damage_base')}")
    print(f"Crit chance bonus: +{sword.get_modifier('crit_chance'):.1%}")
    print(f"Crit power bonus: +{sword.get_modifier('crit_power'):.1%}")
    print()

    return helm, sword


def test_equipment_assembly():
    """Test equipment assembly"""
    print("=== Testing Equipment Assembly ===")

    # Create fighter
    fighter = create_fighter(hp_stat=12, attack_stat=10, defense_stat=8, agility_stat=10, role="TEST")
    base_stats = CombatStats.from_fighter_state(fighter)
    print(f"Base stats: {base_stats}")

    # Test without equipment
    final_stats, final_mods = assemble_fighter(base_stats, None)
    print(f"No equipment - Modifiers: {final_mods}")
    print()

    # Test with basic equipment
    equipment = create_basic_equipment()
    print(f"Equipment: {equipment.detailed_str()}")

    final_stats, final_mods = assemble_fighter(base_stats, equipment)
    print(f"With equipment - Modifiers: {final_mods}")
    print()

    return final_stats, final_mods


def test_zone_protection():
    """Test zone protection system"""
    print("=== Testing Zone Protection ===")

    from core.modules.zones import get_zone_multiplier, BASE_ZONE_MULTIPLIERS
    from items.modifiers import CombatModifiers

    # Test without protection
    base_legs = get_zone_multiplier("legs", None)
    print(f"Base legs multiplier: {base_legs}")

    # Test with protection
    mods = CombatModifiers(legs_protection=0.02)  # 2% protection
    protected_legs = get_zone_multiplier("legs", mods)
    print(f"With 2% protection: {protected_legs}")
    print(f"Damage reduction: {(base_legs - protected_legs) / base_legs:.1%}")
    print()


def test_modifiers_combination():
    """Test combining modifiers from multiple items"""
    print("=== Testing Modifier Combination ===")

    # Create items with overlapping modifiers
    helm = Item("Protective Helm", EquipmentSlot.HELM, {"head_protection": 0.03, "crit_chance": 0.05})
    armor = Item("Light Armor", EquipmentSlot.CUIRASS, {"chest_protection": 0.04, "dodge_chance": 0.1})
    weapon = Item("Magic Sword", EquipmentSlot.MAIN_HAND, {"damage_base": 3.0, "crit_chance": 0.08, "crit_power": 0.15})

    # Assemble equipment
    equipment = Equipment()
    equipment = equipment.equip_item(helm)
    equipment = equipment.equip_item(armor)
    equipment = equipment.equip_item(weapon)

    print(f"Equipment: {equipment}")

    # Test final modifiers
    base_stats = CombatStats(attack=10, defense=8, agility=12, hp=100)
    final_stats, final_mods = assemble_fighter(base_stats, equipment)

    print(f"Combined modifiers: {final_mods}")
    print(f"Total crit chance bonus: +{final_mods.crit_chance:.1%}")
    print(f"Total damage bonus: +{final_mods.damage_base}")
    print()


if __name__ == "__main__":
    print("🧪 ITEMS SYSTEM TEST")
    print("=" * 50)

    try:
        # Run tests
        test_basic_item_creation()
        test_equipment_assembly()
        test_zone_protection()
        test_modifiers_combination()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()