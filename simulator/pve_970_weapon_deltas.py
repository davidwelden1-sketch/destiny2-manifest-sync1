"""Historical Bungie 9.7.0 PvE weapon-family damage deltas, not absolute damage.

Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published 2026-06-09. These are patch-note changes against the PRE-9.7.0
baseline, not multipliers to apply blindly to a current post-patch measurement.
No manifest item hash, roll, current activity tuning, or gameplay measurement is
certified here. PvP is deliberately excluded.
"""
from math import prod

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
FAMILIES = frozenset(("rocket_pulse", "rocket_launcher", "heavy_grenade_launcher"))
TARGETS = frozenset(("base_combatant", "elite", "champion", "boss"))


def historical_pve_delta(family, target, *, activity, source_patch_version):
    """Return a sourced historical ratio ONLY for the specified patch.

    Rocket Pulse boss change is explicitly *on top of* its generic PvE -10%,
    hence 0.90 * 0.75 = 0.675. This is a relative patch delta, not boss DPS.
    For launchers and heavy drum GLs, the published +5% applies only against
    bosses and Champions. An unlisted target returns a 1.0 delta, not a claim
    that the weapon has no other damage bonuses.
    """
    for name, value in (("family", family), ("target", target),
                        ("activity", activity), ("source_patch_version", source_patch_version)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a nonempty string")
    family, target, activity = (family.strip().casefold(),
                                target.strip().casefold(), activity.strip().casefold())
    base = {"family": family, "target": target, "activity": activity,
            "source_patch_version": PATCH_VERSION, "source_url": SOURCE_URL,
            "published_on": "2026-06-09", "evidence_grade": "official_historical_patch",
            "gameplay_measured": False, "current_game_verified": False,
            "absolute_damage": None, "boss_dps": None, "multiplier": None,
            "components": []}
    if activity not in ("pve", "pvp"):
        raise ValueError("activity must be explicitly pve or pvp")
    if target not in TARGETS:
        raise ValueError("unknown combatant class")
    if family not in FAMILIES:
        return {**base, "status": "unsupported_weapon_family"}
    if activity == "pvp":
        return {**base, "status": "pvp_not_applicable"}
    if source_patch_version.strip() != PATCH_VERSION:
        return {**base, "status": "source_patch_version_mismatch"}
    factors = []
    if family == "rocket_pulse":
        factors.append(("all_pve_targets", 0.90))
        if target == "boss":
            factors.append(("additional_boss_scalar", 0.75))
    elif family in ("rocket_launcher", "heavy_grenade_launcher"):
        if target in ("boss", "champion"):
            factors.append(("boss_and_champion_scalar", 1.05))
    return {**base, "status": "historical_patch_delta_only",
            "components": [{"scope": scope, "factor": factor}
                           for scope, factor in factors],
            "multiplier": prod(factor for _, factor in factors),
            "interpretation": ("Relative change from the pre-9.7.0 PvE baseline only. "
                               "Do not apply to already post-patch damage observations, "
                               "PvP, or a weapon without independently verified family metadata.")}

