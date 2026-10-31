"""Official 9.7.0.1 Zephyr left-column correction freshness gate.

Bungie 2026-06-16: Zephyr could drop with right-column traits in the
left column; affected perks are updated in place. This is a source-level
historical invalidation, not a current obtainable or enhanced roll index.
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_1
"""
from datetime import date

PATCH_DATE = "2026-06-16"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_1"


def audit_zephyr_left_column(*, weapon_name, observation_date, column,
                             activity="pve"):
    """Flag pre-fix Zephyr left-column observations without certifying rolls.

    Patch-day dates alone cannot distinguish observations before/after
    deployment. A current manifest hash, item acquisition, and live roll
    verification are separate requirements.
    """
    if not isinstance(weapon_name, str) or not weapon_name.strip():
        raise ValueError("weapon_name must be a nonempty string")
    if column not in ("left", "right"):
        raise ValueError("column must be left or right")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("unsupported activity")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("observation_date must be YYYY-MM-DD") from exc
    if parsed.isoformat() != observation_date:
        raise ValueError("observation_date must be YYYY-MM-DD")

    affected = weapon_name.strip().casefold() == "zephyr" and column == "left"
    if not affected:
        status = "not_affected_by_this_specific_fix"
    elif observation_date < PATCH_DATE:
        status = "pre_fix_left_column_requires_revalidation"
    elif observation_date == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "post_fix_observation_not_roll_certification"

    return {
        "weaponName": weapon_name.strip(),
        "column": column,
        "observationDate": observation_date,
        "activity": activity,
        "sourceUrl": SOURCE_URL,
        "patchDate": PATCH_DATE,
        "evidenceGrade": "official_patch_note_not_live_instance_evidence",
        "status": status,
        "leftColumnObservationRevalidationRequired": affected and
            observation_date <= PATCH_DATE,
        "artifactEnabled": False if activity in ("competitive", "trials") else None,
        "currentExactRollCertified": False,
        "enhancedTraitCertified": False,
        "currentAcquisitionCertified": False,
        "pveBossDpsMeasured": False,
        "pvpTtkMeasured": False,
    }
