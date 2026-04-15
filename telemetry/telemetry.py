from core.api import get_stamina_level, FATIGUE_LEVEL_FRESH, FATIGUE_LEVEL_TIRED, FATIGUE_LEVEL_EXHAUSTED

class Telemetry:

    def __init__(self):
        self.events = []

        self.counters = {
            "crit": 0,
            "dodge": 0,
            "block": 0,
            "block_break": 0,
            "hit": 0,
        }

        self.damage_types = {
            "crit": 0.0,
            "normal": 0.0,
            "blocked": 0.0,
        }

        # Damage absorption tracking
        self.damage_absorbed = {
            "dodge": 0.0,      # Damage absorbed by dodging
            "block": 0.0,      # Damage absorbed by blocking
        }

        # Absorption resource event tracking
        self.absorption_events = []

        self.stamina_samples = []
        self.momentum_log = []

        # Stamina state time distribution tracking
        self.stamina_time_distribution = {
            "high": 0.0,   # Fresh (>60 stamina)
            "mid": 0.0,    # Tired (30-60 stamina)
            "low": 0.0     # Exhausted (<30 stamina)
        }
        self.total_samples = 0

    # ============================================================
    # RECORD
    # ============================================================

    def record(self, event, state=None):

        self.events.append(event)

        # =========================
        # PROCESS STRUCTURED ATTACKS
        # =========================
        for attack in event.get("attacks", []):
            event_type = attack["event"]
            damage = attack["damage"]

            # Count events
            self.counters[event_type] += 1

            # Categorize damage
            if event_type == "crit":
                self.damage_types["crit"] += damage
            elif event_type in ["block", "block_break"]:
                self.damage_types["blocked"] += damage
            else:
                self.damage_types["normal"] += damage

            # Track damage absorption
            if "absorbed" in attack:
                absorbed_data = attack["absorbed"]
                if "dodge" in absorbed_data:
                    self.damage_absorbed["dodge"] += absorbed_data["dodge"]
                if "block" in absorbed_data:
                    self.damage_absorbed["block"] += absorbed_data["block"]

        # =========================
        # PROCESS ABSORPTION EVENTS
        # =========================
        if "absorption_events" in event:
            for abs_event in event["absorption_events"]:
                self.absorption_events.append(abs_event)

        # =========================
        # STATE
        # =========================
        if state:
            self.stamina_samples.append((
                state.fighter_a.stamina,
                state.fighter_b.stamina
            ))

            self.momentum_log.append(state.momentum)

            # Record stamina states for both fighters
            self.record_stamina_states(state.fighter_a.stamina, state.fighter_b.stamina)

    def record_stamina_states(self, stamina_a: int, stamina_b: int):
        """Record stamina states for time distribution metrics"""
        for stamina in [stamina_a, stamina_b]:
            level = get_stamina_level(stamina)

            if level == FATIGUE_LEVEL_FRESH:
                self.stamina_time_distribution["high"] += 1
            elif level == FATIGUE_LEVEL_TIRED:
                self.stamina_time_distribution["mid"] += 1
            else:  # FATIGUE_LEVEL_EXHAUSTED
                self.stamina_time_distribution["low"] += 1

            self.total_samples += 1

    def record_damage_absorption(self, absorption_type: str, absorbed_amount: float):
        """Record damage absorption by type (dodge or block)"""
        if absorption_type in self.damage_absorbed:
            self.damage_absorbed[absorption_type] += absorbed_amount

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(self):

        # Calculate total damage from structured events
        total_damage = 0.0
        for event in self.events:
            for attack in event.get("attacks", []):
                total_damage += attack["damage"]

        rounds = len(self.events)

        # -------------------------
        # STAMINA
        # -------------------------
        if self.stamina_samples:
            avg_stamina_a = sum(s[0] for s in self.stamina_samples) / len(self.stamina_samples)
            avg_stamina_b = sum(s[1] for s in self.stamina_samples) / len(self.stamina_samples)
        else:
            avg_stamina_a = 0
            avg_stamina_b = 0

        # -------------------------
        # MECHANICS %
        # -------------------------
        total_mech = sum(self.counters.values()) or 1

        mechanics_percent = {
            k: v / total_mech
            for k, v in self.counters.items()
        }

        # -------------------------
        # DAMAGE %
        # -------------------------
        total_dmg_types = sum(self.damage_types.values()) or 1

        damage_percent = {
            k: v / total_dmg_types
            for k, v in self.damage_types.items()
        }

        # -------------------------
        # STAMINA TIME DISTRIBUTION
        # -------------------------
        stamina_distribution_normalized = {}
        if self.total_samples > 0:
            stamina_distribution_normalized = {
                k: v / self.total_samples
                for k, v in self.stamina_time_distribution.items()
            }
        else:
            stamina_distribution_normalized = {
                "high": 0.0,
                "mid": 0.0,
                "low": 0.0
            }

        # -------------------------
        # ABSORPTION EVENTS
        # -------------------------
        absorption_event_count = len(self.absorption_events)
        absorption_events_by_fighter = {"A": 0, "B": 0}
        for event in self.absorption_events:
            if event["fighter"] in absorption_events_by_fighter:
                absorption_events_by_fighter[event["fighter"]] += 1

        return {
            "rounds": rounds,
            "total_damage": total_damage,

            "avg_stamina_a": avg_stamina_a,
            "avg_stamina_b": avg_stamina_b,

            "mechanics": mechanics_percent,
            "damage_split": damage_percent,
            "stamina_distribution": stamina_distribution_normalized,
            "damage_absorbed": self.damage_absorbed.copy(),
            "absorption_events": {
                "total": absorption_event_count,
                "by_fighter": absorption_events_by_fighter.copy(),
                "events": self.absorption_events.copy()
            }
        }