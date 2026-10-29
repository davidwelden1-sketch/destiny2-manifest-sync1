"""Deterministic timing arithmetic, not Destiny 2 cooldown calibration."""
from math import isfinite

def cooldown_seconds(base_seconds, regen_rate_multiplier):
    if not all(type(x) in (float, int) and isfinite(x) and x > 0
               for x in (base_seconds, regen_rate_multiplier)):
        raise ValueError("positive finite cooldown and regeneration required")
    return {"seconds": base_seconds / regen_rate_multiplier,
            "model_only": True, "measured_in_game": False}

def uptime_fraction(active_seconds, cycle_seconds):
    if not all(type(x) in (float, int) and isfinite(x) and x > 0
               for x in (active_seconds, cycle_seconds)):
        raise ValueError("positive finite timing inputs required")
    return {"fraction": min(1.0, active_seconds / cycle_seconds),
            "model_only": True, "measured_in_game": False}
