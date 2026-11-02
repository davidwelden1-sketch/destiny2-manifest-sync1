"""Source-scoped 9.7.0 grapple-melee boss stat stacking evidence.

Bungie, 2026-06-09: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Boss-only change: maximum Grenade-stat bonus reduced by 50%; Grenade
and Melee stat damage bonuses now add instead of multiply.
No current exact stat curve, in-game DPS, or Guardian TTK is certified.
"""
from datetime import date
from math import isfinite

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = date(2026, 6, 9)
PATCH_VERSION = "9.7.0"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
TARGETS = frozenset(("boss", "nonboss_combatant", "guardian"))
EVENTS = frozenset(("grapple_melee", "weapon_final_blow", "other_melee"))


def assess_grapple_boss_scaling(*, observation_date, guardian_class, activity,
                                target_rank, event_kind, manifest_version=None,
                                artifact_name=None, artifact_perks=()):
    if guardian_class not in CLASSES or activity not in ACTIVITIES:
        raise ValueError("Unknown class or activity")
    if target_rank not in TARGETS or event_kind not in EVENTS:
        raise ValueError("Unknown target or event")
    if type(observation_date) is not str:
        raise ValueError("Canonical date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Canonical date required")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven selected Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require one named Artifact")

    post_patch = day > PATCH_DATE
    patch_day = day == PATCH_DATE
    boss_event = (activity == "pve" and target_rank == "boss"
                  and event_kind == "grapple_melee")
    supported = post_patch and boss_event
    if patch_day:
        status = "patch_day_deployment_time_unknown"
    elif day < PATCH_DATE:
        status = "pre_patch"
    elif not boss_event:
        status = "boss_only_pve_grapple_melee_rule_not_applicable"
    else:
        status = "official_historical_boss_stat_stacking_change"
    return {
        "id": "d2:patch-rule:970:grapple-melee:boss-stat-bonus",
        "status": status,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_checked_at": "2026-11-02",
        "patch_version": PATCH_VERSION,
        "observation_date": observation_date,
        "manifest_version": manifest_version,
        "guardian_class": guardian_class,
        "activity": activity,
        "target_rank": target_rank,
        "event_kind": event_kind,
        "official_historical_rule_applicable": supported,
        "prepatch_grenade_and_melee_stat_bonuses": "multiplicative" if supported else None,
        "postpatch_grenade_and_melee_stat_bonuses": "additive" if supported else None,
        "maximum_grenade_stat_bonus_relative_reduction": 0.5 if supported else None,
        "evidence_grade": "official_historical_patch_not_gameplay_measured",
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_weapon_perk_armor_legality_verified": False,
        "measured_pve_boss_dps": None,
        "measured_pvp_guardian_ttk": None,
        "measured_damage_resistance": None,
        "measured_cooldown": None,
        "current_runtime_verified": False,
    }


def illustrative_max_stat_bonus_math(*, prepatch_grenade_bonus_fraction,
                                     melee_bonus_fraction):
    """Hypothetical only, at maximum Grenade stat, using supplied bonus fractions.

    Assumes conventional damage multiplier = 1 + bonus. This is a math
    comparison, NOT a measured or certified Destiny damage multiplier.
    """
    for x in (prepatch_grenade_bonus_fraction, melee_bonus_fraction):
        if type(x) not in (int, float) or not isfinite(x) or x < 0:
            raise ValueError("Supply finite nonnegative numeric bonus fractions")
    g = prepatch_grenade_bonus_fraction
    m = melee_bonus_fraction
    old = (1.0 + g) * (1.0 + m)
    new = 1.0 + 0.5 * g + m
    return {
        "hypothetical_only": True,
        "assumes_max_grenade_stat": True,
        "assumes_standard_bonus_fraction_semantics": True,
        "prepatch_multiplier_illustrative": old,
        "postpatch_multiplier_illustrative": new,
        "relative_multiplier_change_illustrative": new / old - 1.0,
        "measured_pve_dps": None,
        "measured_pvp_ttk": None,
    }
