# core/ehp.py - Effective Health Points damage model

from ..config import CONFIG

class EHPDamageCalculator:

    def calculate_base_hp(self, hp_stat: int) -> float:
        return CONFIG["hp_scaling_base"] * ((hp_stat + CONFIG["hp_scaling_constant"]) ** CONFIG["hp_scaling_exponent"])

    def calculate_damage_output(self, attack_stat: int) -> float:
        return CONFIG["damage_scaling_base"] * ((attack_stat + CONFIG["damage_scaling_constant"]) ** CONFIG["damage_scaling_exponent"])



def calculate_defense_multiplier(defense_stat: int) -> float:
    """Calculate defense multiplier for damage reduction"""
    base_mult = (defense_stat / CONFIG["defense_scaling_multiplier"]) ** CONFIG["defense_scaling_exponent"]
    return base_mult * CONFIG["defense_effectiveness"]


def apply_defense_reduction(damage: float, defense_stat: int) -> float:
    """Apply defense-based damage reduction (hidden EHP implementation)"""
    defense_mult = calculate_defense_multiplier(defense_stat)
    return damage / (1 + defense_mult)


