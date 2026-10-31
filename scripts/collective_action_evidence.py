"""Patch-sourced Collective Action coefficients; NOT measured gameplay or a build certifier.

Bungie Update 9.7.0, 2026-06-09:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
All values below are *published* per-perk parameters, not an independently
measured damage, PvP TTK, uptime, stack category, or obtainable weapon roll.
"""
from decimal import Decimal

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH = "9.7.0"
PUBLISHED_DATE = "2026-06-09"
MAX_DURATION_SECONDS = Decimal("16")
# Each key is one documented event, NOT a claim that two events can double-proc.
EVENT_SECONDS = {
    "firesprite": Decimal("8"),
    "void_breach": Decimal("8"),
    "ionic_trace": Decimal("4"),
    "stasis_shard": Decimal("4"),
    "tangle_detonation": Decimal("4"),
    "tangle_throw": Decimal("4"),
}
BONUS = {
    "pve": {"standard": Decimal("0.30"), "enhanced": Decimal("0.33")},
    "pvp": {"standard": Decimal("0.10"), "enhanced": Decimal("0.11")},
}


def published_bonus(mode, enhanced=False):
    """Return a sourced per-hit multiplier; do not combine with other buffs."""
    if mode not in BONUS:
        raise ValueError("mode must be pve or pvp")
    if type(enhanced) is not bool:
        raise TypeError("enhanced must be boolean")
    return Decimal("1") + BONUS[mode]["enhanced" if enhanced else "standard"]


def duration_upper_bound(events):
    """Add listed event grants to a 16s cap; a THEORETICAL upper bound only.

    This is NOT an in-game timer prediction: simultaneous events, activation
    ownership, refresh rules, and cooldowns require independent measurement.
    Artifact elemental orbs deliberately excluded because per-orb duration
    has not been independently established here.
    """
    if not isinstance(events, (tuple, list)):
        raise TypeError("events must be a sequence")
    total = Decimal("0")
    for event in events:
        if event not in EVENT_SECONDS:
            raise ValueError("unknown event; no guessed artifact-orb grant")
        total = min(MAX_DURATION_SECONDS, total + EVENT_SECONDS[event])
    return total


def published_single_hit(base_damage, mode, enhanced=False):
    """Pure arithmetic scenario, not measured damage, TTK or stack validation."""
    if isinstance(base_damage, bool):
        raise TypeError("damage must be a nonnegative finite number")
    try:
        value = Decimal(str(base_damage))
    except Exception as exc:
        raise TypeError("damage must be numeric") from exc
    if not value.is_finite() or value < 0:
        raise ValueError("damage must be finite and nonnegative")
    return value * published_bonus(mode, enhanced)
