"""Necessary armor-slot budget checks; not proof of item/slot availability.

Destiny guardians have five equipped armor slots. An Exotic occupies one.
Set bonus thresholds count distinct pieces, never a repeated bonus on one item.
"""
from collections.abc import Mapping


def check_armor_set_budget(set_piece_counts: Mapping[str, int], exotic_count: int = 1):
    if not isinstance(exotic_count, int) or isinstance(exotic_count, bool) or not 0 <= exotic_count <= 1:
        raise ValueError("Exotic armor count must be 0 or 1")
    if not isinstance(set_piece_counts, Mapping):
        raise ValueError("Set counts must be a mapping")
    for name, count in set_piece_counts.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Set name must be non-empty")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("Set counts must be nonnegative integers")
    used = exotic_count + sum(set_piece_counts.values())
    return {"fits_five_armor_slots": used <= 5, "used_slots": used,
            "remaining_slots": max(0, 5 - used),
            "necessary_not_sufficient": "Armor-slot distribution, obtainable pieces, and class-specific legality remain unverified"}
