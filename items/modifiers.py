# items/modifiers.py - Combat modifiers system

from dataclasses import dataclass
from typing import Dict


@dataclass
class CombatModifiers:
    """
    Combat modifiers that affect battle calculations

    All modifiers are additive bonuses:
    - Zone protections: reduce zone damage multipliers (0.95 - 0.01 = 0.94)
    - Combat bonuses: add to base chances/powers (+10% crit, +20% power, etc.)
    - Negative values supported for penalties
    """

    # Zone protections (reduce zone damage multipliers)
    head_protection: float = 0.0
    chest_protection: float = 0.0
    abdomen_protection: float = 0.0
    hips_protection: float = 0.0
    legs_protection: float = 0.0

    # Combat modifiers
    damage_base: float = 0.0           # Base damage multiplier bonus (0.01 = +1%)
    crit_chance: float = 0.0           # Additional crit chance (+10% = 0.1)
    dodge_chance: float = 0.0          # Additional dodge chance
    crit_power: float = 0.0            # Additional crit multiplier (base 1.5x + modifier)
    block_power: float = 0.0           # Additional block effectiveness
    fatigue_efficiency: float = 0.0    # Fatigue resistance (affects tired/exhausted multipliers)

    def add_modifiers(self, other: 'CombatModifiers') -> 'CombatModifiers':
        """Add another set of modifiers to this one (for combining items)"""
        return CombatModifiers(
            # Zone protections
            head_protection=self.head_protection + other.head_protection,
            chest_protection=self.chest_protection + other.chest_protection,
            abdomen_protection=self.abdomen_protection + other.abdomen_protection,
            hips_protection=self.hips_protection + other.hips_protection,
            legs_protection=self.legs_protection + other.legs_protection,

            # Combat modifiers
            damage_base=self.damage_base + other.damage_base,
            crit_chance=self.crit_chance + other.crit_chance,
            dodge_chance=self.dodge_chance + other.dodge_chance,
            crit_power=self.crit_power + other.crit_power,
            block_power=self.block_power + other.block_power,
            fatigue_efficiency=self.fatigue_efficiency + other.fatigue_efficiency
        )

    def get_zone_protection(self, zone: str) -> float:
        """Get protection value for specific zone"""
        zone_mapping = {
            "head": self.head_protection,
            "chest": self.chest_protection,
            "abdomen": self.abdomen_protection,
            "hips": self.hips_protection,
            "legs": self.legs_protection
        }
        return zone_mapping.get(zone, 0.0)

    def get_adjusted_fatigue_multipliers(self, base_tired: float = 0.75, base_exhausted: float = 0.5) -> tuple[float, float]:
        """
        Calculate adjusted fatigue multipliers based on fatigue_efficiency

        Positive efficiency = better fatigue resistance (higher multipliers)
        Negative efficiency = worse fatigue resistance (lower multipliers)

        Args:
            base_tired: Base tired multiplier (default 0.75)
            base_exhausted: Base exhausted multiplier (default 0.5)

        Returns:
            Tuple of (adjusted_tired, adjusted_exhausted)
        """
        # Apply efficiency bonus/penalty
        adjusted_tired = min(1.0, max(0.1, base_tired + self.fatigue_efficiency))
        adjusted_exhausted = min(1.0, max(0.1, base_exhausted + self.fatigue_efficiency))

        return adjusted_tired, adjusted_exhausted

    def __str__(self) -> str:
        """String representation showing non-zero modifiers"""
        parts = []

        # Zone protections
        zones = {
            "head": self.head_protection,
            "chest": self.chest_protection,
            "abdomen": self.abdomen_protection,
            "hips": self.hips_protection,
            "legs": self.legs_protection
        }
        for zone, value in zones.items():
            if value != 0.0:
                parts.append(f"{zone}_prot:{value:+.3f}")

        # Combat modifiers
        combat = {
            "dmg_base": self.damage_base,
            "crit_ch": self.crit_chance,
            "dodge_ch": self.dodge_chance,
            "crit_pow": self.crit_power,
            "block_pow": self.block_power,
            "fatigue_eff": self.fatigue_efficiency
        }
        for name, value in combat.items():
            if value != 0.0:
                parts.append(f"{name}:{value:+.3f}")

        return " ".join(parts) if parts else "no_modifiers"


def create_default_modifiers() -> CombatModifiers:
    """Create default (empty) combat modifiers for existing fighters"""
    return CombatModifiers()


def modifiers_from_item_dict(item_modifiers: Dict[str, float]) -> CombatModifiers:
    """Create CombatModifiers from item's modifier dictionary"""
    return CombatModifiers(
        # Zone protections
        head_protection=item_modifiers.get("head_protection", 0.0),
        chest_protection=item_modifiers.get("chest_protection", 0.0),
        abdomen_protection=item_modifiers.get("abdomen_protection", 0.0),
        hips_protection=item_modifiers.get("hips_protection", 0.0),
        legs_protection=item_modifiers.get("legs_protection", 0.0),

        # Combat modifiers
        damage_base=item_modifiers.get("damage_base", 0.0),
        crit_chance=item_modifiers.get("crit_chance", 0.0),
        dodge_chance=item_modifiers.get("dodge_chance", 0.0),
        crit_power=item_modifiers.get("crit_power", 0.0),
        block_power=item_modifiers.get("block_power", 0.0),
        fatigue_efficiency=item_modifiers.get("fatigue_efficiency", 0.0)
    )