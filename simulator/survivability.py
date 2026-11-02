"""Survivability arithmetic with explicitly provided damage resistance."""
from math import prod, isfinite

def effective_resistance(resistances, policy="multiplicative"):
    resistances = list(resistances)
    if any(type(r) not in (int, float) or not isfinite(r) or not 0 <= r < 1 for r in resistances):
        raise ValueError("Resistance fractions must be in [0,1)")
    if policy == "multiplicative":
        return 1 - prod(1-r for r in resistances)
    if policy == "highest":
        return max([0.0, *resistances])
    raise ValueError("Unknown resistance policy")

def effective_health(health, shields=0, resistances=(), policy="multiplicative"):
    if not all(type(v) in (int, float) and isfinite(v) for v in (health, shields)) or health <= 0 or shields < 0:
        raise ValueError("Invalid health or shields")
    # Many individually valid resistance factors can underflow the surviving
    # damage fraction to zero. Never emit a fictitious infinite EHP.
    remaining = 1 - effective_resistance(resistances, policy)
    if remaining <= 0:
        raise ValueError("Combined resistance is numerically indistinguishable from 100%")
    ehp = (health + shields) / remaining
    if not isfinite(ehp):
        raise ValueError("Effective health is nonfinite")
    return ehp
