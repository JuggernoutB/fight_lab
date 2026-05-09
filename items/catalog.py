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

def create_iron_sword() -> Item:
      """
      Create Iron Sword - improved weapon with +5% base damage

      Design philosophy:
      - Moderate base damage boost
      - Tier 2 weapon for mid-game
      """
      return Item(
          name="Iron Sword",
          slot=EquipmentSlot.MAIN_HAND,
          modifiers={"damage_base": 0.05}  # +5% base damage multiplier
      )


def create_steel_sword() -> Item:
      """
      Create Steel Sword - powerful weapon with +15% base damage

      Design philosophy:
      - Strong base damage boost
      - Tier 3 weapon for late-game testing
      """
      return Item(
          name="Steel Sword",
          slot=EquipmentSlot.MAIN_HAND,
          modifiers={"damage_base": 0.15}  # +15% base damage multiplier
      )


def create_super_sword() -> Item:
      """
      Create Super Sword - extreme weapon with +100% base damage for testing

      Design philosophy:
      - Testing extreme damage modifiers
      - Verify system limits and effectiveness
      """
      return Item(
          name="Super Sword",
          slot=EquipmentSlot.MAIN_HAND,
          modifiers={"damage_base": 1.0}  # +100% base damage multiplier
      )


def create_absolute_sword() -> Item:
      """
      Create Absolute Sword - weapon with +50% base damage

      Design philosophy:
      - High-tier base damage boost
      - Strong weapon for late-game testing
      """
      return Item(
          name="Absolute Sword",
          slot=EquipmentSlot.MAIN_HAND,
          modifiers={"damage_base": 0.50}  # +50% base damage multiplier
      )


# Item catalog for easy access
ITEM_CATALOG = {
    "wooden_sword": create_wooden_sword(),
    "iron_sword": create_iron_sword(),
    "steel_sword": create_steel_sword(),
    "super_sword": create_super_sword(),
    "absolute_sword": create_absolute_sword(),
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