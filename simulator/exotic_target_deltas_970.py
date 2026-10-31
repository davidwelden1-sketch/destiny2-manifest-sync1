"""Historical 9.7.0 Exotic target-class deltas keyed to exact weapon hashes.

Bungie official patch: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published 2026-06-09. Item-hash identity is independently catalogued by
light.gg (community manifest display), not asserted by the Bungie patch text.

These are relative changes against matching PRE-9.7.0 PvE damage, not
measured current damage, DPS, a legal perk combination, or a build ranking.
No cross-weapon-family multiplier composition is performed here.
"""

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = "2026-06-09"
TARGETS = frozenset({"base_combatant", "elite", "champion", "boss"})
ACTIVITIES = frozenset({"pve", "pvp", "competitive", "trials"})
BASELINES = frozenset({"pre_9_7_0", "post_9_7_0", "unknown"})

# The source patch lists damage deltas by Exotic NAME, not by hash.
# The hash links are separately sourced and may need revalidation if revised.
EXOTICS = {
    4036115577: {
        "name": "Sleeper Simulant",
        "item_hash_source": "https://www.light.gg/db/items/4036115577/sleeper-simulant/",
        "patch_relative_factors": {"boss": 1.10, "champion": 1.10},
    },
    2130065553: {
        "name": "Arbalest",
        "item_hash_source": "https://www.light.gg/db/items/2130065553/arbalest/",
        "patch_relative_factors": {"champion": 1.33},
    },
}


def historical_exotic_target_delta(*, item_hash, target, activity,
                                   source_patch_version, reference_baseline):
    """Return a historical scalar only when exact hash, PvE and baseline qualify.

    A factor of 1.0 on an otherwise eligible unlisted target means the
    9.7.0 note did not list a change for that weapon/target. It does NOT
    certify that damage is unchanged by other patches, buffs or debuffs.
    """
    if type(item_hash) is not int or item_hash <= 0:
        raise ValueError("item_hash must be a positive integer (not bool)")
    for name, value in (("target", target), ("activity", activity),
                        ("source_patch_version", source_patch_version),
                        ("reference_baseline", reference_baseline)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a nonempty string")
    target = target.strip().casefold()
    activity = activity.strip().casefold()
    reference_baseline = reference_baseline.strip().casefold()
    if target not in TARGETS:
        raise ValueError("target must be a supported PvE combatant class")
    if activity not in ACTIVITIES:
        raise ValueError("unknown activity")
    if reference_baseline not in BASELINES:
        raise ValueError("unknown reference baseline")

    item = EXOTICS.get(item_hash)
    base = {
        "item_hash": item_hash,
        "weapon": item["name"] if item else None,
        "item_hash_source": item["item_hash_source"] if item else None,
        "hash_evidence_grade": "community_manifest_catalog" if item else None,
        "target": target,
        "activity": activity,
        "reference_baseline": reference_baseline,
        "source_patch_version": PATCH_VERSION,
        "source_url": SOURCE_URL,
        "published_on": PATCH_DATE,
        "evidence_grade": "official_historical_named_exotic_patch",
        "relative_multiplier": None,
        "absolute_damage": None,
        "boss_dps": None,
        "guardian_ttk": None,
        "gameplay_measured": False,
        "current_game_verified": False,
        "current_roll_certified": False,
        "artifact_selection_verified": False,
    }
    if item is None:
        return {**base, "status": "unknown_exact_weapon_hash"}
    if activity != "pve":
        return {**base, "status": "pvp_not_applicable"}
    if source_patch_version.strip() != PATCH_VERSION:
        return {**base, "status": "source_patch_version_mismatch"}
    if reference_baseline != "pre_9_7_0":
        return {**base, "status": "not_a_pre_patch_reference"}
    factor = item["patch_relative_factors"].get(target)
    if factor is None:
        return {**base, "status": "no_listed_target_change", "relative_multiplier": 1.0}
    return {**base, "status": "historical_patch_delta_only",
            "relative_multiplier": factor,
            "interpretation": "Patch-relative PvE delta from a matched pre-9.7.0 baseline only; not current measured DPS or PvP damage."}
