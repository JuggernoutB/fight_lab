# core/config.py
# Centralized configuration for the combat system
# All balance parameters in one place for easy tuning

CONFIG = {
    # ============================================================
    # CRITICAL HITS
    # ============================================================
    "base_crit_chance": 0.01,         # Base crit chance
    "agi_diff_crit_scale": 0.05,     # Agility difference scaling for crit
    "crit_damage_multiplier": 1.5,    # Damage multiplier for crits
    "min_crit_chance": 0.05,         # Minimum possible crit chance
    "max_crit_chance": 0.51,          # Maximum possible crit chance

    # ============================================================
    # DODGE
    # ============================================================
    "base_dodge_chance": 0.05,        # Base dodge chance
    "agi_diff_dodge_scale": 0.025,     # Agility difference scaling for dodge
    "min_dodge_chance": 0.05,         # Minimum possible dodge chance
    "max_dodge_chance": 0.3,          # Maximum possible dodge chance

    # ============================================================
    # BLOCKING
    # ============================================================
    "base_block_reduction": 0.1,     # Base damage reduction from blocking
    "def_diff_block_scale": 0.075,    # Defense difference scaling for blocking
    "min_block_reduction": 0.1,       # Minimum block damage reduction
    "max_block_reduction": 0.85,       # Maximum block damage reduction
    "base_block_break_chance": 0.025,  # Base block break chance
    "agi_block_break_scale": 0.05,    # Agility scaling for block break
    "min_block_break_chance": 0.1,   # Minimum block break chance
    "max_block_break_chance": 0.525,    # Maximum block break chance
    "block_break_damage_ratio": 0.75,  # Damage ratio when block is broken

    # ============================================================
    # FATIGUE SYSTEM
    # ============================================================
    "stamina_fresh_threshold": 70,    # Above this = Fresh (no penalties)
    "stamina_tired_threshold": 30,    # Above this = Tired, below = Exhausted
    "fresh_multiplier": 1.0,          # No fatigue penalty (100%)
    "tired_multiplier": 0.75,         # Tired penalty (75% effectiveness)
    "exhausted_multiplier": 0.5,      # Exhausted penalty (50% effectiveness)


    # ============================================================
    # STAMINA SYSTEM
    # ============================================================
    "initial_stamina": 100,           # Maximum stamina points
    "attack_stamina_cost_per_zone": 6,  # Stamina cost per attack zone
    "defense_stamina_cost_per_zone": 3, # Stamina cost per defense zone
    "stamina_regen_per_round": 4,     # Stamina regenerated per round

    # Action-based stamina costs (for successful mechanics)
    "stamina_cost_dodge": 5,          # Stamina cost for successful dodge
    "stamina_cost_crit": 5,           # Stamina cost for successful critical hit
    "stamina_cost_block_break": 4,    # Stamina cost for successful block break

    # ============================================================
    # EHP SCALING
    # ============================================================
    "hp_scaling_base": 10.0,         # Base health multiplier
    "hp_scaling_constant": 24,        # Constant added to health stat
    "hp_scaling_exponent": 0.68,      # Exponent for health scaling curve
    "damage_scaling_base": 1.4,      # Base damage multiplier
    "damage_scaling_constant": 50.0,    # Constant added to attack stat
    "damage_scaling_exponent": 0.55,  # Exponent for damage scaling curve
    "defense_scaling_multiplier": 40.0, # Defense stat divider for EHP calculation
    "defense_scaling_exponent": 1.1, # Exponent for defense scaling curve

    # ============================================================
    # DEFENSE (EHP INTEGRATION)
    # ============================================================
    "defense_effectiveness": 0.35,
}