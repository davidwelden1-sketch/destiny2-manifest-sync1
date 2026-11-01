"""Source-gated ammo economy evidence from Bungie Update 9.7.0 (2026-06-09).

Official source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
This records historical rules, not gameplay-tested ammo, exact item-hash rolls,
kill attribution, damage, TTK, or current Artifact certification.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
ACTIVITIES = frozenset({"pve", "pvp", "competitive", "trials"})
# Historical (old, post-9.7.0) values for precision linear fusion rifles.
PVE_PRECISION_LFR_BRICKS = {
    ("heavy", "base"): (3, 5),
    ("heavy", "enhanced"): (4, 6),
    ("special", "base"): (3, 5),
    ("special", "enhanced"): (6, 10),
}


def _status(observation_date, activity, source_patch_version):
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be YYYY-MM-DD")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    if activity not in ACTIVITIES:
        raise ValueError("unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    if source_patch_version != PATCH_VERSION:
        return "source_patch_version_mismatch"
    if day < PATCH_DATE:
        return "pre_patch_observation_requires_revalidation"
    if day == PATCH_DATE:
        return "patch_day_deployment_time_unknown"
    return None


def _base(activity):
    return {
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "activity": activity,
        "artifact_enabled": False if activity in {"competitive", "trials"} else None,
        "evidence_grade": "official_historical_patch_rule_not_gameplay_measurement",
        "gameplay_measured": False,
        "current_manifest_item_verified": False,
        "current_artifact_selection_verified": False,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "ammo_meter_rate": None,
        "weapon_kill_attribution": None,
    }


def audit_pit_brick(*, observation_date, activity, enemy_floating_above_pit,
                    meter_threshold_reached, owed_brick_before=False,
                    source_patch_version=PATCH_VERSION):
    """Screen documented brick deferral; do not simulate unknown meter values.

    The patch says an above-pit kill cannot drop its brick even if the ammo
    meter fills; progress continues and a later eligible kill spawns the owed
    brick. It does not specify multiple owed bricks or simultaneous payouts.
    """
    freshness = _status(observation_date, activity, source_patch_version)
    for name, value in (("enemy_floating_above_pit", enemy_floating_above_pit),
                        ("meter_threshold_reached", meter_threshold_reached),
                        ("owed_brick_before", owed_brick_before)):
        if type(value) is not bool:
            raise ValueError(name + " must be boolean")
    status = freshness
    if status is None:
        if enemy_floating_above_pit:
            status = ("brick_deferred_until_eligible_kill" if meter_threshold_reached
                      else "ammo_meter_progress_not_lost")
        elif owed_brick_before and meter_threshold_reached:
            status = "simultaneous_owed_and_new_threshold_payout_unresolved"
        elif owed_brick_before:
            status = "owed_brick_spawns_on_eligible_kill"
        elif meter_threshold_reached:
            status = "ordinary_brick_drop_not_certified_by_this_note"
        else:
            status = "no_specific_drop_inferred"
    return {
        **_base(activity),
        "status": status,
        "above_pit": enemy_floating_above_pit,
        "threshold_reached_supplied_not_measured": meter_threshold_reached,
        "owed_brick_before_supplied_not_measured": owed_brick_before,
        "pit_kill_drops_brick": False if freshness is None and enemy_floating_above_pit else None,
        "owed_brick_spawn_rule_applies": status == "owed_brick_spawns_on_eligible_kill",
        "number_of_bricks_spawned": None,
        "pvp_guardian_drop_behavior_measured": False,
    }


def audit_precision_lfr_brick(*, observation_date, activity, ammo_class,
                              brick_type, source_patch_version=PATCH_VERSION):
    """Report only Bungie's PvE precision-LFR per-brick amounts, not DPS."""
    freshness = _status(observation_date, activity, source_patch_version)
    if ammo_class not in {"heavy", "special"}:
        raise ValueError("ammo_class must be heavy or special")
    if brick_type not in {"base", "enhanced"}:
        raise ValueError("brick_type must be base or enhanced")
    status = freshness
    if status is None:
        status = ("official_pve_precision_lfr_ammo_per_brick_only"
                  if activity == "pve" else "pvp_ammo_amount_not_established")
    old, new = PVE_PRECISION_LFR_BRICKS[(ammo_class, brick_type)]
    applicable = status == "official_pve_precision_lfr_ammo_per_brick_only"
    return {
        **_base(activity),
        "status": status,
        "ammo_class": ammo_class,
        "brick_type": brick_type,
        "previous_pve_ammo_per_brick": old if applicable else None,
        "post_patch_pve_ammo_per_brick": new if applicable else None,
        "exact_weapon_hash_eligibility_verified": False,
        "enhanced_perk_eligibility_verified": False,
        "ammo_pickup_uptime_measured": False,
    }
