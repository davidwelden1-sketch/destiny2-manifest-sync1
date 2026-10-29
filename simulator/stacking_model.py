"""Deterministic combat stacking with explicit rules; never silently multiply unknown buffs."""
from math import isfinite

def calculate_damage(base_damage, modifiers):
    """Modifiers are explicit dicts with group, multiplier and stacking rule.

    'exclusive_max' selects the highest multiplier per group; 'multiplicative'
    combines independent groups. This is a hypothetical calculator, not
    evidence that Destiny applies these rules to any particular buffs.
    """
    if not isfinite(base_damage) or base_damage < 0:
        raise ValueError("invalid base damage")
    groups = {}
    for mod in modifiers:
        group = mod["group"]
        multiplier = mod["multiplier"]
        if not isinstance(group, str) or not group:
            raise ValueError("invalid group")
        if not isfinite(multiplier) or multiplier < 0:
            raise ValueError("invalid multiplier")
        if mod.get("rule") != "exclusive_max":
            raise ValueError("unknown stacking rule")
        groups[group] = max(groups[group], multiplier) if group in groups else multiplier
    total = base_damage
    for multiplier in groups.values():
        total *= multiplier
    return {"damage": total, "model_only": True, "groups": groups}
