# V14 RESET - meta_layer.py

def update_meta(state, events):
    """
    READ-ONLY ANALYTICS LAYER
    MUST NOT influence combat
    """

    if not events:
        state.momentum = 0
        state.deadlock_pressure = 0
        return

    # Calculate damage from structured events
    dmg_a = 0.0
    dmg_b = 0.0

    for event in events:
        for attack in event.get("attacks", []):
            # Handle both "target" (legacy) and "defender" (new API)
            target = attack.get("target") or attack.get("defender")
            if target == "A":
                dmg_a += attack["damage"]
            elif target == "B":
                dmg_b += attack["damage"]

    state.momentum = (dmg_b - dmg_a) / max(1, (dmg_a + dmg_b))

    # simple deadlock detection
    if abs(dmg_a - dmg_b) < 10:
        state.deadlock_pressure = 0.1
    else:
        state.deadlock_pressure = 0.0