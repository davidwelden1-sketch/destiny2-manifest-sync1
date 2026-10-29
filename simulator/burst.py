"""Explicit shot-timing sequences for burst and nonuniform weapons."""
def time_to_kill_sequence(health, shot_events):
    if health <= 0:
        raise ValueError("Health must be positive")
    accumulated = 0.0
    previous = -1.0
    for t, damage in shot_events:
        if t < 0 or t < previous or damage < 0:
            raise ValueError("Events must be nonnegative and ordered")
        previous = t
        accumulated += damage
        if accumulated + 1e-9 >= health:
            return t
    return None
