# items/__init__.py - Equipment system for fight lab

from .item import Item, EquipmentSlot
from .modifiers import CombatModifiers, create_default_modifiers
from .equipment import Equipment, CombatStats, assemble_fighter, assemble_fighter_from_state, create_basic_equipment
from .catalog import get_item, list_available_items, create_wooden_sword

__all__ = [
    'Item',
    'EquipmentSlot',
    'CombatModifiers',
    'create_default_modifiers',
    'Equipment',
    'CombatStats',
    'assemble_fighter',
    'assemble_fighter_from_state',
    'create_basic_equipment',
    'get_item',
    'list_available_items',
    'create_wooden_sword'
]