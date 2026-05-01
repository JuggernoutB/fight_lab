# balance/targets.py

TARGETS = {

    # =========================
    # FIGHT LENGTH
    # =========================
    "rounds_avg": (8.0, 10.5),

    # =========================
    # DPS
    # =========================
    "dps_avg": (19, 24),

    # =========================
    # DRAW RATE
    # =========================
    "draw_rate": (0.1, 0.21),

    # =========================
    # STAMINA EXHAUSTION
    # =========================
    "stamina_exhaustion_rate": (0.0, 0.02),  # Max 2% fights with 0 stamina

    # =========================
    # MECHANICS DISTRIBUTION
    # =========================
    "crit": (0.08, 0.12),
    "dodge": (0.04, 0.07),
    "block": (0.23, 0.33),
    "block_break": (0.035, 0.1),
    "hit": (0.40, 0.55),

    # =========================
    # DAMAGE SPLIT
    # =========================
    "crit_dmg": (0.10, 0.18),
    "normal_dmg": (0.50, 0.60),
    "blocked_dmg": (0.27, 0.32),

    # =========================
    # STAMINA STATES
    # =========================
    "stamina_high": (0.30, 0.45),
    "stamina_mid": (0.40, 0.55),
    "stamina_low": (0.10, 0.20),

    # =========================
    # ROLE BALANCE
    # =========================
    "role_balance_spread": (0.0, 0.06),  # Max 6% spread (relaxed for new scoring system)

    # Role distribution targets (percentage of total fights)
    "role_distribution": {
        "TANK": (0.18, 0.30),        # 18-30% of builds
        "BRUISER": (0.10, 0.20),     # 10-20% of builds
        "SKIRMISHER": (0.12, 0.22),  # 12-22% of builds
        "ASSASSIN": (0.15, 0.25),    # 15-25% of builds
        "UNIVERSAL": (0.20, 0.35),   # 20-35% of builds (balanced builds common)
    },
}