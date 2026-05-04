# balance/targets_level_1.py

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
    "draw_rate": (0.08, 0.30),

    # =========================
    # STAMINA EXHAUSTION
    # =========================
    "stamina_exhaustion_rate": (0.0, 0.35),  # 0-35% fights ending in stamina draw

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
    # BUILD TYPE BALANCE
    # =========================
    "2_stat_builds_spread": (0.0, 0.05),  # Max 5% spread for 2-stat builds + Universal
    "3_stat_builds_spread": (0.0, 0.15),  # Max 15% spread for 3-stat builds + Universal
}