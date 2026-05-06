# items/catalog.py - Item catalog with predefined items

from .item import Item, EquipmentSlot


def create_wooden_sword() -> Item:
    """
    Create Wooden Sword - basic weapon with +1% damage

    Design philosophy:
    - Minimal but measurable damage boost
    - Entry-level weapon for testing
    - Sets baseline for item value calculations
    """
    return Item(
        name="Wooden Sword",
        slot=EquipmentSlot.MAIN_HAND,
        modifiers={"damage_base": 0.01}  # +1% damage multiplier
    )


# Item catalog for easy access
ITEM_CATALOG = {
    "wooden_sword": create_wooden_sword(),
}


def get_item(item_id: str) -> Item:
    """Get item from catalog by ID"""
    if item_id not in ITEM_CATALOG:
        available = list(ITEM_CATALOG.keys())
        raise ValueError(f"Item '{item_id}' not found. Available: {available}")

    return ITEM_CATALOG[item_id]


def list_available_items() -> dict:
    """Get all available items"""
    return ITEM_CATALOG.copy()