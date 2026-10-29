"""Conservative activity-specific legality rules from official Bungie notes.

These rules are historical published settings, not a live playlist/Artifact
rotation check or proof that a specific weapon or roll is obtainable.
Source: https://www.bungie.net/7/en/News/Article/twid_05_29_2026
Published: 2026-05-29; reviewed: 2026-10-29.
"""
SOURCE = "https://www.bungie.net/7/en/News/Article/twid_05_29_2026"
SOURCE_DATE = "2026-05-29"
REVIEWED_DATE = "2026-10-29"


def activity_constraints(activity):
    """Return known historical constraints; unknown activities fail closed."""
    if not isinstance(activity, str) or not activity.strip():
        raise ValueError("activity must be a nonempty string")
    name = " ".join(activity.casefold().strip().split())
    base = {
        "source_url": SOURCE, "source_date": SOURCE_DATE,
        "reviewed_date": REVIEWED_DATE, "current_playlist_verified": False,
        "gameplay_verified": False, "special_weapons_allowed": None,
        "supers_allowed": None, "powered_melees_allowed": None,
        "passive_grenade_recharge": None, "passive_class_ability_recharge": None,
        "artifact_enabled": None, "primary_damage_multiplier": None,
        "heavy_damage_multiplier": None, "airborne_effectiveness_bonus": None,
    }
    if name in {"arena collision", "crucible arena collision"}:
        return {**base, "status": "official_historical_arena_collision",
                "special_weapons_allowed": False, "supers_allowed": False,
                "powered_melees_allowed": False,
                "passive_grenade_recharge": False,
                "passive_class_ability_recharge": False,
                "primary_damage_multiplier": 1.0,
                "heavy_damage_multiplier": None,
                "heavy_damage_note": "decreased; numerical scalar not stated",
                "airborne_effectiveness_bonus": 60,
                "grenade_class_recharge_note": "final blows refund energy; exact amount depends on cooldown/stat"}
    if name in {"trials", "trials of osiris", "competitive", "competitive crucible"}:
        return {**base, "status": "official_historical_artifact_disabled",
                "artifact_enabled": False}
    return {**base, "status": "mode_specific_review_required"}


def candidate_conflicts(activity, *, special=False, super_required=False,
                        powered_melee=False, passive_ability_regen=False,
                        artifact_required=False):
    """Only report explicit contradictions; unknowns are review blockers."""
    for value in (special, super_required, powered_melee,
                  passive_ability_regen, artifact_required):
        if type(value) is not bool:
            raise ValueError("candidate flags must be booleans")
    rules = activity_constraints(activity)
    conflicts = []
    if special and rules["special_weapons_allowed"] is False:
        conflicts.append("special_weapon_disabled")
    if super_required and rules["supers_allowed"] is False:
        conflicts.append("super_disabled")
    if powered_melee and rules["powered_melees_allowed"] is False:
        conflicts.append("powered_melee_disabled")
    if passive_ability_regen and (rules["passive_grenade_recharge"] is False
                                  or rules["passive_class_ability_recharge"] is False):
        conflicts.append("passive_ability_recharge_disabled")
    if artifact_required and rules["artifact_enabled"] is False:
        conflicts.append("artifact_disabled")
    return {"activity": activity, "conflicts": conflicts,
            "legal_certified": False, "current_review_required": True,
            "source_url": rules["source_url"]}
