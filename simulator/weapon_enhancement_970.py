"""Conservative 9.7.0 weapon-tier vs enhanced-mod vs enhanced-perk evidence.

Bungie 2026-06-09 Update 9.7.0 states that enhanced weapon mods unlock at
Gear Tier 3, and that crafted weapons and reshape-capable raid Adepts can
reach Gear Tier 5. Only an Enhanced Intrinsic can enable the additive stat
boost associated with gear tier. None of those rules proves an enhanced
TRAIT is in a particular weapon's legal roll pool.

Historical source, not current item acquisition, gameplay, or perk certification.
"""

SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
REVIEWED_DATE = "2026-10-31"
CATEGORIES = {"crafted", "reshape_capable_raid_adept", "other", "unknown"}


def classify_enhancement_evidence(*, item_hash, gear_tier, category,
                                  enhanced_intrinsic=None,
                                  enhanced_mod_compatible=None,
                                  activity="pve"):
    """Classify three distinct enhancement concepts, without certifying rolls.

    gear_tier=None means the instance's tier is unknown; a number is a
    caller-supplied observation, not authenticated live-inventory evidence.
    """
    if type(item_hash) is not int or item_hash <= 0:
        raise ValueError("item_hash must be a positive integer")
    if gear_tier is not None and (type(gear_tier) is not int or not 1 <= gear_tier <= 5):
        raise ValueError("gear_tier must be 1..5 or None")
    if category not in CATEGORIES:
        raise ValueError("unknown weapon category")
    if enhanced_intrinsic is not None and type(enhanced_intrinsic) is not bool:
        raise ValueError("enhanced_intrinsic must be bool or None")
    if enhanced_mod_compatible is not None and type(enhanced_mod_compatible) is not bool:
        raise ValueError("enhanced_mod_compatible must be bool or None")
    if activity not in {"pve", "pvp", "competitive", "trials"}:
        raise ValueError("unknown activity")

    mod_tier_requirement_met = None if gear_tier is None else gear_tier >= 3
    if mod_tier_requirement_met is False or enhanced_mod_compatible is False:
        enhanced_mod_use_established = False
    elif mod_tier_requirement_met is True and enhanced_mod_compatible is True:
        enhanced_mod_use_established = True
    else:
        enhanced_mod_use_established = None

    if enhanced_intrinsic is False:
        stat_bonus_prerequisite_met = False
    elif enhanced_intrinsic is True:
        stat_bonus_prerequisite_met = True
    else:
        stat_bonus_prerequisite_met = None

    return {
        "item_hash": item_hash,
        "gear_tier_observation": gear_tier,
        "category": category,
        "tier_five_upgrade_category_documented": category in {"crafted", "reshape_capable_raid_adept"},
        "enhanced_weapon_mod_tier_requirement_met": mod_tier_requirement_met,
        "enhanced_weapon_mod_use_established_from_supplied_inputs": enhanced_mod_use_established,
        "enhanced_intrinsic_stat_bonus_prerequisite_met": stat_bonus_prerequisite_met,
        "additive_stat_bonus_amount": None,
        "enhanced_trait_perk_legality": "not_established_by_tier_or_mod",
        "enhanced_trait_socket_hashes": None,
        "current_obtainability_certified": False,
        "current_roll_certified": False,
        "live_instance_verified": False,
        "pve_damage_measured": False,
        "pvp_ttk_measured": False,
        "activity": activity,
        "artifact_enabled": False if activity in {"competitive", "trials"} else None,
        "source_url": SOURCE,
        "source_date": SOURCE_DATE,
        "reviewed_date": REVIEWED_DATE,
        "evidence_grade": "official_historical_patch_rule_with_unverified_instance_inputs",
    }
