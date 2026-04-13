# core/config.py
# Centralized configuration for the combat system
# All balance parameters in one place for easy tuning

CONFIG = {
    # ============================================================
    # ENGINE
    # ============================================================
    "block_break_damage_ratio": 0.85,  # Damage ratio when block is broken (85%)

    # ============================================================
    # CRITICAL HITS
    # ============================================================
    "base_crit_chance": 0.08,         # Base crit chance (8%)
    "agi_diff_crit_scale": 0.015,     # Agility difference scaling for crit
    "crit_damage_multiplier": 1.6,    # Damage multiplier for crits
    "min_crit_chance": 0.005,         # Minimum possible crit chance (0.5%)
    "max_crit_chance": 0.35,          # Maximum possible crit chance (35%)

    # ============================================================
    # DODGE
    # ============================================================
    "base_dodge_chance": 0.22,        # Base dodge chance (22%)
    "agi_diff_dodge_scale": 0.04,     # Agility difference scaling for dodge
    "min_dodge_chance": 0.02,         # Minimum possible dodge chance (2%)
    "max_dodge_chance": 0.4,          # Maximum possible dodge chance (40%)
    "full_dodge_ratio": 0.6,          # Ratio of total dodge chance that results in full dodge
    "glance_damage_ratio": 0.5,       # Damage ratio for glancing hits

    # ============================================================
    # BLOCKING
    # ============================================================
    "base_block_reduction": 0.30,     # Base damage reduction from blocking (30%)
    "def_diff_block_scale": 0.025,    # Defense difference scaling for blocking
    "min_block_reduction": 0.1,       # Minimum block damage reduction (10%)
    "max_block_reduction": 0.7,       # Maximum block damage reduction (70%)
    "base_block_break_chance": 0.28,  # Base block break chance (28%)
    "agi_block_break_scale": 0.07,    # Agility scaling for block break
    "min_block_break_chance": 0.05,   # Minimum block break chance (5%)
    "max_block_break_chance": 0.6,    # Maximum block break chance (60%)

    # ============================================================
    # FATIGUE SYSTEM
    # ============================================================
    "stamina_fresh_threshold": 60,    # Above this = Fresh (no penalties)
    "stamina_tired_threshold": 25,    # Above this = Tired, below = Exhausted
    "fresh_multiplier": 1.0,          # No fatigue penalty (100%)
    "tired_multiplier": 0.75,         # Tired penalty (75% effectiveness)
    "exhausted_multiplier": 0.5,      # Exhausted penalty (50% effectiveness)


    # ============================================================
    # STAMINA SYSTEM
    # ============================================================
    "initial_stamina": 100,           # Maximum stamina points
    "attack_stamina_cost_per_zone": 7,  # Stamina cost per attack zone
    "defense_stamina_cost_per_zone": 4, # Stamina cost per defense zone
    "stamina_regen_per_round": 5,     # Stamina regenerated per round

    # ============================================================
    # EHP SCALING
    # ============================================================
    "hp_scaling_base": 10.0,         # Base health multiplier
    "hp_scaling_constant": 30,        # Constant added to health stat
    "hp_scaling_exponent": 0.67,      # Exponent for health scaling curve
    "damage_scaling_base": 1.1,      # Base damage multiplier
    "damage_scaling_constant": 50,    # Constant added to attack stat
    "damage_scaling_exponent": 0.63,  # Exponent for damage scaling curve
    "defense_scaling_multiplier": 40.0, # Defense stat divider for EHP calculation
    "defense_scaling_exponent": 0.55, # Exponent for defense scaling curve
}