# core/ehp.py - Effective Health Points damage model

from ..config import CONFIG

class EHPDamageCalculator:

    def calculate_base_hp(self, hp_stat: int) -> float:
        return CONFIG["hp_scaling_base"] * ((hp_stat + CONFIG["hp_scaling_constant"]) ** CONFIG["hp_scaling_exponent"])

    def calculate_damage_output(self, attack_stat: int) -> float:
        return CONFIG["damage_scaling_base"] * ((attack_stat + CONFIG["damage_scaling_constant"]) ** CONFIG["damage_scaling_exponent"])

    def calculate_ehp(self, hp_stat: int, defense_stat: int) -> float:
        base_hp = self.calculate_base_hp(hp_stat)
        return base_hp * (1 + (defense_stat / CONFIG["defense_scaling_multiplier"]) ** CONFIG["defense_scaling_exponent"])


def calculate_defense_multiplier(defense_stat: int) -> float:
    """Calculate defense multiplier for damage reduction"""
    base_mult = (defense_stat / CONFIG["defense_scaling_multiplier"]) ** CONFIG["defense_scaling_exponent"]
    return base_mult * CONFIG["defense_effectiveness"]


def apply_defense_reduction(damage: float, defense_stat: int) -> float:
    """Apply defense-based damage reduction (hidden EHP implementation)"""
    defense_mult = calculate_defense_multiplier(defense_stat)
    return damage / (1 + defense_mult)


def calculate_absorption_efficiency(defense_stat: int) -> float:
    """Calculate how efficiently defense converts absorbed damage to resource"""
    base_efficiency = 1.0
    defense_mult = calculate_defense_multiplier(defense_stat)
    return base_efficiency + (defense_mult * 0.5)  # Conservative boost to absorption efficiency