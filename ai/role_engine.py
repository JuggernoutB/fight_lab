import random
from core.modules.zones import ZONES

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


def choose_action_normal():
    """
    Normal mode: равномерное поведение для benchmark_level
    - 50% раундов 1 зона атаки, 50% раундов 2 зоны атаки
    - 33.3% раундов 0 зон защиты, 33.3% 1 зона, 33.3% 2 зоны
    """
    # Выбор количества зон для атаки (1 или 2)
    num_attack = 1 if random.random() < 0.5 else 2
    attack_zones = random.sample(ZONES, num_attack)

    # Выбор количества зон для защиты (0, 1 или 2)
    defense_choice = random.random()
    if defense_choice < 0.333:
        defense_zones = []
    elif defense_choice < 0.666:
        defense_zones = [random.choice(ZONES)]
    else:
        defense_zones = random.sample(ZONES, 2)

    return {
        "attack_zones": attack_zones,
        "defense_zones": defense_zones,
        "rest": 0
    }


def choose_action(fighter, state, mode="ai"):
    """
    Выбор действия для бойца

    Args:
        fighter: объект бойца
        state: состояние игры
        mode: режим выбора действий ("ai" или "normal")
    """
    # Normal mode: равномерное поведение
    if mode == "normal":
        return choose_action_normal()

    # AI mode: существующая логика
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