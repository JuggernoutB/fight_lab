# core/stamina.py - Stamina system

from typing import List
from ..config import CONFIG

DEFAULT_ZONE = "chest"            # Default zone for action conversion

# Legacy exports for backwards compatibility
ATTACK_COST = CONFIG["attack_stamina_cost_per_zone"]
DEFENSE_COST = CONFIG["defense_stamina_cost_per_zone"]
REGEN = CONFIG["stamina_regen_per_round"]

def get_initial_stamina() -> int:
      """Get initial stamina value for new fighters"""
      return CONFIG["initial_stamina"]

def calculate_action_cost(atk_zones: List[str], def_zones: List[str]) -> int:
    return len(atk_zones) * ATTACK_COST + len(def_zones) * DEFENSE_COST

def can_act(stamina: int, atk_zones: List[str], def_zones: List[str]) -> bool:
    return stamina >= calculate_action_cost(atk_zones, def_zones)

def update_stamina(stamina: int, atk_zones: List[str], def_zones: List[str]) -> int:
    cost = calculate_action_cost(atk_zones, def_zones)
    stamina = stamina - cost + REGEN
    return max(0, min(CONFIG["initial_stamina"], stamina))

def apply_stamina(stamina: int, action: dict) -> int:
    """Apply stamina changes based on action dictionary"""
    # Handle both formats: {"attack": 2, "defense": 1} and {"attack_zones": [...], "defense_zones": [...]}
    if "attack_zones" in action:
        atk_zones = action["attack_zones"]
        def_zones = action.get("defense_zones", [])
    else:
        # Convert numbers to zone lists (legacy format from role_engine)
        attack_count = action.get("attack", 0)
        defense_count = action.get("defense", 0)

        # Create zone lists based on counts
        atk_zones = [DEFAULT_ZONE] * attack_count  # Use default zone for attacks
        def_zones = [DEFAULT_ZONE] * defense_count # Use default zone for defense

    return update_stamina(stamina, atk_zones, def_zones)