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
        level=2,
        modifiers={"damage_base": 0.01}  # +1% base damage
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
          level=2,
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
          level=2,
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
          level=2,
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
          level=2,
          modifiers={"damage_base": 0.50}  # +50% base damage multiplier
      )


def create_endurance_ring() -> Item:
      """
      Create Endurance Ring - accessory with light fatigue resistance

      Design philosophy:
      - Noticeable but not overpowered fatigue efficiency (+2%)
      - Perfect for testing fatigue_efficiency mechanics
      - Sustained pressure advantage without direct DPS boost
      """
      return Item(
          name="Endurance Ring",
          slot=EquipmentSlot.OFF_HAND,
          level=2,
          modifiers={"fatigue_efficiency": 0.02}  # 2% fatigue penalty reduction
      )


def create_stamina_amulet() -> Item:
      """
      Create Stamina Amulet - powerful fatigue resistance item

      Design philosophy:
      - Strong fatigue efficiency (+5%) for meaningful impact
      - Tank/Bruiser style equipment for long fights
      - Significant sustained performance improvement
      """
      return Item(
          name="Stamina Amulet",
          slot=EquipmentSlot.OFF_HAND,
          level=2,
          modifiers={"fatigue_efficiency": 0.05}  # 5% fatigue penalty reduction
      )


def create_marathon_boots() -> Item:
      """
      Create Marathon Boots - very strong endurance equipment

      Design philosophy:
      - Very strong fatigue efficiency (+10%) for extreme testing
      - Demonstrates upper limit of balanced fatigue_efficiency
      - Shows maximum sustainable advantage without breaking balance
      """
      return Item(
          name="Marathon Boots",
          slot=EquipmentSlot.GREAVES,
          level=2,
          modifiers={"fatigue_efficiency": 0.10}  # 10% fatigue penalty reduction
      )


def create_block_breaker_sword() -> Item:
    """
    Create Block Breaker Sword - weapon with enhanced critical power

    Design philosophy:
    - High critical power for testing against defensive opponents
    - Specialized weapon for burst damage
    - Focus on crit effectiveness rather than block breaking
    """
    return Item(
        name="Critical Sword",
        slot=EquipmentSlot.MAIN_HAND,
        level=2,
        modifiers={"crit_power": 0.25}  # +25% critical power
    )


def create_master_critical_sword() -> Item:
    """
    Create Master Critical Sword - extreme critical weapon

    Design philosophy:
    - Very high critical chance for extreme testing
    - Shows maximum effectiveness of crit_chance
    - Tests upper limits of critical mechanics
    """
    return Item(
        name="Master Critical Sword",
        slot=EquipmentSlot.MAIN_HAND,
        level=2,
        modifiers={"crit_chance": 0.15}  # +15% critical chance
    )


# Item catalog for easy access
ITEM_CATALOG = {
    # Damage weapons
    "wooden_sword": create_wooden_sword(),
    "iron_sword": create_iron_sword(),
    "steel_sword": create_steel_sword(),
    "super_sword": create_super_sword(),
    "absolute_sword": create_absolute_sword(),
    # Fatigue efficiency items
    "endurance_ring": create_endurance_ring(),
    "stamina_amulet": create_stamina_amulet(),
    "marathon_boots": create_marathon_boots(),
    # Critical weapons
    "critical_sword": create_block_breaker_sword(),
    "master_critical_sword": create_master_critical_sword(),
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