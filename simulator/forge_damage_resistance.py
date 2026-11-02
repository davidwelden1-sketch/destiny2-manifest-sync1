"""Deterministic PvE/PvP DR arithmetic; does not certify live stacking compatibility.

Callers must supply separately sourced DR fractions and a stacking rule.
This helper's multiplicative combination is a hypothetical independent-source
model, not proof that two Destiny effects actually stack.
"""
from math import isfinite, prod


def _valid_fraction(value):
    return type(value) in (int, float) and isfinite(value) and 0 <= value < 1


def combined_dr(*fractions):
    if not fractions or any(not _valid_fraction(x) for x in fractions):
        raise ValueError("DR inputs must be finite fractions in [0, 1), not booleans")
    return 1 - prod(1 - x for x in fractions)


def damage_taken(raw_damage, *fractions):
    if type(raw_damage) not in (int, float) or not isfinite(raw_damage) or raw_damage < 0:
        raise ValueError("raw damage must be finite and nonnegative")
    result = raw_damage * (1 - combined_dr(*fractions))
    if not isfinite(result):
        raise ValueError("calculated damage is nonfinite")
    return result


GIFTED_CONVICTION_PVE_REPORTED = {0: 0.0, 1: 0.25, 2: 0.40, 3: 0.50}
GIFTED_CONVICTION_PVP_REPORTED = {0: 0.0, 1: 0.05, 2: 0.075, 3: 0.10}


def gifted_conviction_reported(stacks, mode="pve"):
    table = (GIFTED_CONVICTION_PVE_REPORTED if mode == "pve" else
             GIFTED_CONVICTION_PVP_REPORTED if mode == "pvp" else None)
    if type(stacks) is not int or table is None or stacks not in table:
        raise ValueError("invalid mode or stack count")
    return table[stacks]
