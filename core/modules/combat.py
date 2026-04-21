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
    attacker_fatigue_bonus: float = 0.0,
    defender_skip_activations: int = 0
) -> tuple[Dict[str, Dict], Dict[str, int], Dict[str, any], int]:

    if not atk_zones:
        return {}, {}, {}, defender_skip_activations

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
    total_absorbed_by_defender = 0.0  # Track total damage absorbed by defender

    # Track successful actions for stamina costs
    action_costs = {
        "dodge": 0,
        "crit": 0,
        "block_break": 0
    }

    # Track skip protection events (list to allow multiple activations)
    skip_events = []

    # NEW: Defense-based skip protection system
    # Use skip activations remaining for the entire fight (passed from game engine)
    skip_activations_remaining = defender_skip_activations

    # Get config for skip protection threshold
    config = CONFIG

    for z in atk_zones:

        raw = base * ZONE_MULTIPLIERS[z]   # true pre-mitigation snapshot
        dmg = raw

        # =========================
        # STEP 1: ROLL ALL MECHANICS (independent checks)
        # =========================

        # Check if zone is blocked
        is_blocked = z in def_zones

        # Always check crit (unless blocked zone)
        is_crit = False
        crit_skipped = False
        if not is_blocked:
            is_crit = calc_crit(
                atk_agility,
                def_defense,
                attacker_stamina,
                attacker_fatigue_bonus
            )

            # Check if crit is blocked by skip protection (defense-based)
            if is_crit and skip_activations_remaining > 0:
                is_crit = False  # Block the crit
                crit_skipped = True
                skip_events.append("crit_skip")
                skip_activations_remaining -= 1  # Consume one activation

        # Always check dodge (unless blocked zone)
        dodge_state = "hit"
        dodge_skipped = False
        if not is_blocked:
            dmg_temp, dodge_state = apply_dodge(
                dmg,
                atk_attack,
                def_agility,
                defender_stamina,
                atk_agility
            )

            # Check if dodge is blocked by skip protection (defense-based)
            if dodge_state in ["dodge", "glance"] and skip_activations_remaining > 0:
                dodge_state = "hit"  # Block the dodge, make it a normal hit
                dodge_skipped = True
                skip_events.append("dodge_skip")
                skip_activations_remaining -= 1  # Consume one activation

            # Don't apply dodge damage reduction yet, just remember the state

        # =========================
        # STEP 2: RESOLVE FINAL OUTCOME
        # =========================

        # Priority: dodge > block > crit hit
        if not is_blocked and dodge_state == "dodge":
            # Full dodge - all damage absorbed, but crit still counted!
            action_costs["dodge"] += 1  # Successful dodge costs stamina
            if is_crit:
                action_costs["crit"] += 1  # Successful crit costs stamina

            result = {
                "damage": 0,
                "event": "crit_dodge" if is_crit else "dodge",
                "absorbed": {
                    "block": 0.0,
                    "dodge": raw
                },
                "crit_rolled": is_crit  # Track crit for statistics
            }
            if debug_mode:
                result.update({
                    "raw": raw,
                    "mitigated": raw,
                    "is_crit": is_crit,
                    "is_blocked": False,
                    "is_dodged": True
                })
            results[z] = result
            continue

        elif is_blocked:
            # Handle block logic
            break_succeeded = block_break(
                atk_agility, def_defense, attacker_stamina, attacker_fatigue_bonus
            )

            # Check if block break is blocked by skip protection (defense-based)
            block_break_skipped = False
            if break_succeeded and skip_activations_remaining > 0:
                break_succeeded = False  # Block the block break
                block_break_skipped = True
                skip_events.append("block_break_skip")
                skip_activations_remaining -= 1  # Consume one activation

            if break_succeeded:
                action_costs["block_break"] += 1  # Successful block break costs stamina
                dmg *= CONFIG["block_break_damage_ratio"]
                event = "crit_block_break" if is_crit else "block_break"
                if is_crit:
                    action_costs["crit"] += 1  # Successful crit costs stamina
                    dmg *= CONFIG["crit_damage_multiplier"]
            else:
                dmg = apply_block(dmg, atk_attack, def_defense, defender_stamina)
                event = "crit_block" if is_crit else "block"
                if is_crit:
                    action_costs["crit"] += 1  # Successful crit costs stamina
                    dmg *= CONFIG["crit_damage_multiplier"]

        else:
            # Regular hit or glancing hit
            if dodge_state == "glance":
                dmg, _ = apply_dodge(dmg, atk_attack, def_agility, defender_stamina, atk_agility)
                event = "crit_glance" if is_crit else "glance"
                if is_crit:
                    action_costs["crit"] += 1  # Successful crit costs stamina
            else:
                event = "crit" if is_crit else "hit"

            if is_crit:
                action_costs["crit"] += 1  # Successful crit costs stamina
                dmg *= CONFIG["crit_damage_multiplier"]

        # =========================
        # EHP MITIGATION - Apply defense-based damage reduction
        # =========================
        # Apply EHP-based mitigation (hidden defense effectiveness)
        from core.modules.ehp import apply_defense_reduction
        dmg = apply_defense_reduction(dmg, def_defense)

        # =========================
        # FINAL OUTPUT - Stable API Contract
        # =========================
        # Round damage using probabilistic rounding
        final_damage = round_damage_probabilistic(dmg)

        # Calculate absorbed damage
        block_absorbed = 0.0
        dodge_absorbed = 0.0

        if is_blocked:
            # Block mitigation = damage reduced by blocking (both block and block_break)
            block_absorbed = max(0.0, raw - dmg)
        elif dodge_state == "glance":
            # Glancing hit from dodge = damage reduced by glancing
            dodge_absorbed = max(0.0, raw - dmg)

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

        # Add absorbed damage to defender's total (BLOCK ONLY - dodge is separate)
        total_absorbed_by_defender += block_absorbed  # Only block mitigation is tracked

    # NOTE: Skip protection is now defense-based and managed in game_engine.py

    return results, action_costs, skip_events, skip_activations_remaining