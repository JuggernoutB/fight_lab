import random

# ============================================================
# AI THRESHOLDS (НЕ механика, а поведение!)
# ============================================================

# stamina thresholds (поведенческие, не равны fatigue напрямую)
AI_STAMINA_CRITICAL = 15
AI_STAMINA_LOW = 35

# damage reaction thresholds
AI_DAMAGE_HEAVY = 300

# aggression thresholds
AI_STREAK_AGGRESSION = 2


def choose_action(fighter, state):

    stamina = fighter.stamina

    # безопасный доступ
    last_dmg = getattr(fighter, "last_damage_taken", 0)
    streak = getattr(fighter, "streak", 0)

    # =========================
    # 1. CRITICAL EXHAUSTION (still must attack)
    # =========================
    if stamina < AI_STAMINA_CRITICAL:
        return {
            "attack_zones": ["chest"],  # Minimum required attack
            "defense_zones": [],
            "rest": 0
        }

    # =========================
    # 2. HEAVY DAMAGE REACTION
    # =========================
    if last_dmg > AI_DAMAGE_HEAVY:
        return {
            "attack_zones": ["chest"],
            "defense_zones": ["head", "chest"],
            "rest": 0
        }

    # =========================
    # 3. AGGRESSION (STREAK)
    # =========================
    if streak >= AI_STREAK_AGGRESSION:
        return {
            "attack_zones": ["head", "chest"],
            "defense_zones": [],
            "rest": 0
        }

    # =========================
    # 4. LOW STAMINA PLAY
    # =========================
    if stamina < AI_STAMINA_LOW:
        return {
            "attack_zones": ["chest"],
            "defense_zones": ["chest"],
            "rest": 0
        }

    # =========================
    # 5. DEFAULT MIX
    # =========================
    return random.choice([
        {
            "attack_zones": ["head", "chest"],
            "defense_zones": []
        },
        {
            "attack_zones": ["chest"],
            "defense_zones": ["head"]
        },
        {
            "attack_zones": ["chest"],
            "defense_zones": ["chest"]
        },
    ])