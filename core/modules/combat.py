# core/engine.py - V15.6 FIXED COMBAT ENGINE

import random
from typing import Dict, List
from ..config import CONFIG
from .ehp import EHPDamageCalculator
from .zones import get_zone_multiplier
from .fatigue import get_fatigue_multiplier
from .crit import calc_crit
from .dodge import apply_dodge
from .block import apply_block, block_break
from .rounding import round_damage_probabilistic, apply_damage_variance


def process_attack(
    attacker: Dict,
    defender: Dict,
    attacker_stamina: int,
    defender_stamina: int,
    atk_zones: List[str],
    def_zones: List[str],
    debug_mode: bool = False,
    attacker_fatigue_bonus: float = 0.0,
    attacker_modifiers=None,
    defender_modifiers=None
) -> tuple[Dict[str, Dict], Dict[str, int], Dict[str, any]]:

    if not atk_zones:
        return {}, {}, {}

    # === DATA NORMALIZATION (protect against dict typos) ===
    try:
        atk_attack = attacker["attack"]
        atk_agility = attacker["agility"]
        def_defense = defender["defense"]
        def_agility = defender["agility"]
    except KeyError as e:
        raise ValueError(f"Missing required stat in fighter data. KeyError: {e}. Attacker keys: {list(attacker.keys())}, Defender keys: {list(defender.keys())}")

    calc = EHPDamageCalculator()

    # BASE (no fatigue yet)
    base = calc.calculate_damage_output(atk_attack)

    # Apply equipment damage bonus
    if attacker_modifiers:
        base += attacker_modifiers.damage_base

    base /= len(atk_zones)

    # apply fatigue ONCE
    base *= get_fatigue_multiplier(attacker_stamina, "attack")

    results = {}
    total_absorbed_by_defender = 0.0  # Track total damage absorbed by defender

    # Track successful actions for stamina costs
    action_costs = {
        "dodge": 0,
        "crit": 0,
        "block_break": 0
    }

    # Track events (legacy compatibility)
    skip_events = []

    for z in atk_zones:

        # =========================
        # STEP 1: Base damage calculation with zone protection
        # =========================
        zone_multiplier = get_zone_multiplier(z, defender_modifiers)
        raw_damage = base * zone_multiplier   # damage after zone protection

        # =========================
        # STEP 2: Roll dodge (with skip protection)
        # =========================
        is_dodged = False

        # Check if zone is blocked (dodge doesn't apply to blocked zones)
        is_blocked = z in def_zones

        if not is_blocked:
            # Calculate dodge chance
            dmg_temp, dodge_state = apply_dodge(raw_damage, atk_attack, def_agility, defender_stamina, atk_agility, defender_modifiers)

            # Process dodge result directly

            # Process dodge result
            if dodge_state == "dodge":  # Full dodge only
                is_dodged = True
                action_costs["dodge"] += 1
                # Full dodge: all damage absorbed, END here
                result = {
                    "damage": 0,
                    "event": "dodge",
                    "absorbed": {
                        "block": 0.0,
                        "dodge": raw_damage  # All raw damage absorbed by dodge
                    }
                }

                if debug_mode:
                    result.update({
                        "raw": raw_damage,
                        "mitigated": raw_damage,
                        "damage_before_rounding": 0.0,
                        "is_crit": False,
                        "is_blocked": False,
                        "is_dodged": True
                    })

                results[z] = result
                continue  # Skip to next zone

        # =========================
        # STEP 3: Apply crit (ALWAYS, if hit occurred)
        # =========================
        is_crit = calc_crit(
            atk_agility,
            def_defense,
            attacker_stamina,
            attacker_fatigue_bonus,
            attacker_modifiers
        )

        # Apply crit effect

        # Apply crit multiplier to raw damage
        if is_crit:
            action_costs["crit"] += 1
            crit_multiplier = CONFIG["crit_damage_multiplier"]
            # Apply equipment crit power bonus
            if attacker_modifiers:
                crit_multiplier += attacker_modifiers.crit_power
            raw_damage *= crit_multiplier

        # =========================
        # STEP 4: Apply block (if zone is defended)
        # =========================
        blocked_damage = raw_damage  # Start with full damage
        event = "hit"  # Default event

        if is_blocked:
            # Check block break with skip protection
            break_succeeded = block_break(
                atk_agility, def_defense, attacker_stamina, attacker_fatigue_bonus, attacker_modifiers
            )

            # Process block break result

            if break_succeeded:
                action_costs["block_break"] += 1
                blocked_damage = raw_damage * CONFIG["block_break_damage_ratio"]
                event = "crit_block_break" if is_crit else "block_break"
            else:
                blocked_damage = apply_block(raw_damage, atk_attack, def_defense, defender_stamina, defender_modifiers)
                event = "crit_block" if is_crit else "block"
        else:
            # No block, full damage goes through
            event = "crit" if is_crit else "hit"

        # =========================
        # STEP 5: Apply DEF (EHP mitigation)
        # =========================
        final_damage_float = calc.apply_defense_reduction(blocked_damage, def_defense)

        # =========================
        # STEP 6: Apply damage variance (RNG)
        # =========================
        final_damage_with_variance = apply_damage_variance(final_damage_float)

        # =========================
        # STEP 7: Final damage and absorption calculation
        # =========================
        final_damage = round_damage_probabilistic(final_damage_with_variance)

        # Calculate total absorbed damage (KEY CHANGE: total absorption)
        absorbed_total = raw_damage - final_damage_with_variance  # Before rounding

        # Split absorption between block and defense for tracking
        if is_blocked:
            block_absorbed = max(0.0, raw_damage - blocked_damage)
            defense_absorbed = max(0.0, blocked_damage - final_damage_with_variance)
        else:
            block_absorbed = 0.0
            defense_absorbed = absorbed_total

        # =========================
        # STEP 7: Build result
        # =========================
        result = {
            "damage": final_damage,
            "event": event,
            "absorbed": {
                "block": block_absorbed,
                "dodge": 0.0  # No partial dodge in new system
            }
        }

        # Debug information only when requested
        if debug_mode:
            result.update({
                "raw": raw_damage,
                "mitigated": absorbed_total,
                "damage_before_rounding": final_damage_float,
                "damage_with_variance": final_damage_with_variance,
                "is_crit": is_crit,
                "is_blocked": is_blocked,
                "is_dodged": False  # Already handled above for full dodge
            })

        results[z] = result

        # Add absorbed damage to defender's total (TOTAL ABSORPTION now)
        total_absorbed_by_defender += absorbed_total

    # Return updated values
    return results, action_costs, skip_events