from balance.targets import TARGETS


def check_range(name, value, low, high):
    if value < low or value > high:
        return f"[FAIL] {name}: {value:.4f} not in ({low}, {high})"
    return f"[OK]   {name}: {value:.4f}"


def validate(results, summary, rounds_list, n):

    report = []
    failed = False

    # =========================
    # BASIC METRICS
    # =========================
    avg_rounds = sum(rounds_list) / n

    # Get pre-calculated DPS from summary
    avg_dps = summary["avg_dps"]

    # Calculate draw rate
    total_draws = results.get("DRAW_MUTUAL_DEATH", 0) + results.get("DRAW_STAMINA", 0) + results.get("DRAW_TIMEOUT", 0) + results.get("DRAW_OTHER", 0)
    draw_rate = total_draws / n

    checks = [
        ("rounds_avg", avg_rounds),
        ("dps_avg", avg_dps),
        ("draw_rate", draw_rate),
    ]

    for name, value in checks:
        low, high = TARGETS[name]
        msg = check_range(name, value, low, high)
        report.append(msg)
        if "[FAIL]" in msg:
            failed = True

    # =========================
    # MECHANICS
    # =========================
    total_mechanics = sum(summary["mechanics"].values())
    for k in ["crit", "dodge", "block", "block_break", "hit"]:
        if k in TARGETS and total_mechanics > 0:
            rate = summary["mechanics"].get(k, 0) / total_mechanics
            low, high = TARGETS[k]
            msg = check_range(k, rate, low, high)
            report.append(msg)
            if "[FAIL]" in msg:
                failed = True

    # =========================
    # DAMAGE SPLIT
    # =========================
    total_damage_split = summary["damage_split"]["crit"] + summary["damage_split"]["normal"] + summary["damage_split"]["blocked"]
    if total_damage_split > 0:
        for k in ["crit_dmg", "normal_dmg", "blocked_dmg"]:
            if k in TARGETS:
                damage_key = k.replace("_dmg", "")
                rate = summary["damage_split"][damage_key] / total_damage_split
                low, high = TARGETS[k]
                msg = check_range(k, rate, low, high)
                report.append(msg)
                if "[FAIL]" in msg:
                    failed = True

    # =========================
    # STAMINA STATES
    # =========================
    total_stamina = summary["stamina_distribution"]["high"] + summary["stamina_distribution"]["mid"] + summary["stamina_distribution"]["low"]
    if total_stamina > 0:
        for k in ["stamina_high", "stamina_mid", "stamina_low"]:
            if k in TARGETS:
                state = k.replace("stamina_", "")
                rate = summary["stamina_distribution"][state] / total_stamina
                low, high = TARGETS[k]
                msg = check_range(k, rate, low, high)
                report.append(msg)
                if "[FAIL]" in msg:
                    failed = True

    # =========================
    # ROLE BALANCE
    # =========================
    if "role_balance_spread" in summary and "role_balance_spread" in TARGETS:
        role_spread = summary["role_balance_spread"]
        low, high = TARGETS["role_balance_spread"]
        msg = check_range("role_balance_spread", role_spread, low, high)
        report.append(msg)
        if "[FAIL]" in msg:
            failed = True

    # =========================
    # ARCHETYPE BALANCE
    # =========================
    if "archetype_balance_spread" in summary and "archetype_balance_spread" in TARGETS:
        archetype_spread = summary["archetype_balance_spread"]
        low, high = TARGETS["archetype_balance_spread"]
        msg = check_range("archetype_balance_spread", archetype_spread, low, high)
        report.append(msg)
        if "[FAIL]" in msg:
            failed = True

    # Archetype individual winrates
    if "archetype_winrates" in summary and "archetype_winrates" in TARGETS:
        for archetype, winrate in summary["archetype_winrates"].items():
            if archetype in TARGETS["archetype_winrates"]:
                low, high = TARGETS["archetype_winrates"][archetype]
                msg = check_range(f"archetype_{archetype.lower()}_winrate", winrate, low, high)
                report.append(msg)
                if "[FAIL]" in msg:
                    failed = True

    # Critical EXTREME dominance check
    if "archetype_winrates" in summary and "EXTREME" in summary["archetype_winrates"]:
        extreme_winrate = summary["archetype_winrates"]["EXTREME"]
        low, high = TARGETS["extreme_dominance_check"]
        msg = check_range("extreme_dominance_check", extreme_winrate, low, high)
        report.append(msg)
        if "[FAIL]" in msg:
            failed = True

    # =========================
    # RETURN RESULT
    # =========================
    final_report = "\n".join(report)
    return failed, final_report