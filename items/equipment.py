# items/equipment.py - Equipment system and build assembly pipeline

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from .item import Item, EquipmentSlot
from .modifiers import CombatModifiers, create_default_modifiers, modifiers_from_item_dict


@dataclass
class CombatStats:
    """
    Base combat stats (separation from items)

    These are the core fighter attributes independent of equipment
    """
    attack: float
    defense: float
    agility: float
    hp: float

    @classmethod
    def from_fighter_state(cls, fighter_state):
        """Create CombatStats from existing FighterState"""
        hp_stat = getattr(fighter_state, 'hp_stat', fighter_state.hp)  # Use hp_stat if available
        return cls(
            attack=float(fighter_state.attack),
            defense=float(fighter_state.defense),
            agility=float(fighter_state.agility),
            hp=float(hp_stat)
        )

    def __str__(self) -> str:
        return f"ATK:{self.attack:.1f} DEF:{self.defense:.1f} AGI:{self.agility:.1f} HP:{self.hp:.1f}"


@dataclass
class Equipment:
    """
    Equipment set containing items in all 7 slots

    Slots:
    1. HELM - head protection
    2. CUIRASS - chest protection
    3. MIDPLATE - abdomen protection
    4. WAISTGUARD - hips protection
    5. GREAVES - legs protection
    6. MAIN_HAND - primary weapon
    7. OFF_HAND - secondary weapon/shield
    """
    helm: Optional[Item] = None
    cuirass: Optional[Item] = None
    midplate: Optional[Item] = None
    waistguard: Optional[Item] = None
    greaves: Optional[Item] = None
    main_hand: Optional[Item] = None
    off_hand: Optional[Item] = None

    def get_items(self) -> List[Item]:
        """Get list of all equipped items (non-None)"""
        items = []
        for item in [self.helm, self.cuirass, self.midplate, self.waistguard,
                    self.greaves, self.main_hand, self.off_hand]:
            if item is not None:
                items.append(item)
        return items

    def get_item_by_slot(self, slot: EquipmentSlot) -> Optional[Item]:
        """Get item in specific slot"""
        slot_mapping = {
            EquipmentSlot.HELM: self.helm,
            EquipmentSlot.CUIRASS: self.cuirass,
            EquipmentSlot.MIDPLATE: self.midplate,
            EquipmentSlot.WAISTGUARD: self.waistguard,
            EquipmentSlot.GREAVES: self.greaves,
            EquipmentSlot.MAIN_HAND: self.main_hand,
            EquipmentSlot.OFF_HAND: self.off_hand
        }
        return slot_mapping.get(slot)

    def equip_item(self, item: Item) -> 'Equipment':
        """Equip item in appropriate slot, returns new Equipment instance"""
        new_equipment = Equipment(
            helm=self.helm,
            cuirass=self.cuirass,
            midplate=self.midplate,
            waistguard=self.waistguard,
            greaves=self.greaves,
            main_hand=self.main_hand,
            off_hand=self.off_hand
        )

        # Set item in appropriate slot
        if item.slot == EquipmentSlot.HELM:
            new_equipment.helm = item
        elif item.slot == EquipmentSlot.CUIRASS:
            new_equipment.cuirass = item
        elif item.slot == EquipmentSlot.MIDPLATE:
            new_equipment.midplate = item
        elif item.slot == EquipmentSlot.WAISTGUARD:
            new_equipment.waistguard = item
        elif item.slot == EquipmentSlot.GREAVES:
            new_equipment.greaves = item
        elif item.slot == EquipmentSlot.MAIN_HAND:
            new_equipment.main_hand = item
        elif item.slot == EquipmentSlot.OFF_HAND:
            new_equipment.off_hand = item

        return new_equipment

    def __str__(self) -> str:
        equipped_count = len(self.get_items())
        return f"Equipment({equipped_count}/7 slots)"

    def detailed_str(self) -> str:
        """Detailed equipment listing"""
        lines = ["Equipment:"]
        slot_items = [
            ("HELM", self.helm),
            ("CUIRASS", self.cuirass),
            ("MIDPLATE", self.midplate),
            ("WAISTGUARD", self.waistguard),
            ("GREAVES", self.greaves),
            ("MAIN_HAND", self.main_hand),
            ("OFF_HAND", self.off_hand)
        ]

        for slot_name, item in slot_items:
            if item:
                lines.append(f"  {slot_name}: {item.name}")
            else:
                lines.append(f"  {slot_name}: (empty)")

        return "\n".join(lines)


def apply_item_to_modifiers(base_modifiers: CombatModifiers, item: Item) -> CombatModifiers:
    """Apply single item's modifiers to existing modifier set"""
    item_mods = modifiers_from_item_dict(item.modifiers)
    return base_modifiers.add_modifiers(item_mods)


def assemble_fighter(base_stats: CombatStats, equipment: Optional[Equipment] = None) -> Tuple[CombatStats, CombatModifiers]:
    """
    Build assembly pipeline: combine base stats with equipment modifiers

    Args:
        base_stats: Base fighter stats (attack, defense, agility, hp)
        equipment: Equipment set (optional, defaults to empty)

    Returns:
        Tuple of (final_stats, final_modifiers)

    Note: Currently stats aren't modified by items (pure modifiers),
          but this pipeline allows for future stat modifications
    """
    # Start with base stats (currently unchanged by equipment)
    final_stats = base_stats

    # Start with default (empty) modifiers
    final_modifiers = create_default_modifiers()

    # Apply each equipped item's modifiers
    if equipment:
        for item in equipment.get_items():
            final_modifiers = apply_item_to_modifiers(final_modifiers, item)

    return final_stats, final_modifiers


def assemble_fighter_from_state(fighter_state, equipment: Optional[Equipment] = None) -> Tuple[CombatStats, CombatModifiers]:
    """
    Convenience function to assemble fighter from existing FighterState

    Args:
        fighter_state: Existing FighterState object
        equipment: Equipment set (optional)

    Returns:
        Tuple of (combat_stats, combat_modifiers)
    """
    base_stats = CombatStats.from_fighter_state(fighter_state)
    return assemble_fighter(base_stats, equipment)


# Factory functions for common equipment setups

def create_empty_equipment() -> Equipment:
    """Create completely empty equipment set"""
    return Equipment()


def create_basic_equipment() -> Equipment:
    """Create basic starter equipment set for testing"""
    return Equipment(
        helm=Item("Basic Helm", EquipmentSlot.HELM, {"head_protection": 0.01}),
        cuirass=Item("Basic Cuirass", EquipmentSlot.CUIRASS, {"chest_protection": 0.02}),
        main_hand=Item("Basic Sword", EquipmentSlot.MAIN_HAND, {"damage_base": 1.0})
    )