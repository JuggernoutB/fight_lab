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
    debug_mode: bool = False,
    attacker_absorption_resource: float = 0.0
) -> tuple[Dict[str, Dict], float]:

    if not atk_zones:
        return {}, attacker_absorption_resource

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
        dodge_state = "hit"  # Default state
        damage_absorbed = 0.0  # Track dodge absorption

        # =========================
        # BLOCK LOGIC
        # =========================
        is_blocked = False
        if z in def_zones:
            is_blocked = True

            # Use enhanced block_break with absorption resource
            break_succeeded, attacker_absorption_resource = block_break(
                atk_agility, def_defense, attacker_stamina, attacker_absorption_resource
            )

            if break_succeeded:
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
                # Full dodge - all damage absorbed
                result = {
                    "damage": 0,
                    "event": "dodge",
                    "absorbed": {
                        "block": 0.0,
                        "dodge": raw  # All damage absorbed by dodge
                    }
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
            elif dodge_state == "glance":
                # Partial dodge - some damage absorbed
                damage_absorbed = max(0.0, raw - dmg)
                # This absorption will be included in the final result below
            else:
                damage_absorbed = 0.0  # No dodge, no absorption

        # =========================
        # CRIT LOGIC (only for unblocked zones)
        # =========================
        is_crit = False
        if not is_blocked:
            # Use enhanced crit with absorption resource
            is_crit, attacker_absorption_resource = calc_crit(
                atk_agility,
                def_defense,
                attacker_stamina,
                attacker_absorption_resource
            )

        if is_crit:
            dmg *= CONFIG["crit_damage_multiplier"]
            event = "crit"

        # =========================
        # FINAL OUTPUT - Stable API Contract
        # =========================
        # Round damage using probabilistic rounding
        final_damage = round_damage_probabilistic(dmg)

        # Calculate absorbed damage
        block_absorbed = 0.0
        dodge_absorbed = 0.0

        if is_blocked:
            # Block absorption = damage reduced by blocking (both block and block_break)
            block_absorbed = max(0.0, raw - dmg)
        elif dodge_state == "glance":
            # Glancing hit from dodge = damage reduced by glancing
            dodge_absorbed = damage_absorbed  # Set earlier in dodge logic

        result = {
            "damage": final_damage,
            "event": event,
            "absorbed": {
                "block": block_absorbed,
                "dodge": dodge_absorbed
            }
        }

        # Debug information only when requested
        if debug_mode:
            result.update({
                "raw": raw,
                "mitigated": max(0.0, raw - dmg),
                "damage_before_rounding": dmg,  # Show damage before probabilistic rounding
                "is_crit": is_crit,
                "is_blocked": is_blocked,
                "is_dodged": dodge_state in ("dodge", "glance")
            })

        results[z] = result

    return results, attacker_absorption_resource