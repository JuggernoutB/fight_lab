# items/valuation.py - Item effectiveness and value assessment system

from typing import Dict, List, Tuple
from .item import Item
from .modifiers import CombatModifiers
from core.modules.ehp import EHPDamageCalculator


class ItemValuationSystem:
    """
    System for evaluating item effectiveness and relative value

    Philosophy:
    - Assigns numerical "value" to each modifier type
    - Allows comparison between different modifier types
    - Forms basis for item pricing, balance, and design decisions
    """

    def __init__(self):
        """Initialize with baseline evaluation parameters"""
        # Base stat levels for evaluation context
        self.baseline_stats = {
            "attack": 10,     # Average fighter attack
            "defense": 8,     # Average fighter defense
            "agility": 9,     # Average fighter agility
            "hp": 100         # Average fighter HP
        }

        # Value weights for different modifier types
        self.modifier_values = self._initialize_modifier_values()

    def _initialize_modifier_values(self) -> Dict[str, float]:
        """
        Initialize value weights for each modifier type

        Values represent relative importance/power of each modifier.
        These are baseline estimates that can be refined through testing.
        """
        return {
            # Zone protections (damage mitigation value)
            "head_protection": 80.0,      # Head is high-value target
            "chest_protection": 70.0,     # Common attack zone
            "abdomen_protection": 70.0,   # Common attack zone
            "hips_protection": 65.0,      # Medium frequency zone
            "legs_protection": 60.0,      # Lower frequency zone

            # Offensive modifiers (damage increase value)
            "damage_base": 100.0,         # Direct damage multiplier
            "crit_chance": 150.0,         # Crit very valuable
            "crit_power": 120.0,          # Crit power strong but conditional
            "block_break_chance": 90.0,   # Useful vs defensive enemies

            # Defensive modifiers (survival value)
            "dodge_chance": 130.0,        # Dodge very valuable
            "block_power": 75.0,          # Block decent but conditional

            # Utility modifiers
            "block_break_power": 50.0,    # Situational value
            "fatigue_efficiency": 85.0    # Stamina management value
        }

    def evaluate_item(self, item: Item) -> Dict[str, float]:
        """
        Evaluate an item's effectiveness

        Returns:
            Dict with evaluation metrics:
            - total_value: Overall item value score
            - modifier_breakdown: Value contribution per modifier
            - efficiency_score: Value per modifier point
            - category_focus: Primary category (offense/defense/utility)
        """
        breakdown = {}
        total_value = 0.0

        # Calculate value for each modifier
        for modifier_name, modifier_value in item.modifiers.items():
            if modifier_name in self.modifier_values:
                weight = self.modifier_values[modifier_name]
                contribution = abs(modifier_value) * weight
                breakdown[modifier_name] = contribution
                total_value += contribution

        # Determine category focus
        category_scores = self._categorize_modifiers(breakdown)
        primary_category = max(category_scores, key=category_scores.get) if category_scores else "none"

        # Calculate efficiency (value per modifier count)
        modifier_count = len(item.modifiers)
        efficiency = total_value / modifier_count if modifier_count > 0 else 0.0

        return {
            "total_value": total_value,
            "modifier_breakdown": breakdown,
            "efficiency_score": efficiency,
            "category_focus": primary_category,
            "category_scores": category_scores
        }

    def _categorize_modifiers(self, breakdown: Dict[str, float]) -> Dict[str, float]:
        """Categorize modifiers into offense/defense/utility"""
        categories = {"offense": 0.0, "defense": 0.0, "utility": 0.0}

        offense_modifiers = {"damage_base", "crit_chance", "crit_power", "block_break_chance", "block_break_power"}
        defense_modifiers = {"head_protection", "chest_protection", "abdomen_protection",
                           "hips_protection", "legs_protection", "dodge_chance", "block_power"}
        utility_modifiers = {"fatigue_efficiency"}

        for modifier_name, value in breakdown.items():
            if modifier_name in offense_modifiers:
                categories["offense"] += value
            elif modifier_name in defense_modifiers:
                categories["defense"] += value
            elif modifier_name in utility_modifiers:
                categories["utility"] += value

        return categories

    def compare_items(self, items: List[Item]) -> List[Tuple[Item, Dict]]:
        """
        Compare multiple items by effectiveness

        Returns:
            List of (item, evaluation) tuples sorted by total value
        """
        evaluations = []
        for item in items:
            evaluation = self.evaluate_item(item)
            evaluations.append((item, evaluation))

        # Sort by total value (highest first)
        evaluations.sort(key=lambda x: x[1]["total_value"], reverse=True)
        return evaluations

    def estimate_damage_impact(self, modifier_value: float, context_stats: Dict = None) -> float:
        """
        Estimate actual damage impact of damage_base modifier

        Args:
            modifier_value: The damage_base modifier value (e.g. 0.01 for +1%)
            context_stats: Fighter stats context (optional)

        Returns:
            Estimated damage increase per attack
        """
        stats = context_stats or self.baseline_stats
        calc = EHPDamageCalculator()

        # Calculate baseline damage
        base_damage = calc.calculate_damage_output(stats["attack"])

        # Calculate damage with modifier
        modified_damage = base_damage * (1.0 + modifier_value)

        # Return absolute increase
        return modified_damage - base_damage

    def generate_item_report(self, item: Item) -> str:
        """Generate detailed text report for an item"""
        evaluation = self.evaluate_item(item)

        lines = []
        lines.append(f"📊 ITEM EVALUATION: {item.name}")
        lines.append("=" * 50)

        lines.append(f"Slot: {item.slot.value}")
        lines.append(f"Total Value Score: {evaluation['total_value']:.1f}")
        lines.append(f"Efficiency Score: {evaluation['efficiency_score']:.1f}")
        lines.append(f"Primary Category: {evaluation['category_focus']}")

        lines.append("\n📋 MODIFIER BREAKDOWN:")
        for modifier, value in evaluation['modifier_breakdown'].items():
            original_value = item.modifiers[modifier]
            if modifier == "damage_base":
                lines.append(f"  {modifier}: +{original_value:.1%} → {value:.1f} value")
                # Add damage estimate
                damage_impact = self.estimate_damage_impact(original_value)
                lines.append(f"    Estimated damage increase: +{damage_impact:.2f} per attack")
            else:
                lines.append(f"  {modifier}: {original_value:+.3f} → {value:.1f} value")

        lines.append("\n🏷️ CATEGORY DISTRIBUTION:")
        for category, score in evaluation['category_scores'].items():
            percentage = score / evaluation['total_value'] * 100 if evaluation['total_value'] > 0 else 0
            lines.append(f"  {category.capitalize()}: {score:.1f} ({percentage:.1f}%)")

        return "\n".join(lines)


# Global valuation instance
_valuation_system = ItemValuationSystem()


def evaluate_item(item: Item) -> Dict[str, float]:
    """Convenience function to evaluate single item"""
    return _valuation_system.evaluate_item(item)


def compare_items(items: List[Item]) -> List[Tuple[Item, Dict]]:
    """Convenience function to compare items"""
    return _valuation_system.compare_items(items)


def generate_item_report(item: Item) -> str:
    """Convenience function to generate item report"""
    return _valuation_system.generate_item_report(item)