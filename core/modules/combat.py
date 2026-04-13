# core/engine.py - V15.6 FIXED COMBAT ENGINE

import random
from typing import Dict, List
from ..config import CONFIG
from .ehp import EHPDamageCalculator
from .zones import ZONE_MULTIPLIERS
from .fatigue import get_fatigue_multiplier
from .crit import calc_crit
from .dodge import apply_dodge
from .block import apply_block, block_break
from .rounding import round_damage_probabilistic


def process_attack(
    attacker: Dict,
    defender: Dict,
    attacker_stamina: int,
    defender_stamina: int,
    atk_zones: List[str],
    def_zones: List[str],
    debug_mode: bool = False
) -> Dict[str, Dict]:

    if not atk_zones:
        return {}

    # === DATA NORMALIZATION (protect against dict typos) ===
    try:
        atk_attack = attacker["attack"]
        atk_agility = attacker["agility"]
        def_defense = defender["defense"]
        def_agility = defender["agility"]
    except KeyError as e:
        raise ValueError(f"Missing required stat in fighter data: {e}")

    calc = EHPDamageCalculator()

    # BASE (no fatigue yet)
    base = calc.calculate_damage_output(atk_attack)
    base /= len(atk_zones)

    # apply fatigue ONCE (correct)
    base *= get_fatigue_multiplier(attacker_stamina, "attack")

    results = {}

    for z in atk_zones:

        raw = base * ZONE_MULTIPLIERS[z]   # true pre-mitigation snapshot
        dmg = raw

        event = "hit"

        # =========================
        # BLOCK LOGIC
        # =========================
        if z in def_zones:

            if block_break(atk_agility, def_defense, attacker_stamina):
                # block is partially ignored
                dmg *= CONFIG["block_break_damage_ratio"]
                event = "block_break"
            else:
                dmg = apply_block(dmg, atk_attack, def_defense, defender_stamina)
                event = "block"

        # =========================
        # DODGE LOGIC
        # =========================
        else:
            dmg, dodge_state = apply_dodge(
                dmg,
                atk_attack,
                def_agility,
                defender_stamina
            )

            if dodge_state == "dodge":
                result = {
                    "damage": 0,
                    "event": "dodge"
                }
                if debug_mode:
                    result.update({
                        "raw": raw,
                        "mitigated": raw,
                        "is_crit": False,
                        "is_blocked": False,
                        "is_dodged": True
                    })
                results[z] = result
                continue

        # =========================
        # CRIT LOGIC
        # =========================
        is_crit = random.random() < calc_crit(
            atk_agility,
            def_defense,
            attacker_stamina
        )

        if is_crit:
            dmg *= CONFIG["crit_damage_multiplier"]
            event = "crit"

        # =========================
        # FINAL OUTPUT - Stable API Contract
        # =========================
        # Round damage using probabilistic rounding
        final_damage = round_damage_probabilistic(dmg)

        result = {
            "damage": final_damage,
            "event": event
        }

        # Debug information only when requested
        if debug_mode:
            result.update({
                "raw": raw,
                "mitigated": max(0.0, raw - dmg),
                "damage_before_rounding": dmg,  # Show damage before probabilistic rounding
                "is_crit": is_crit,
                "is_blocked": event in ("block", "block_break"),
                "is_dodged": False
            })

        results[z] = result

    return results