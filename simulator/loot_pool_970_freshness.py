"""Conservative 9.7.0 game-wide raid/dungeon loot-pool freshness gate.

Bungie Update 9.7.0 (2026-06-09) refreshed rewards for pre-Edge of Fate
raids/dungeons. A historical pool or origin trait is not evidence of a
current legal perk pair, enhanced roll, acquisition, or playable build.
"""
from datetime import date

from simulator.activity_rules import activity_constraints

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
REVIEWED_DATE = "2026-10-31"
PATCH_DATE = date.fromisoformat(SOURCE_DATE)
SOURCE_KINDS = frozenset({"raid", "dungeon", "destination", "other"})
ACTIVITIES = frozenset({"pve", "pvp", "trials", "competitive"})


def audit_loot_pool_freshness(*, item_hash, source_kind, pre_edge_of_fate,
                              craftable, observation_date, activity="pve",
                              observed_manifest_version=None,
                              reference_manifest_version=None):
    """Audit source-level patch freshness without inventing item-level legality."""
    if item_hash is not None and (type(item_hash) is not int or item_hash <= 0):
        raise ValueError("item_hash must be a positive integer or None")
    if not isinstance(source_kind, str) or source_kind not in SOURCE_KINDS:
        raise ValueError("source_kind must be raid/dungeon/destination/other")
    if pre_edge_of_fate is not None and type(pre_edge_of_fate) is not bool:
        raise ValueError("pre_edge_of_fate must be bool or None")
    if craftable is not None and type(craftable) is not bool:
        raise ValueError("craftable must be bool or None")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be ISO date")
    try:
        observed_at = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("observation_date must be ISO date") from exc
    if observed_at.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    if activity not in ACTIVITIES:
        raise ValueError("activity must be pve/pvp/trials/competitive")
    for value in (observed_manifest_version, reference_manifest_version):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("manifest versions must be nonempty strings or None")

    before_patch = observed_at < PATCH_DATE
    affected_raid = source_kind == "raid" and pre_edge_of_fate is True
    affected_dungeon = source_kind == "dungeon" and pre_edge_of_fate is True
    # Bungie explicitly distinguishes updated CRAFTABLE RAID perk pools from
    # tiered DUNGEON weapons with new origin traits.
    raid_craftable_pool = affected_raid and craftable is True
    flags = []
    if affected_raid:
        flags.append("raid_tiered_rewards")
        if raid_craftable_pool:
            flags.extend(("craftable_raid_perk_pool_updated",
                          "craftable_raid_tier_upgrade_supported"))
    if affected_dungeon:
        flags.extend(("dungeon_tiered_weapon_rewards",
                      "dungeon_new_origin_traits"))

    if observed_manifest_version is None or reference_manifest_version is None:
        version_state = "version_comparison_unavailable"
    elif observed_manifest_version != reference_manifest_version:
        version_state = "version_mismatch_revalidate"
    else:
        version_state = "versions_match_not_roll_certification"

    return {
        "item_hash": item_hash,
        "source_kind": source_kind,
        "pre_edge_of_fate": pre_edge_of_fate,
        "craftable": craftable,
        "observation_date": observation_date,
        "activity": activity,
        "artifact_enabled": activity_constraints(activity)["artifact_enabled"],
        "official_source_level_changes": flags,
        "perk_pool_revalidation_required": before_patch and raid_craftable_pool,
        "origin_trait_revalidation_required": before_patch and affected_dungeon,
        "tiered_reward_revalidation_required": before_patch and
            (affected_raid or affected_dungeon),
        "manifest_version_status": version_state,
        "current_exact_perk_pair_verified": False,
        "enhanced_perk_legality_verified": False,
        "current_acquisition_verified": False,
        "current_artifact_selection_verified": False,
        "pve_boss_dps": None,
        "pvp_ttk": None,
        "pve_damage_resistance": None,
        "gameplay_measured": False,
        "evidence_grade": "official_historical_source_level_patch_only",
        "source_url": SOURCE_URL,
        "source_date": SOURCE_DATE,
        "reviewed_date": REVIEWED_DATE,
    }
