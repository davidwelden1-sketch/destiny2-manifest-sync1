"""Deterministic action-sequence damage model; timing and numbers supplied by caller."""
def simulate_rotation(actions, window_seconds):
    if window_seconds <= 0:
        raise ValueError("Window must be positive")
    events = []
    for action in actions:
        t = float(action["time"])
        damage = float(action["damage"])
        if t < 0 or damage < 0:
            raise ValueError("Invalid action")
        if t < window_seconds:
            events.append((t, damage))
    total = sum(d for _, d in events)
    return {"total_damage": total, "dps": total/window_seconds,
            "event_count": len(events), "model": "user-supplied event timing and damage"}
