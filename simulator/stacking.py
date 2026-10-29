"""Explicit stacking policies. No Destiny-specific stacking assumed."""
from math import prod

def combine_multipliers(values, policy="multiply"):
    values = list(values)
    if any(v <= 0 for v in values):
        raise ValueError("Multipliers must be positive")
    if policy == "multiply":
        return prod(values)
    if policy == "highest":
        return max([1.0, *values])
    if policy == "additive_bonuses":
        return 1.0 + sum(v - 1.0 for v in values)
    raise ValueError("Unknown stacking policy")

def apply_damage(base_damage, groups):
    if base_damage < 0:
        raise ValueError("Negative damage")
    result = base_damage
    for group in groups:
        result *= combine_multipliers(group["multipliers"], group["policy"])
    return result
