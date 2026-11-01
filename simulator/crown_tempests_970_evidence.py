"""Source-gated Crown of Tempests 9.7.0 research leads, not gameplay results.

Official Bungie Update 9.7.0 (2026-06-09):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

A stack of Conduction Tines is required for Ionic Sentry to create a
Storm Grenade on deployment. Conduction Tines duration changed from
seven to ten seconds *in PvE*. The source does not establish a PvP
duration, weapon-perk kill ownership, or a grenade energy refund.
"""
from datetime import date

SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = "2026-06-09"
PATCH_VERSION = "9.7.0"


def audit_crown_tempests(*, observation_date, activity, class_name,
                         event, tines_stacks, source_patch_version=PATCH_VERSION):
    """Screen a hypothetical event; never certify an observed proc.

    Stack count is a caller-supplied condition, not verified game state.
    PvE duration is a historical official patch value, not measured uptime.
    """
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be YYYY-MM-DD")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("unknown activity")
    if class_name not in ("hunter", "titan", "warlock"):
        raise ValueError("unknown class")
    if event not in ("ionic_sentry_deploy", "weapon_kill", "grenade_damage"):
        raise ValueError("unknown event")
    if type(tines_stacks) is not int or tines_stacks < 0:
        raise ValueError("tines_stacks must be a nonnegative integer")
    if not isinstance(source_patch_version, str) or not source_patch_version:
        raise ValueError("source_patch_version must be a nonempty string")

    if source_patch_version != PATCH_VERSION:
        status = "source_patch_mismatch"
    elif class_name != "warlock":
        status = "class_not_supported_by_exotic"
    elif event != "ionic_sentry_deploy":
        status = "event_not_supported_by_official_rule"
    elif observed < date.fromisoformat(PATCH_DATE):
        status = "pre_patch_requires_historical_revalidation"
    elif observation_date == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif tines_stacks == 0:
        status = "no_conduction_tines_stack"
    else:
        status = "official_post_patch_condition_only"

    eligible = status == "official_post_patch_condition_only"
    return {
        "status": status,
        "official_ionic_sentry_storm_grenade_condition_met": eligible,
        "condition_verified_in_game": False,
        "tines_stacks_supplied_not_measured": tines_stacks,
        "pve_conduction_tines_duration_seconds_official_historical":
            10 if activity == "pve" and class_name == "warlock" and observed > date.fromisoformat(PATCH_DATE)
            and source_patch_version == PATCH_VERSION else None,
        "pve_previous_duration_seconds_official": 7 if activity == "pve" and class_name == "warlock" else None,
        "pvp_conduction_tines_duration_seconds": None,
        "storm_grenade_damage_measured": False,
        "weapon_perk_trigger_from_grenade": None,
        "grenade_kill_attribution": None,
        "ability_energy_refund": None,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "artifact_enabled": False if activity in ("competitive", "trials") else None,
        "source_url": SOURCE,
        "source_date": PATCH_DATE,
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_rule_not_playtest",
    }
