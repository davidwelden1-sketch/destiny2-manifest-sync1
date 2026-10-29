"""Simple recharge model, not an in-game Destiny ability model."""
def recharge_seconds(base_seconds, rate_multiplier=1.0, flat_reduction=0.0):
    if base_seconds <= 0 or rate_multiplier <= 0 or flat_reduction < 0:
        raise ValueError("Invalid cooldown inputs")
    return max(0.0, base_seconds / rate_multiplier - flat_reduction)

def uptime_fraction(active_seconds, cooldown_seconds, starts_on_activation=True):
    if active_seconds < 0 or cooldown_seconds < 0:
        raise ValueError("Invalid duration")
    if active_seconds == 0:
        return 0.0
    if starts_on_activation:
        return min(1.0, active_seconds / max(active_seconds, cooldown_seconds))
    return active_seconds / (active_seconds + cooldown_seconds)
