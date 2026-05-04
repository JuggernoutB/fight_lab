# state/fight_state.py

class FighterState:
    def __init__(self, hp, stamina, role, attack=10, defense=10, agility=10):
        self.hp = hp
        self.stamina = stamina
        self.role = role

        # Combat stats
        self.attack = attack
        self.defense = defense
        self.agility = agility

        self.event_log = []

        # MEMORY (V15 FIX)
        self.last_action = None
        self.streak = 0
        self.damage_taken_last = 0
        self.last_damage_taken = 0



class FightState:
    def __init__(self, round_id, fighter_a, fighter_b):
        self.round_id = round_id
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b

        # meta
        self.momentum = 0.0
        self.deadlock_pressure = 0.0

        # fight end tracking
        self.end_reason = None  # "death", "stamina_exhaustion", "max_rounds"