"""Official June 9 2026 Cascade Point cross-weapon precision priming thresholds.

Bungie Update 9.7.0: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
This only screens the minimum hit COUNT from another weapon. It cannot
establish the rapid-hit timing window, target weapon perk/socket legality,
enhanced behavior, activity applicability, or actual damage/TTK.
"""

# Source-weapon families, not the Cascade Point weapon's frame.
HITS_BY_SOURCE = {
    "auto rifle": 6, "pulse rifle": 6, "smg": 6,
    "trace rifle": 6, "sidearm": 6, "lmg": 6,
    "hand cannon": 4, "scout rifle": 4,
    "bow": 2, "lfr": 2, "glaive projectile": 2,
    "shotgun": 2, "sniper rifle": 2,
}


def screen_cascade_point_priming(source_weapon_type, precision_hits, *,
                                 other_weapon=True):
    """Count-only screen; never returns a certified perk activation."""
    if not isinstance(source_weapon_type, str):
        raise TypeError("source_weapon_type must be a string")
    if type(precision_hits) is not int or precision_hits < 0:
        raise ValueError("precision_hits must be a nonnegative integer")
    if type(other_weapon) is not bool:
        raise TypeError("other_weapon must be boolean")
    family = " ".join(source_weapon_type.strip().casefold().split())
    threshold = HITS_BY_SOURCE.get(family)
    if threshold is None:
        return {"status": "unknown_source_family", "minimum_hits": None,
                "count_threshold_met": False, "certified_activation": False}
    if not other_weapon:
        return {"status": "requires_other_weapon", "minimum_hits": threshold,
                "count_threshold_met": False, "certified_activation": False}
    return {"status": "count_only_not_timing_verified",
            "minimum_hits": threshold,
            "count_threshold_met": precision_hits >= threshold,
            "certified_activation": False}
