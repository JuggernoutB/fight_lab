from core.api import get_stamina_level, FATIGUE_LEVEL_FRESH, FATIGUE_LEVEL_TIRED, FATIGUE_LEVEL_EXHAUSTED

class Telemetry:

    def __init__(self):
        self.events = []

        self.counters = {
            "crit": 0,
            "dodge": 0,
            "block": 0,
            "hit": 0,
            "crit_block": 0,
        }

        # NEW: Separate crit tracking for proper metrics
        self.crit_stats = {
            "total_rolls": 0,      # Total times crit was checked
            "crit_rolls": 0,       # Times crit succeeded (raw crit rate)
            "successful_hits": 0,  # Hits that actually dealt damage (for effective crit rate)
            "crit_hits": 0,        # Crits that actually dealt damage
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

            # Count events (for old compatibility)
            if event_type in self.counters:
                self.counters[event_type] += 1

            # NEW: Track crit statistics properly
            # Check if crit was rolled (for any non-blocked attack)
            if event_type not in ["block"]:  # All non-blocked attacks check crit
                self.crit_stats["total_rolls"] += 1

                # Check if crit succeeded
                is_crit_event = "crit" in event_type
                if is_crit_event:
                    self.crit_stats["crit_rolls"] += 1

                # Track hits that dealt damage (not dodged)
                if event_type != "dodge":
                    self.crit_stats["successful_hits"] += 1

                    # Track crits that dealt damage
                    if is_crit_event:
                        self.crit_stats["crit_hits"] += 1

            # Categorize damage for compatibility
            if "crit" in event_type:
                self.damage_types["crit"] += damage
            elif event_type in ["block", "crit_block"]:
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

            # NEW: Track crit_rolled for dodged attacks
            if "crit_rolled" in attack:
                if attack["crit_rolled"]:
                    self.crit_stats["crit_rolls"] += 1

        # =========================
        # PROCESS ABSORPTION EVENTS
        # =========================

        # Skip events processing removed

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

        # Skip protection events removed

        # -------------------------
        # NEW CRIT METRICS
        # -------------------------
        crit_metrics = {}
        if self.crit_stats["total_rolls"] > 0:
            crit_metrics["raw_crit_rate"] = self.crit_stats["crit_rolls"] / self.crit_stats["total_rolls"]

        if self.crit_stats["successful_hits"] > 0:
            crit_metrics["effective_crit_rate"] = self.crit_stats["crit_hits"] / self.crit_stats["successful_hits"]

        if total_damage > 0:
            crit_metrics["crit_damage_ratio"] = self.damage_types["crit"] / total_damage

        crit_metrics.update({
            "total_rolls": self.crit_stats["total_rolls"],
            "crit_rolls": self.crit_stats["crit_rolls"],
            "successful_hits": self.crit_stats["successful_hits"],
            "crit_hits": self.crit_stats["crit_hits"]
        })

        return {
            "rounds": rounds,
            "total_damage": total_damage,

            "avg_stamina_a": avg_stamina_a,
            "avg_stamina_b": avg_stamina_b,

            "mechanics": mechanics_percent,
            "damage_split": damage_percent,
            "crit_metrics": crit_metrics,  # NEW
            "stamina_distribution": stamina_distribution_normalized,
            "damage_absorbed": self.damage_absorbed.copy(),
        }