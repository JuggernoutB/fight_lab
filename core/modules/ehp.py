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