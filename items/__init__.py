# items/__init__.py - Equipment system for fight lab

from .item import Item, EquipmentSlot
from .modifiers import CombatModifiers, create_default_modifiers
from .equipment import Equipment, CombatStats, assemble_fighter, create_basic_equipment

__all__ = [
    'Item',
    'EquipmentSlot',
    'CombatModifiers',
    'create_default_modifiers',
    'Equipment',
    'CombatStats',
    'assemble_fighter',
    'create_basic_equipment'
]