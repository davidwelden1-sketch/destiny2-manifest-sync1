"""Historical Bungie 9.7.0 Anti-Champion 2.0 frame routing.

Not a current manifest item-hash legality oracle or PvP damage model.
Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
"""
PATCH_VERSION = "9.7.0"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
BASE_FRAMES = {
    "aggressive": "unstoppable",
    "high_impact": "unstoppable",
    "precision": "barrier",
    "adaptive": "barrier",
    "lightweight": "overload",
    "rapid_fire": "overload",
}
FRAME_OVERRIDES = {
    ("auto_rifle", "support"): "overload",
    ("linear_fusion_rifle", "adaptive_burst"): "barrier",
    ("breech_grenade_launcher", "area_denial"): "overload",
    ("breech_grenade_launcher", "double_fire"): "unstoppable",
    ("breech_grenade_launcher", "micro_missile"): "unstoppable",
    ("breech_grenade_launcher", "wave"): "unstoppable",
}
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def review_champion_frame(*, frame, activity, weapon_type=None,
                          item_hash=None, manifest_frame_verified=False):
    """Classify historical PvE Champion routing; fail closed on unknown frames.

    Supplying an item hash or an external verification claim does not certify
    manifest eligibility, obtainable sockets, current Artifact or damage.
    """
    if type(frame) is not str or not frame:
        raise ValueError("Canonical frame required")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Explicit supported activity required")
    if weapon_type is not None and (type(weapon_type) is not str or not weapon_type):
        raise ValueError("Invalid weapon type")
    if item_hash is not None and (type(item_hash) is not int or not 0 < item_hash < 2**32):
        raise ValueError("Invalid unsigned 32-bit item hash")
    if type(manifest_frame_verified) is not bool:
        raise ValueError("Verification flag must be boolean")
    override = (weapon_type, frame)
    if override in FRAME_OVERRIDES:
        counter = FRAME_OVERRIDES[override]
        rule = "specific_frame_override"
    elif frame in BASE_FRAMES:
        counter = BASE_FRAMES[frame]
        rule = "generic_frame_category"
    elif any(k[1] == frame for k in FRAME_OVERRIDES):
        raise ValueError("Specific frame requires matching weapon type")
    else:
        raise ValueError("Frame not in sourced 9.7.0 rule table")

    return {
        "rule_id": "d2:patch-rule:970:champion:" + (
            "override:" + weapon_type + ":" + frame if rule == "specific_frame_override"
            else "base:" + frame),
        "source_url": SOURCE_URL, "patch_version": PATCH_VERSION,
        "reviewed_at": "2026-11-02", "evidence": "official_historical",
        "activity": activity, "frame": frame, "weapon_type": weapon_type,
        "champion_counter_pve": counter if activity == "pve" else None,
        "rule": rule, "item_hash_supplied": item_hash is not None,
        "manifest_frame_verified_claimed": manifest_frame_verified,
        "current_item_hash_legality_certified": False,
        "current_artifact_allocation_certified": False,
        "enhanced_perk_eligibility_certified": False,
        "pve_dps_measured": None, "pvp_ttk_measured": None,
        "pve_dr_measured": None, "ability_cooldown_measured": None,
        "pvp_guardian_damage_inferred": False,
        "certified_for_live_build": False,
    }
