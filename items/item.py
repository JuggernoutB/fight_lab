# items/item.py - Core item and slot definitions

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class EquipmentSlot(Enum):
    """Equipment slot types"""
    HELM = "helm"
    CUIRASS = "cuirass"
    MIDPLATE = "midplate"
    WAISTGUARD = "waistguard"
    GREAVES = "greaves"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"


@dataclass
class Item:
    """
    Data-driven item with modifiers and level

    Examples:
        # Heavy helm with head protection (level 3)
        Item(
            name="Steel Helm",
            slot=EquipmentSlot.HELM,
            level=3,
            modifiers={"head_protection": 0.05}
        )

        # Critical damage sword (level 2)
        Item(
            name="Keen Blade",
            slot=EquipmentSlot.MAIN_HAND,
            level=2,
            modifiers={"crit_power": 0.2, "damage_base": 2.0}
        )

        # Nimble boots with negative defense (level 1)
        Item(
            name="Swift Boots",
            slot=EquipmentSlot.GREAVES,
            level=1,
            modifiers={"dodge_chance": 0.15, "legs_protection": -0.02}
        )
    """
    name: str
    slot: EquipmentSlot
    level: int
    modifiers: Dict[str, float]

    def __post_init__(self):
        """Validate item modifiers"""
        valid_modifiers = {
            # Zone protections
            "head_protection",
            "chest_protection",
            "abdomen_protection",
            "hips_protection",
            "legs_protection",
            # Combat modifiers
            "damage_base",
            "crit_chance",
            "dodge_chance",
            "crit_power",
            "block_break_power",
            "block_power",
            "fatigue_efficiency"
        }

        for modifier in self.modifiers:
            if modifier not in valid_modifiers:
                raise ValueError(f"Invalid modifier '{modifier}' in item '{self.name}'. Valid modifiers: {valid_modifiers}")

    def get_modifier(self, modifier_name: str) -> float:
        """Get modifier value, returns 0.0 if not present"""
        return self.modifiers.get(modifier_name, 0.0)

    def __str__(self) -> str:
        return f"{self.name} ({self.slot.value})"

    def __repr__(self) -> str:
        return f"Item(name='{self.name}', slot={self.slot}, modifiers={self.modifiers})"