"""Official 9.7.0 Centrifuse and Titan Unbreakable research leads.

Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published 2026-06-09. Source is historical patch evidence, NOT a measured
weapon proc, obtainable item-hash/roll, current Artifact or certified build.

Centrifuse: magazine refill per trigger increased from 4% to 10%.
The note does not identify the trigger's cause or its event attribution.
Titan Unbreakable: final blows with the aspect's blast now grant Devour.
The note does not specify Devour duration or Guardian-specific reliability.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = "2026-06-09"
PATCH_VERSION = "9.7.0"
ACTIVITIES = frozenset({"pve", "pvp", "competitive", "trials"})
CLASSES = frozenset({"hunter", "titan", "warlock"})


def _day(value):
    if not isinstance(value, str):
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    try:
        day = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != value:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    return day


def _inputs(observation_date, activity, source_patch_version):
    observed = _day(observation_date)
    if activity not in ACTIVITIES:
        raise ValueError("unknown activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    if source_patch_version != PATCH_VERSION:
        return observed, "source_patch_version_mismatch"
    if observed < date.fromisoformat(PATCH_DATE):
        return observed, "pre_patch_observation_requires_revalidation"
    if observed == date.fromisoformat(PATCH_DATE):
        return observed, "patch_day_deployment_time_unknown"
    return observed, None


def _base(activity):
    return {
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE,
        "source_patch_version": PATCH_VERSION,
        "activity": activity,
        "artifact_enabled": False if activity in {"competitive", "trials"} else None,
        "current_manifest_item_verified": False,
        "current_artifact_selection_verified": False,
        "gameplay_measured": False,
        "pve_boss_dps": None,
        "pve_damage_resistance": None,
        "pvp_guardian_ttk": None,
        "evidence_grade": "official_historical_patch_rule_not_playtest",
    }


def audit_centrifuse_refill(*, observation_date, activity, event,
                           weapon_name="Centrifuse",
                           source_patch_version=PATCH_VERSION):
    """Screen the *amount* of a hypothetical refill, not its trigger."""
    _, freshness = _inputs(observation_date, activity, source_patch_version)
    if not isinstance(weapon_name, str) or not weapon_name.strip():
        raise ValueError("weapon_name must be nonempty")
    if not isinstance(event, str) or not event.strip():
        raise ValueError("event must be nonempty")
    if freshness is not None:
        status = freshness
    elif weapon_name.strip().casefold() != "centrifuse":
        status = "weapon_identity_not_established"
    elif event != "refill_trigger":
        status = "event_not_supported_by_patch_note"
    else:
        status = "official_post_patch_refill_amount_only"
    return {
        **_base(activity),
        "status": status,
        "weapon_name": weapon_name,
        "event": event,
        "previous_refill_percent_per_trigger_official": 4,
        "post_patch_refill_percent_per_trigger_official":
            10 if status == "official_post_patch_refill_amount_only" else None,
        "refill_trigger_conditions": None,
        "weapon_kill_attribution": None,
        "refill_frequency": None,
        "actual_refill_measured": False,
        "current_weapon_roll_certified": False,
    }


def audit_unbreakable_devour(*, observation_date, activity, class_name,
                            event, aspect_equipped,
                            source_patch_version=PATCH_VERSION):
    """Screen the explicit Titan blast-final-blow condition, not Devour uptime."""
    _, freshness = _inputs(observation_date, activity, source_patch_version)
    if class_name not in CLASSES:
        raise ValueError("unknown class")
    if not isinstance(event, str) or not event.strip():
        raise ValueError("event must be nonempty")
    if type(aspect_equipped) is not bool:
        raise ValueError("aspect_equipped must be bool")
    if freshness is not None:
        status = freshness
    elif class_name != "titan":
        status = "class_not_supported_by_aspect"
    elif not aspect_equipped:
        status = "aspect_not_equipped"
    elif event != "unbreakable_blast_final_blow":
        status = "event_not_supported_by_patch_note"
    else:
        status = "official_post_patch_condition_only"
    return {
        **_base(activity),
        "status": status,
        "class_name": class_name,
        "event": event,
        "aspect_equipped_supplied_not_verified": aspect_equipped,
        "official_devour_grant_condition_met":
            status == "official_post_patch_condition_only",
        "devour_duration_seconds": None,
        "devour_healing_measured": False,
        "blast_kill_attribution_measured": False,
        "ability_regeneration_measured": False,
        "guardian_final_blow_verified": False,
    }
