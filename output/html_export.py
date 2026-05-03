# output/html_export.py - HTML export for benchmark results

import json
from datetime import datetime
from typing import Dict, List

def export_benchmark_to_html(results: Dict, level: int, num_fights: int, action_mode: str, output_path: str = None):
    """
    Export benchmark results to HTML file with interactive tabs

    Args:
        results: Benchmark results dictionary
        level: Level that was benchmarked
        num_fights: Number of fights
        action_mode: Action mode used
        output_path: Custom output path (optional)
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/benchmark_level_{level}_{num_fights}_{action_mode}_{timestamp}.html"

    html_content = generate_html_content(results, level, num_fights, action_mode)

    # Ensure output directory exists
    import os
    os.makedirs(os.path.dirname(output_path) if '/' in output_path else 'output', exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path

def generate_html_content(results: Dict, level: int, num_fights: int, action_mode: str) -> str:
    """Generate complete HTML content"""

    # Calculate totals for convenience
    total_stat_points = level * 4 + 8
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Benchmark Results - Level {level}</title>
    <style>
        {get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Level {level} Benchmark Results</h1>
            <div class="meta-info">
                <span>📊 {total_stat_points} stat points | 🥊 {num_fights:,} fights | 🎮 {action_mode} mode</span>
                <span>⏱️ Generated: {timestamp}</span>
            </div>
        </header>

        <nav class="tabs">
            <button class="tab-button active" onclick="openTab(event, 'overview')">📋 Overview</button>
            <button class="tab-button" onclick="openTab(event, 'roles')">⚔️ Roles & Winrates</button>
            <button class="tab-button" onclick="openTab(event, 'balance')">⚖️ Balance Analysis</button>
            <button class="tab-button" onclick="openTab(event, 'builds')">🏗️ Builds by Role</button>
            <button class="tab-button" onclick="openTab(event, 'combat')">⚡ Mechanics Analysis</button>
        </nav>

        {generate_overview_tab(results, level, num_fights, action_mode)}
        {generate_roles_tab(results)}
        {generate_balance_tab(results)}
        {generate_builds_tab(results)}
        {generate_combat_tab(results)}
    </div>

    <script>
        {get_javascript()}
    </script>
</body>
</html>"""

    return html

def generate_overview_tab(results: Dict, level: int, num_fights: int, action_mode: str) -> str:
    """Generate overview tab content"""

    # Calculate key metrics (same logic as print_level_benchmark_results)
    summary = results.get("summary", {})
    total = summary.get("total_fights", num_fights)
    winners = summary.get("winners", {})

    # Calculate metrics
    rounds_avg = summary.get("avg_rounds", 0)
    dps_avg = sum(results.get("dps_data", [])) / len(results.get("dps_data", [1])) if results.get("dps_data") else 0
    draw_rate = (winners.get("DRAW_TIMEOUT", 0) + winners.get("DRAW_MUTUAL_DEATH", 0)) / total if total > 0 else 0
    stamina_exhaustion_rate = results.get("stamina_exhaustion_fights", 0) / total if total > 0 else 0

    return f"""
        <div id="overview" class="tab-content active">
            <div class="grid-2">
                <div class="card">
                    <h3>📊 Fight Statistics</h3>
                    <div class="stat-grid">
                        <div class="stat">
                            <span class="stat-label">Average Fight Length</span>
                            <span class="stat-value">{rounds_avg:.1f} rounds</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Average DPS</span>
                            <span class="stat-value">{dps_avg:.1f}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Draw Rate</span>
                            <span class="stat-value">{draw_rate:.1%}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Stamina Draw Rate</span>
                            <span class="stat-value">{stamina_exhaustion_rate:.1%}</span>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>🎲 Build Analysis</h3>
                    <div class="stat-grid">
                        <div class="stat">
                            <span class="stat-label">Unique Builds</span>
                            <span class="stat-value">{len(results.get('builds_used', {}))}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Pure Builds (>15% conf)</span>
                            <span class="stat-value">{sum(1 for conf in results.get('role_confidences', []) if conf > 0.15)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Hybrid Builds (<5% conf)</span>
                            <span class="stat-value">{sum(1 for conf in results.get('role_confidences', []) if conf < 0.05)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Average Confidence</span>
                            <span class="stat-value">{sum(results.get('role_confidences', [0])) / len(results.get('role_confidences', [1])) if results.get('role_confidences') else 0:.3f}</span>
                        </div>
                    </div>
                </div>
            </div>

            {generate_stamina_overview(results)}
            {generate_rounds_distribution_chart(results)}
        </div>
    """

def generate_stamina_overview(results):
    """Generate stamina overview for main tab"""
    stamina_data = results.get("stamina_data", {})
    total_fights = results.get("summary", {}).get("total_fights", 1)
    stamina_exhaustion_fights = results.get("stamina_exhaustion_fights", 0)
    zero_stamina_encounters = results.get("zero_stamina_encounters", 0)

    # Calculate percentages for stamina distribution
    if stamina_data:
        total_time = sum(stamina_data.values()) or 1
        high = (stamina_data.get("high", 0) / total_time) * 100
        mid = (stamina_data.get("mid", 0) / total_time) * 100
        low = (stamina_data.get("low", 0) / total_time) * 100
    else:
        high = mid = low = 0

    # Calculate percentages for zero stamina analysis
    exhaustion_rate = (stamina_exhaustion_fights / total_fights * 100) if total_fights > 0 else 0
    zero_stamina_rate = (zero_stamina_encounters / total_fights * 100) if total_fights > 0 else 0

    return f"""
        <div class="card" style="margin-bottom: 20px;">
            <h3>⚡ Stamina Analysis</h3>
            <div class="grid-2" style="margin-bottom: 20px;">
                <div>
                    <h4 style="margin: 0 0 15px 0; color: #374151;">⏱️ Stamina Distribution</h4>
                    <div class="stamina-chart-overview">
                        <div class="stamina-bar-overview">
                            <div class="stamina-segment-overview high" style="width: {high:.1f}%">
                                Fresh: {high:.1f}%
                            </div>
                            <div class="stamina-segment-overview mid" style="width: {mid:.1f}%">
                                Tired: {mid:.1f}%
                            </div>
                            <div class="stamina-segment-overview low" style="width: {low:.1f}%">
                                Exhausted: {low:.1f}%
                            </div>
                        </div>
                    </div>
                </div>
                <div>
                    <h4 style="margin: 0 0 15px 0; color: #374151;">💥 Zero Stamina Analysis</h4>
                    <div class="zero-stamina-overview">
                        <div class="overview-metric-row">
                            <span class="overview-metric-label">Fights ending in stamina draw:</span>
                            <span class="overview-metric-value">{stamina_exhaustion_fights} ({exhaustion_rate:.1f}%)</span>
                        </div>
                        <div class="overview-metric-row">
                            <span class="overview-metric-label">Fights with 0 stamina encounters:</span>
                            <span class="overview-metric-value">{zero_stamina_encounters} ({zero_stamina_rate:.1f}%)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <style>
        .stamina-chart-overview {{ margin: 15px 0; }}
        .stamina-bar-overview {{ display: flex; height: 35px; border-radius: 6px; overflow: hidden; border: 1px solid #e5e7eb; }}
        .stamina-segment-overview {{ display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.8rem; }}
        .stamina-segment-overview.high {{ background: #10b981; }}
        .stamina-segment-overview.mid {{ background: #f59e0b; }}
        .stamina-segment-overview.low {{ background: #ef4444; }}
        .zero-stamina-overview {{ }}
        .overview-metric-row {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #f3f4f6; }}
        .overview-metric-row:last-child {{ border-bottom: none; }}
        .overview-metric-label {{ font-size: 0.85rem; color: #6b7280; }}
        .overview-metric-value {{ font-weight: bold; color: #374151; font-size: 0.9rem; }}
        </style>
    """

def generate_roles_tab(results: Dict) -> str:
    """Generate roles and winrates tab"""

    # Extract role data directly from results
    roles_table = generate_role_distribution_table(results)

    # Generate filtered winrate tables
    winrate_table_2stat = generate_winrate_matrix_table_filtered(results, "2stat")
    winrate_table_3stat = generate_winrate_matrix_table_filtered(results, "3stat")
    winrate_table_extreme = generate_winrate_matrix_table_filtered(results, "extreme")

    return f"""
        <div id="roles" class="tab-content">
            <div class="card">
                <h3>🏆 Winrate Matrix - 2-Stat Builds + Universal</h3>
                {winrate_table_2stat}
            </div>

            <div class="card">
                <h3>🏆 Winrate Matrix - 3-Stat Builds + Universal</h3>
                {winrate_table_3stat}
            </div>

            <div class="card">
                <h3>🏆 Winrate Matrix - Extreme Builds + Universal</h3>
                {winrate_table_extreme}
            </div>

            <div class="card">
                <h3>⚔️ Role Distribution</h3>
                {roles_table}
            </div>
        </div>
    """

def generate_balance_tab(results: Dict) -> str:
    """Generate balance analysis tab"""

    return f"""
        <div id="balance" class="tab-content">
            <div class="card">
                <h3>⚖️ Balance Validation</h3>
                <div class="balance-grid">
                    {generate_balance_metrics_html(results)}
                </div>
            </div>

            <div class="card">
                <h3>⚡ Combat Mechanics</h3>
                {generate_old_mechanics_table(results)}
            </div>
        </div>
    """

def generate_builds_tab(results: Dict) -> str:
    """Generate builds by role tab - main new feature"""

    builds_by_role = results.get("builds_by_role", {})

    if not builds_by_role:
        return f"""
            <div id="builds" class="tab-content">
                <div class="card">
                    <p>No build data available</p>
                </div>
            </div>
        """

    # Generate role tabs for builds
    role_tabs = ""
    role_content = ""

    for i, (role, builds) in enumerate(builds_by_role.items()):
        active_class = "active" if i == 0 else ""
        role_tabs += f'<button class="role-tab {active_class}" onclick="openRoleTab(event, \'{role}\')">{role}</button>\n'

        builds_table = generate_builds_table(builds, role)
        role_content += f"""
            <div id="{role}" class="role-content {active_class}">
                {builds_table}
            </div>
        """

    return f"""
        <div id="builds" class="tab-content">
            <div class="card">
                <h3>🏗️ Builds by Role</h3>
                <div class="role-tabs">
                    {role_tabs}
                </div>
                <div class="role-contents">
                    {role_content}
                </div>
            </div>
        </div>
    """

def generate_combat_tab(results: Dict) -> str:
    """Generate mechanics analysis tab"""

    return f"""
        <div id="combat" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h3>🛡️ Skip Protection Analysis</h3>
                    {generate_skip_protection_table(results)}
                </div>

                <div class="card">
                    <h3>💥 Critical Hit Analysis</h3>
                    {generate_mechanics_table(results, "crit")}
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <h3>🎯 Hit Analysis</h3>
                    {generate_mechanics_table(results, "hit")}
                </div>

                <div class="card">
                    <h3>🦘 Dodge Analysis</h3>
                    {generate_mechanics_table(results, "dodge")}
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <h3>🛡️ Block Analysis</h3>
                    {generate_mechanics_table(results, "block")}
                </div>

                <div class="card">
                    <h3>💥 Block Break Analysis</h3>
                    {generate_mechanics_table(results, "block_break")}
                </div>
            </div>

            <div class="card">
                <h3>🔥 Damage Prevention Analysis</h3>
                {generate_damage_prevention_table(results)}
            </div>

            <div class="card">
                <h3>💎 Net Value Analysis</h3>
                {generate_net_value_table(results)}
            </div>

        </div>
    """

def generate_mechanics_table(results: Dict, mechanic_type: str):
    """Generate mechanics analysis table for specific mechanic"""
    role_mechanics = results.get("role_mechanics", {})

    if not role_mechanics:
        return f"<p>No {mechanic_type} data available</p>"

    rows = ""
    for role in sorted(role_mechanics.keys()):
        data = role_mechanics[role]
        fights = data.get("fights", 1)
        total_rounds = data.get("total_rounds", 1)
        mechanic_count = data.get(mechanic_type, 0)

        # Calculate metrics
        per_fight = mechanic_count / fights if fights > 0 else 0
        per_round = mechanic_count / total_rounds if total_rounds > 0 else 0

        # Special handling for crit damage
        if mechanic_type == "crit":
            crit_damage = data.get("crit_damage", 0.0)
            avg_crit_damage = crit_damage / mechanic_count if mechanic_count > 0 else 0
            rows += f"""
                <tr>
                    <td><strong>{role}</strong></td>
                    <td>{per_fight:.2f}</td>
                    <td>{per_round:.3f}</td>
                    <td>{avg_crit_damage:.1f}</td>
                    <td>{mechanic_count}</td>
                    <td>{fights}</td>
                </tr>
            """
        else:
            rows += f"""
                <tr>
                    <td><strong>{role}</strong></td>
                    <td>{per_fight:.2f}</td>
                    <td>{per_round:.3f}</td>
                    <td>{mechanic_count}</td>
                    <td>{fights}</td>
                </tr>
            """

    # Generate table headers based on mechanic type
    if mechanic_type == "crit":
        headers = """
            <th>Role</th>
            <th>Crits per Fight</th>
            <th>Crits per Round</th>
            <th>Avg Crit Damage</th>
            <th>Total Crits</th>
            <th>Fights</th>
        """
    else:
        mechanic_name = mechanic_type.replace("_", " ").title()
        headers = f"""
            <th>Role</th>
            <th>{mechanic_name}s per Fight</th>
            <th>{mechanic_name}s per Round</th>
            <th>Total {mechanic_name}s</th>
            <th>Fights</th>
        """

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        {headers}
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """

def generate_damage_prevention_table(results: Dict):
    """Generate damage prevention analysis table"""
    role_mechanics = results.get("role_mechanics", {})

    if not role_mechanics:
        return "<p>No damage prevention data available</p>"

    rows = ""
    for role in sorted(role_mechanics.keys()):
        data = role_mechanics[role]
        fights = data.get("fights", 1)
        total_rounds = data.get("total_rounds", 1)

        block_prevented = data.get("block_prevented", 0.0)
        dodge_prevented = data.get("dodge_prevented", 0.0)
        total_prevented = data.get("total_prevented", 0.0)

        # Calculate per-fight and per-round metrics
        block_per_fight = block_prevented / fights if fights > 0 else 0
        dodge_per_fight = dodge_prevented / fights if fights > 0 else 0
        total_per_fight = total_prevented / fights if fights > 0 else 0

        block_per_round = block_prevented / total_rounds if total_rounds > 0 else 0
        dodge_per_round = dodge_prevented / total_rounds if total_rounds > 0 else 0
        total_per_round = total_prevented / total_rounds if total_rounds > 0 else 0

        rows += f"""
            <tr>
                <td><strong>{role}</strong></td>
                <td>{block_per_fight:.1f}</td>
                <td>{dodge_per_fight:.1f}</td>
                <td>{total_per_fight:.1f}</td>
                <td>{block_per_round:.2f}</td>
                <td>{dodge_per_round:.2f}</td>
                <td>{total_per_round:.2f}</td>
                <td>{fights}</td>
            </tr>
        """

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Role</th>
                        <th>Block Prevented/Fight</th>
                        <th>Dodge Prevented/Fight</th>
                        <th>Total Prevented/Fight</th>
                        <th>Block Prevented/Round</th>
                        <th>Dodge Prevented/Round</th>
                        <th>Total Prevented/Round</th>
                        <th>Fights</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """

def generate_net_value_table(results: Dict):
    """Generate net value analysis table (damage dealt + damage prevented)"""
    role_mechanics = results.get("role_mechanics", {})

    if not role_mechanics:
        return "<p>No net value data available</p>"

    rows = ""
    # Sort roles by net value per fight (highest first)
    role_data = []
    for role, data in role_mechanics.items():
        fights = data.get("fights", 1)
        net_value = data.get("net_value", 0.0)
        net_per_fight = net_value / fights if fights > 0 else 0
        role_data.append((role, data, net_per_fight))

    role_data.sort(key=lambda x: x[2], reverse=True)

    for role, data, net_per_fight in role_data:
        fights = data.get("fights", 1)
        total_rounds = data.get("total_rounds", 1)

        net_value = data.get("net_value", 0.0)
        total_damage = data.get("total_damage", 0.0)
        total_prevented = data.get("total_prevented", 0.0)
        crit_bonus = data.get("crit_bonus_damage", 0.0)
        block_break_bonus = data.get("block_break_bonus", 0.0)

        # Calculate metrics
        damage_per_fight = total_damage / fights if fights > 0 else 0
        prevented_per_fight = total_prevented / fights if fights > 0 else 0
        net_per_round = net_value / total_rounds if total_rounds > 0 else 0

        # Calculate efficiency (net value per action)
        total_actions = data.get("hit", 0) + data.get("crit", 0) + data.get("dodge", 0) + data.get("block", 0)
        efficiency = net_value / total_actions if total_actions > 0 else 0

        rows += f"""
            <tr>
                <td><strong>{role}</strong></td>
                <td>{net_per_fight:.1f}</td>
                <td>{net_per_round:.2f}</td>
                <td>{damage_per_fight:.1f}</td>
                <td>{prevented_per_fight:.1f}</td>
                <td>{efficiency:.2f}</td>
                <td>{fights}</td>
            </tr>
        """

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Role</th>
                        <th>Net Value/Fight</th>
                        <th>Net Value/Round</th>
                        <th>Damage Dealt/Fight</th>
                        <th>Damage Prevented/Fight</th>
                        <th>Efficiency (Value/Action)</th>
                        <th>Fights</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """

def generate_raw_data_tab(results: Dict) -> str:
    """Generate raw data tab"""

    # Convert tuples and other non-JSON types to strings for display
    def convert_for_json(obj):
        if isinstance(obj, tuple):
            return list(obj)  # Convert tuples to lists
        elif hasattr(obj, '__dict__'):
            return str(obj)  # Convert complex objects to strings
        return obj

    # Deep copy and convert
    import copy
    cleaned_results = copy.deepcopy(results)

    # Remove problematic keys that have tuples
    if 'builds_used' in cleaned_results:
        # Convert tuple keys to string representations
        builds_used = {}
        for build_tuple, count in cleaned_results['builds_used'].items():
            if isinstance(build_tuple, tuple):
                builds_used[str(build_tuple)] = count
            else:
                builds_used[build_tuple] = count
        cleaned_results['builds_used'] = builds_used

    return f"""
        <div id="raw" class="tab-content">
            <div class="card">
                <h3>🔧 Raw Data (JSON)</h3>
                <pre id="raw-json">{json.dumps(cleaned_results, indent=2, default=convert_for_json)}</pre>
                <button onclick="copyRawData()">📋 Copy to Clipboard</button>
            </div>
        </div>
    """

# Helper functions for generating specific components
def generate_builds_table(builds: List, role: str) -> str:
    """Generate table of builds for a specific role"""

    if not builds:
        return f"<p>No {role} builds found in this benchmark.</p>"

    # Sort builds by confidence (descending)
    sorted_builds = sorted(builds, key=lambda x: x.get('confidence', 0), reverse=True)

    rows = ""
    for i, build in enumerate(sorted_builds):
        hp = build.get('hp_stat', build.get('hp', 0))
        attack = build.get('attack', 0)
        defense = build.get('defense', 0)
        agility = build.get('agility', 0)
        confidence = build.get('confidence', 0)
        fights = build.get('fights', 0)

        total_stats = hp + attack + defense + agility
        confidence_class = "high-conf" if confidence > 0.15 else "low-conf" if confidence < 0.05 else "mid-conf"

        rows += f"""
            <tr>
                <td>{i+1}</td>
                <td>{hp}</td>
                <td>{attack}</td>
                <td>{defense}</td>
                <td>{agility}</td>
                <td>{total_stats}</td>
                <td><span class="confidence {confidence_class}">{confidence:.3f}</span></td>
                <td>{fights}</td>
            </tr>
        """

    return f"""
        <div class="builds-summary">
            <p><strong>{len(builds)}</strong> unique {role} builds found</p>
            <p>Average confidence: <strong>{sum(b.get('confidence', 0) for b in builds) / len(builds):.3f}</strong></p>
        </div>
        <div class="table-wrapper">
            <table class="builds-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>HP</th>
                        <th>ATK</th>
                        <th>DEF</th>
                        <th>AGI</th>
                        <th>Total</th>
                        <th>Confidence</th>
                        <th>Fights</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """

# More helper functions will be added...

def get_css_styles() -> str:
    """Return CSS styles for the HTML"""
    return """
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .meta-info {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .tabs {
            display: flex;
            background: white;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            flex-wrap: wrap;
        }

        .tab-button {
            background: none;
            border: none;
            padding: 12px 20px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            margin-right: 5px;
            margin-bottom: 5px;
        }

        .tab-button:hover {
            background: #f0f0f0;
        }

        .tab-button.active {
            background: #667eea;
            color: white;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .card h3 {
            margin-bottom: 20px;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
            .meta-info {
                flex-direction: column;
                gap: 5px;
            }
        }

        .stat-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .stat {
            display: flex;
            flex-direction: column;
            text-align: center;
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
        }

        .stat-label {
            font-size: 0.85rem;
            color: #6b7280;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1f2937;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }

        tr:hover {
            background: #f9fafb;
        }

        .builds-table th,
        .builds-table td {
            text-align: center;
        }

        .table-wrapper {
            overflow-x: auto;
            margin-top: 15px;
        }

        .confidence.high-conf {
            background: #10b981;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }

        .confidence.mid-conf {
            background: #f59e0b;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }

        .confidence.low-conf {
            background: #ef4444;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }

        .role-tabs {
            display: flex;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .role-tab {
            background: #f1f5f9;
            border: none;
            padding: 10px 15px;
            margin-right: 5px;
            margin-bottom: 5px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .role-tab:hover {
            background: #e2e8f0;
        }

        .role-tab.active {
            background: #3b82f6;
            color: white;
        }

        .role-content {
            display: none;
        }

        .role-content.active {
            display: block;
        }

        .builds-summary {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        pre {
            background: #1f2937;
            color: #e5e7eb;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.85rem;
            line-height: 1.4;
        }

        button {
            font-family: inherit;
        }
    """

def get_javascript() -> str:
    """Return JavaScript for tab functionality"""
    return """
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;

            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }

            tablinks = document.getElementsByClassName("tab-button");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].classList.remove("active");
            }

            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }

        function openRoleTab(evt, roleName) {
            var i, rolecontent, rolelinks;

            rolecontent = document.getElementsByClassName("role-content");
            for (i = 0; i < rolecontent.length; i++) {
                rolecontent[i].classList.remove("active");
            }

            rolelinks = document.getElementsByClassName("role-tab");
            for (i = 0; i < rolelinks.length; i++) {
                rolelinks[i].classList.remove("active");
            }

            document.getElementById(roleName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }

        function copyRawData() {
            const rawData = document.getElementById('raw-json').textContent;
            navigator.clipboard.writeText(rawData).then(function() {
                alert('Raw data copied to clipboard!');
            });
        }
    """

# Helper function implementations
def generate_role_distribution_table(results):
    """Generate role distribution table"""
    fights = results.get("fights", [])
    if not fights:
        return "<p>No role data available</p>"

    # Count roles from fight data (same logic as console output)
    from collections import Counter
    role_a = [fight["fighter_a"]["role"] for fight in fights]
    role_b = [fight["fighter_b"]["role"] for fight in fights]

    role_counter_a = Counter(role_a)
    role_counter_b = Counter(role_b)

    # Combine A and B role counts
    combined_roles = {}
    for role, count in role_counter_a.items():
        combined_roles[role] = combined_roles.get(role, 0) + count
    for role, count in role_counter_b.items():
        combined_roles[role] = combined_roles.get(role, 0) + count

    total_fighters = sum(combined_roles.values())

    if total_fighters == 0:
        return "<p>No role data available</p>"

    # Generate table with separate A and B columns
    rows = ""
    for role in sorted(combined_roles.keys()):
        count_a = role_counter_a.get(role, 0)
        count_b = role_counter_b.get(role, 0)
        total_count = count_a + count_b
        percentage = (total_count / total_fighters * 100) if total_fighters > 0 else 0

        rows += f"""
            <tr>
                <td><strong>{role}</strong></td>
                <td>{count_a}</td>
                <td>{count_b}</td>
                <td>{total_count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
        """

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Role</th>
                        <th>Fighter A</th>
                        <th>Fighter B</th>
                        <th>Total</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """

def categorize_roles(roles):
    """Categorize roles into 2-stat, 3-stat, extreme, and universal"""
    extreme_builds = {"ATK", "AGI", "DEF", "HP"}
    universal_builds = {"UNIVERSAL"}

    # 2-stat builds have exactly 2 underscores in name (e.g., ATK_DEF)
    two_stat_builds = set()
    three_stat_builds = set()

    for role in roles:
        if role in extreme_builds or role in universal_builds:
            continue

        underscore_count = role.count('_')
        if underscore_count == 1:  # ATK_DEF, AGI_HP, etc.
            two_stat_builds.add(role)
        elif underscore_count == 2:  # ATK_HP_DEF, AGI_DEF_ATK, etc.
            three_stat_builds.add(role)

    return {
        "2stat": two_stat_builds | universal_builds,
        "3stat": three_stat_builds | universal_builds,
        "extreme": extreme_builds | universal_builds
    }

def generate_winrate_matrix_table_filtered(results, role_filter):
    """Generate winrate matrix table with role filtering"""
    role_analysis = results.get("role_analysis", {})
    role_matchups = results.get("role_matchups", {})

    if not role_analysis:
        return "<p>No winrate data available</p>"

    # Get all roles that appear in fights and filter by category
    all_roles = set(role_analysis.keys())
    role_categories = categorize_roles(all_roles)

    # Filter roles based on the requested filter
    if role_filter in role_categories:
        filtered_roles = role_categories[role_filter] & all_roles  # Only roles that actually appear in data
    else:
        filtered_roles = all_roles

    sorted_roles_list = sorted(filtered_roles)

    if not sorted_roles_list:
        return "<p>No winrate data available</p>"

    # Calculate overall winrates for each role
    overall_winrates = {}
    for role, stats in role_analysis.items():
        if role in filtered_roles:  # Only include filtered roles
            overall_winrates[role] = {
                "winrate": stats["winrate"],
                "total": stats["fights"]
            }

    # Helper function to get matchup winrate
    def get_matchup_winrate(role_a, role_b):
        if role_a == role_b:
            return None, "N/A"

        matchup_key = f"{role_a}_vs_{role_b}"
        if matchup_key in role_matchups:
            stats = role_matchups[matchup_key]
            if stats["total"] > 0:
                winrate = (stats["wins"] + 0.5 * stats["draws"]) / stats["total"]
                return winrate, f"{winrate*100:.1f}%"
        return 0, "0.0%"

    # Generate header
    header = "<tr><th>Role</th>"
    for role in sorted_roles_list:
        header += f"<th>vs {role}</th>"
    header += "<th>Overall</th></tr>"

    # Generate rows
    rows = ""
    for attacker_role in sorted_roles_list:
        row = f"<tr><td><strong>{attacker_role}</strong></td>"

        for defender_role in sorted_roles_list:
            if attacker_role == defender_role:
                row += "<td>-</td>"
            else:
                winrate_val, winrate_str = get_matchup_winrate(attacker_role, defender_role)
                if winrate_val is None:
                    row += "<td>-</td>"
                else:
                    winrate_pct = winrate_val * 100
                    # New color coding: green (40-60), yellow (35-40 and 60-65), red (rest)
                    if 40 <= winrate_pct <= 60:
                        color_class = "balanced"  # Green - balanced range
                    elif (35 <= winrate_pct < 40) or (60 < winrate_pct <= 65):
                        color_class = "warning"   # Yellow - slightly unbalanced
                    else:
                        color_class = "extreme"   # Red - extreme values
                    row += f'<td><span class="winrate {color_class}">{winrate_str}</span></td>'

        # Overall winrate
        if attacker_role in overall_winrates:
            overall = overall_winrates[attacker_role]
            overall_pct = overall['winrate'] * 100
            # Same color coding for overall
            if 40 <= overall_pct <= 60:
                overall_color = "balanced"  # Green - balanced range
            elif (35 <= overall_pct < 40) or (60 < overall_pct <= 65):
                overall_color = "warning"   # Yellow - slightly unbalanced
            else:
                overall_color = "extreme"   # Red - extreme values
            row += f'<td><span class="winrate {overall_color}"><strong>{overall_pct:.1f}%</strong> ({overall["total"]} fights)</span></td>'
        else:
            row += '<td>-</td>'

        row += "</tr>"
        rows += row

    return f"""
        <div class="table-wrapper">
            <table class="winrate-matrix">
                <thead>{header}</thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        <style>
        .winrate.balanced {{ background: #10b981; color: white; padding: 2px 4px; border-radius: 3px; font-size: 0.85rem; }}  /* Green: 40-60% */
        .winrate.warning {{ background: #f59e0b; color: white; padding: 2px 4px; border-radius: 3px; font-size: 0.85rem; }}   /* Yellow: 35-40% and 60-65% */
        .winrate.extreme {{ background: #ef4444; color: white; padding: 2px 4px; border-radius: 3px; font-size: 0.85rem; }}   /* Red: <35% or >65% */
        .winrate-matrix {{ font-size: 0.9rem; }}
        .winrate-matrix td {{ text-align: center; padding: 8px 4px; }}
        .winrate-matrix th {{ text-align: center; padding: 8px 4px; font-size: 0.85rem; }}
        .winrate-matrix th:first-child {{ min-width: 100px; }}
        .winrate-matrix th {{ white-space: nowrap; }}

        /* Responsive design for narrow screens */
        @media (max-width: 1400px) {{
            .winrate-matrix {{ font-size: 0.85rem; }}
            .winrate-matrix th, .winrate-matrix td {{ padding: 6px 3px; }}
            .winrate.balanced, .winrate.warning, .winrate.extreme {{ font-size: 0.8rem; padding: 1px 3px; }}
        }}

        @media (max-width: 1200px) {{
            .winrate-matrix {{ font-size: 0.8rem; }}
            .winrate-matrix th, .winrate-matrix td {{ padding: 6px 2px; }}
            .winrate.balanced, .winrate.warning, .winrate.extreme {{ font-size: 0.75rem; padding: 1px 3px; }}
            .winrate-matrix th:first-child {{ min-width: 90px; }}
        }}

        @media (max-width: 768px) {{
            .winrate-matrix {{ font-size: 0.75rem; }}
            .winrate-matrix th, .winrate-matrix td {{ padding: 4px 1px; }}
            .winrate.balanced, .winrate.warning, .winrate.extreme {{ font-size: 0.7rem; padding: 1px 2px; }}
            .winrate-matrix th:first-child {{ min-width: 70px; }}
        }}
        </style>
    """

def generate_winrate_matrix_table(results):
    """Generate winrate matrix table (original function for compatibility)"""
    return generate_winrate_matrix_table_filtered(results, "all")

def generate_balance_metrics_html(results):
    """Generate balance validation metrics"""

    # Calculate metrics same way as console output
    summary = results.get("summary", {})
    total = summary.get("total_fights", 1)
    winners = summary.get("winners", {})

    # Calculate base metrics
    avg_rounds = summary.get('avg_rounds', 0)
    avg_dps = sum(results.get("dps_data", [])) / len(results.get("dps_data", [1])) if results.get("dps_data") else 0
    draw_rate = (winners.get("DRAW_TIMEOUT", 0) + winners.get("DRAW_MUTUAL_DEATH", 0)) / total if total > 0 else 0
    stamina_exhaustion_rate = results.get("stamina_exhaustion_fights", 0) / total if total > 0 else 0

    # Calculate mechanics averages
    mechanics_avg = {}
    if results.get("mechanics_data"):
        for k, v in results["mechanics_data"].items():
            mechanics_avg[k] = v / total

    # Calculate damage averages
    damage_avg = {}
    if results.get("damage_data"):
        for k, v in results["damage_data"].items():
            damage_avg[k] = v / total

    # Calculate stamina averages
    stamina_avg = {}
    if results.get("stamina_data"):
        for k, v in results["stamina_data"].items():
            stamina_avg[k] = v / total

    # Calculate role balance spread
    role_analysis = results.get("role_analysis", {})
    role_balance_spread = 0.0
    if role_analysis:
        winrates = [data["winrate"] for data in role_analysis.values()]
        if len(winrates) >= 2:
            role_balance_spread = max(winrates) - min(winrates)

    # Import validation logic
    try:
        from balance.validator import validate_single_metric
        from balance.targets import TARGETS
    except ImportError:
        return "<p>Balance validator not available</p>"

    # Define metrics to validate with actual target ranges
    validation_metrics = [
        ("rounds_avg", avg_rounds, f"{TARGETS['rounds_avg'][0]} - {TARGETS['rounds_avg'][1]}"),
        ("dps_avg", avg_dps, f"{TARGETS['dps_avg'][0]} - {TARGETS['dps_avg'][1]}"),
        ("draw_rate", draw_rate, f"{TARGETS['draw_rate'][0]} - {TARGETS['draw_rate'][1]}"),
        ("stamina_exhaustion_rate", stamina_exhaustion_rate, f"{TARGETS['stamina_exhaustion_rate'][0]} - {TARGETS['stamina_exhaustion_rate'][1]}"),
    ]

    # Add mechanics validation
    for mechanic in ['dodge', 'block', 'block_break', 'hit']:
        if mechanic in mechanics_avg and mechanic in TARGETS:
            low, high = TARGETS[mechanic]
            validation_metrics.append((mechanic, mechanics_avg[mechanic], f"{low} - {high}"))

    # Add damage validation
    for damage_type in ['crit_dmg', 'normal_dmg', 'blocked_dmg']:
        damage_key = damage_type.replace('_dmg', '')
        if damage_key in damage_avg and damage_type in TARGETS:
            low, high = TARGETS[damage_type]
            validation_metrics.append((damage_type, damage_avg[damage_key], f"{low} - {high}"))

    # Add stamina validation
    for stamina_level in ['stamina_high', 'stamina_mid', 'stamina_low']:
        stamina_key = stamina_level.replace('stamina_', '')
        if stamina_key in stamina_avg and stamina_level in TARGETS:
            low, high = TARGETS[stamina_level]
            validation_metrics.append((stamina_level, stamina_avg[stamina_key], f"{low} - {high}"))

    # Add role balance
    if 'role_balance_spread' in TARGETS:
        low, high = TARGETS['role_balance_spread']
        validation_metrics.append(("role_balance_spread", role_balance_spread, f"{low} - {high}"))

    # Run validation
    rows = ""
    all_passed = True

    for metric_name, value, expected_range in validation_metrics:
        try:
            is_valid = validate_single_metric(metric_name, value)
            status = "passed" if is_valid else "failed"

            if not is_valid:
                all_passed = False

            status_icon = "✅" if is_valid else "❌"
            status_class = status

            # Format value
            if isinstance(value, float):
                if value < 1:
                    display_value = f"{value:.4f}"
                else:
                    display_value = f"{value:.1f}"
            else:
                display_value = str(value)

            rows += f"""
                <tr class="balance-{status}">
                    <td>{status_icon} {metric_name}</td>
                    <td>{display_value}</td>
                    <td>{expected_range}</td>
                    <td><span class="status {status_class}">{status.upper()}</span></td>
                </tr>
            """
        except Exception as e:
            # Skip metrics that can't be validated
            continue

    if not rows:
        return "<p>No balance validation data available</p>"

    overall_status = "PASSED" if all_passed else "FAILED"
    overall_icon = "✅" if all_passed else "❌"

    return f"""
        <div class="balance-summary">
            <h4>{overall_icon} Overall Balance Test: {overall_status}</h4>
        </div>
        <div class="table-wrapper">
            <table class="balance-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Actual Value</th>
                        <th>Expected Range</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <style>
        .balance-summary {{ margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 6px; }}
        .status.passed {{ background: #10b981; color: white; padding: 2px 8px; border-radius: 3px; }}
        .status.failed {{ background: #ef4444; color: white; padding: 2px 8px; border-radius: 3px; }}
        .balance-failed {{ background: #fef2f2; }}
        .balance-passed {{ background: #f0fdf4; }}
        </style>
    """

def generate_old_mechanics_table(results):
    """Generate combat mechanics table (old version)"""

    # Calculate mechanics averages same way as console output
    total = results.get("summary", {}).get("total_fights", 1)
    mechanics_avg = {}
    if results.get("mechanics_data"):
        for k, v in results["mechanics_data"].items():
            mechanics_avg[k] = v / total

    if not mechanics_avg:
        return "<p>No mechanics data available</p>"

    rows = ""
    for mechanic in ['hit', 'crit', 'dodge', 'block', 'block_break', 'crit_block', 'crit_block_break']:
        if mechanic in mechanics_avg:
            value = mechanics_avg[mechanic]
            percentage = value * 100

            # Color coding based on mechanic type
            color_class = ""
            if mechanic == 'hit':
                color_class = "primary"
            elif 'crit' in mechanic:
                color_class = "success"
            elif mechanic in ['dodge', 'block']:
                color_class = "info"
            elif mechanic in ['block_break']:
                color_class = "warning"

            # Format display name
            display_name = mechanic.replace('_', ' ').title()

            rows += f"""
                <tr>
                    <td><strong>{display_name}</strong></td>
                    <td><span class="mechanic-value {color_class}">{percentage:.1f}%</span></td>
                </tr>
            """

    if not rows:
        return "<p>No mechanics data available</p>"

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Mechanic</th>
                        <th>Frequency</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <style>
        .mechanic-value {{ padding: 2px 8px; border-radius: 3px; font-weight: bold; }}
        .mechanic-value.primary {{ background: #3b82f6; color: white; }}
        .mechanic-value.success {{ background: #10b981; color: white; }}
        .mechanic-value.info {{ background: #06b6d4; color: white; }}
        .mechanic-value.warning {{ background: #f59e0b; color: white; }}
        </style>
    """

def generate_damage_table(results):
    """Generate damage distribution table"""

    # Calculate damage averages same way as console output
    total = results.get("summary", {}).get("total_fights", 1)
    damage_avg = {}
    if results.get("damage_data"):
        for k, v in results["damage_data"].items():
            damage_avg[k] = v / total

    if not damage_avg:
        return "<p>No damage data available</p>"

    # Calculate total damage for percentage calculation
    total_damage = sum(damage_avg.values())

    if total_damage <= 0:
        return "<p>No damage data available</p>"

    rows = ""
    # Use the actual available damage types
    for damage_type, value in damage_avg.items():
        percentage = (value / total_damage * 100) if total_damage > 0 else 0

        display_name = damage_type.replace('_', ' ').title() + " Damage"

        color_class = ""
        if damage_type == 'normal':
            color_class = "primary"
        elif damage_type == 'crit':
            color_class = "success"
        elif damage_type == 'blocked':
            color_class = "warning"
        else:
            color_class = "info"  # Default for any other damage types

        rows += f"""
            <tr>
                <td><strong>{display_name}</strong></td>
                <td><span class="damage-value {color_class}">{percentage:.1f}%</span></td>
            </tr>
        """

    if not rows:
        return "<p>No damage data available</p>"

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Damage Type</th>
                        <th>Share</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <style>
        .damage-value {{ padding: 2px 8px; border-radius: 3px; font-weight: bold; }}
        .damage-value.primary {{ background: #3b82f6; color: white; }}
        .damage-value.success {{ background: #10b981; color: white; }}
        .damage-value.warning {{ background: #f59e0b; color: white; }}
        .damage-value.info {{ background: #06b6d4; color: white; }}
        </style>
    """

def generate_skip_protection_table(results):
    """Generate skip protection analysis table"""
    role_absorption = results.get("role_absorption", {})

    if not role_absorption:
        return "<p>No skip protection data available</p>"

    rows = ""
    for role in sorted(role_absorption.keys()):
        data = role_absorption[role]
        fights = data.get("fights", 1)
        skip_events = data.get("skip_events", 0)
        avg_per_fight = skip_events / fights if fights > 0 else 0

        # Calculate efficiency (skip events per round)
        total_rounds = data.get("total_rounds", 1)
        efficiency = skip_events / total_rounds if total_rounds > 0 else 0

        rows += f"""
            <tr>
                <td><strong>{role}</strong></td>
                <td>{avg_per_fight:.2f}</td>
                <td>{efficiency:.3f}</td>
                <td>{skip_events}</td>
                <td>{fights}</td>
            </tr>
        """

    return f"""
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Role</th>
                        <th>Skip per Fight</th>
                        <th>Efficiency</th>
                        <th>Total Skip Events</th>
                        <th>Fights</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """

def generate_crit_analysis(results):
    """Generate critical hit analysis"""
    crit_metrics = results.get("crit_metrics_avg", {})

    if not crit_metrics:
        return "<p>No critical hit data available</p>"

    raw_rate = crit_metrics.get("raw_crit_rate", 0) * 100
    effective_rate = crit_metrics.get("effective_crit_rate", 0) * 100
    damage_ratio = crit_metrics.get("crit_damage_ratio", 0) * 100

    total_rolls = crit_metrics.get("total_rolls", 0)
    crit_rolls = crit_metrics.get("crit_rolls", 0)
    successful_hits = crit_metrics.get("successful_hits", 0)
    crit_hits = crit_metrics.get("crit_hits", 0)

    return f"""
        <div class="crit-stats">
            <div class="stat-row">
                <span class="stat-label">Raw Crit Rate:</span>
                <span class="stat-value">{raw_rate:.1f}% ({crit_rolls}/{total_rolls} rolls)</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Effective Crit Rate:</span>
                <span class="stat-value">{effective_rate:.1f}% ({crit_hits}/{successful_hits} hits)</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Crit Damage Ratio:</span>
                <span class="stat-value">{damage_ratio:.1f}% of total damage</span>
            </div>
        </div>
        <style>
        .crit-stats {{ display: flex; flex-direction: column; gap: 10px; }}
        .stat-row {{ display: flex; justify-content: space-between; padding: 8px; background: #f8fafc; border-radius: 4px; }}
        .stat-label {{ font-weight: 600; }}
        .stat-value {{ color: #059669; font-weight: bold; }}
        </style>
    """

def generate_stamina_chart(results):
    """Generate stamina distribution visualization"""
    stamina_data = results.get("stamina_data", {})

    if not stamina_data:
        return "<p>No stamina data available</p>"

    # Calculate percentages from stamina time distribution
    total_time = sum(stamina_data.values()) or 1
    high = (stamina_data.get("high", 0) / total_time) * 100
    mid = (stamina_data.get("mid", 0) / total_time) * 100
    low = (stamina_data.get("low", 0) / total_time) * 100

    return f"""
        <div class="stamina-chart">
            <div class="stamina-bar">
                <div class="stamina-segment high" style="width: {high:.1f}%">
                    <span>Fresh: {high:.1f}%</span>
                </div>
                <div class="stamina-segment mid" style="width: {mid:.1f}%">
                    <span>Tired: {mid:.1f}%</span>
                </div>
                <div class="stamina-segment low" style="width: {low:.1f}%">
                    <span>Exhausted: {low:.1f}%</span>
                </div>
            </div>
        </div>
        <style>
        .stamina-chart {{ margin: 15px 0; }}
        .stamina-bar {{ display: flex; height: 40px; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; }}
        .stamina-segment {{ display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9rem; }}
        .stamina-segment.high {{ background: #10b981; }}
        .stamina-segment.mid {{ background: #f59e0b; }}
        .stamina-segment.low {{ background: #ef4444; }}
        </style>
    """

def generate_zero_stamina_encounters(results):
    """Generate zero stamina encounters metrics"""
    total_fights = results.get("summary", {}).get("total_fights", 1)
    stamina_exhaustion_fights = results.get("stamina_exhaustion_fights", 0)
    zero_stamina_encounters = results.get("zero_stamina_encounters", 0)

    # Calculate percentages
    exhaustion_rate = (stamina_exhaustion_fights / total_fights * 100) if total_fights > 0 else 0
    zero_stamina_rate = (zero_stamina_encounters / total_fights * 100) if total_fights > 0 else 0

    return f"""
        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <h4 style="margin: 0 0 15px 0; color: #374151;">💥 Zero Stamina Analysis</h4>
            <div class="zero-stamina-metrics">
                <div class="metric-row">
                    <span class="metric-label">Fights ending in stamina draw (both can't attack):</span>
                    <span class="metric-value">{stamina_exhaustion_fights} ({exhaustion_rate:.1f}%)</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Fights with 0 stamina encounters:</span>
                    <span class="metric-value">{zero_stamina_encounters} ({zero_stamina_rate:.1f}%)</span>
                </div>
            </div>
        </div>

        <style>
        .zero-stamina-metrics {{ margin: 10px 0; }}
        .metric-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f3f4f6; }}
        .metric-row:last-child {{ border-bottom: none; }}
        .metric-label {{ font-size: 0.9rem; color: #6b7280; }}
        .metric-value {{ font-weight: bold; color: #374151; }}
        </style>
    """

def generate_rounds_distribution_chart(results):
    """Generate rounds distribution chart"""
    rounds_dist = results.get("rounds_distribution", {})

    if not rounds_dist:
        return ""

    total_fights = sum(rounds_dist.values())
    avg_rounds = results.get("rounds_avg", 0)

    # Create simple bar chart
    bars = ""
    max_count = max(rounds_dist.values()) if rounds_dist else 1

    for rounds in sorted(rounds_dist.keys()):
        count = rounds_dist[rounds]
        percentage = (count / total_fights * 100) if total_fights > 0 else 0
        bar_width = (count / max_count * 100) if max_count > 0 else 0

        bars += f"""
            <div class="round-bar">
                <span class="round-label">{rounds} rounds</span>
                <div class="bar-container">
                    <div class="bar-fill" style="width: {bar_width}%"></div>
                    <span class="bar-text">{count} fights ({percentage:.1f}%)</span>
                </div>
            </div>
        """

    return f"""
        <div class="card">
            <h3>📊 Fight Duration Distribution</h3>
            <p><strong>Average:</strong> {avg_rounds:.1f} rounds | <strong>Total:</strong> {total_fights} fights</p>
            <div class="rounds-chart">
                {bars}
            </div>
        </div>
        <style>
        .rounds-chart {{ margin: 15px 0; }}
        .round-bar {{ margin: 8px 0; }}
        .round-label {{ display: inline-block; width: 80px; font-weight: bold; }}
        .bar-container {{ position: relative; background: #f3f4f6; height: 25px; border-radius: 4px; margin-left: 10px; display: inline-block; width: calc(100% - 90px); }}
        .bar-fill {{ position: absolute; background: #3b82f6; height: 100%; border-radius: 4px; transition: width 0.3s; }}
        .bar-text {{ position: absolute; left: 8px; top: 50%; transform: translateY(-50%); font-size: 0.85rem; z-index: 1; }}
        </style>
    """