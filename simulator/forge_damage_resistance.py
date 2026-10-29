"""Deterministic DR calculations. Does not assert live stacking compatibility."""
from math import prod

def combined_dr(*fractions):
    if not fractions or any(type(x) not in (int, float) or not 0 <= x < 1 for x in fractions):
        raise ValueError("DR inputs must be fractions in [0, 1)")
    return 1 - prod(1 - x for x in fractions)

def damage_taken(raw_damage, *fractions):
    if raw_damage < 0:
        raise ValueError("damage must be nonnegative")
    return raw_damage * (1 - combined_dr(*fractions))

GIFTED_CONVICTION_PVE_REPORTED = {0:0.0, 1:0.25, 2:0.40, 3:0.50}
GIFTED_CONVICTION_PVP_REPORTED = {0:0.0, 1:0.05, 2:0.075, 3:0.10}

def gifted_conviction_reported(stacks, mode="pve"):
    table = GIFTED_CONVICTION_PVE_REPORTED if mode == "pve" else GIFTED_CONVICTION_PVP_REPORTED if mode == "pvp" else None
    if table is None or stacks not in table:
        raise ValueError("invalid mode or stack count")
    return table[stacks]
