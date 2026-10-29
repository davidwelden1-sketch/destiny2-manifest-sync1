"""Survivability arithmetic with explicitly provided damage resistance."""
from math import prod, isfinite

def effective_resistance(resistances, policy="multiplicative"):
    resistances = list(resistances)
    if any(not isinstance(r, (int, float)) or not isfinite(r) or not 0 <= r < 1 for r in resistances):
        raise ValueError("Resistance fractions must be in [0,1)")
    if policy == "multiplicative":
        return 1 - prod(1-r for r in resistances)
    if policy == "highest":
        return max([0.0, *resistances])
    raise ValueError("Unknown resistance policy")

def effective_health(health, shields=0, resistances=(), policy="multiplicative"):
    if not all(isinstance(v, (int, float)) and isfinite(v) for v in (health, shields)) or health <= 0 or shields < 0:
        raise ValueError("Invalid health or shields")
    return (health + shields) / (1-effective_resistance(resistances, policy))
