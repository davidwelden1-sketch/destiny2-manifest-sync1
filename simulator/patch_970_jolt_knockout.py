"""Historical 9.7.0 Arc construct jolt and Titan Knockout rule gates.

Official patch 2026-06-09: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
This module does not calculate real jolt DPS, PvP melee damage, or TTK.
"""
from datetime import date
from decimal import Decimal, InvalidOperation

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
ACTIVITIES = frozenset({"pve", "pvp", "competitive", "trials"})
CONSTRUCTS = {"Spark of Shock": frozenset({"Arc Soul", "Ionic Sentry"}),
              "Facet of Dominance": frozenset({"Arc Soul"})}


def _context(*, activity, observation_date, source_patch_version):
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Explicit supported activity required")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    if type(source_patch_version) is not str or not source_patch_version.strip():
        raise ValueError("Source patch version required")
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_observation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "historical_patch_rule_only"
    return status


def _base(*, activity, observation_date, status):
    return {
        "source_url": SOURCE_URL, "source_published_at": PATCH_DATE.isoformat(),
        "reviewed_at": "2026-11-02", "patch_version": PATCH_VERSION,
        "activity": activity, "observation_date": observation_date,
        "evidence": "official_historical", "status": status,
        "artifact_effects_active": False if activity in {"competitive", "trials"} else None,
        "current_artifact_allocation_verified": False,
        "runtime_verified": False, "pve_boss_dps_measured": None,
        "pve_dr_measured": None, "pvp_guardian_damage_measured": None,
        "pvp_ttk_measured": None, "ability_cooldown_measured": None,
        "weapon_hash_legality_verified": False,
        "certified_for_app_build_recommendation": False,
    }


def review_construct_jolt(*, fragment, construct, activity, observation_date,
                           seconds_since_last_application=None,
                           source_patch_version=PATCH_VERSION):
    """Review a single known construct against the historical 4-second gate.

    The patch does not specify cross-construct ownership, first application,
    target-specific cooldowns, or whether another jolt source shares the timer.
    Four seconds elapsed is necessary for this documented reapplication gate,
    not sufficient to guarantee a proc or any damage.
    """
    status = _context(activity=activity, observation_date=observation_date,
                      source_patch_version=source_patch_version)
    if type(fragment) is not str or fragment not in CONSTRUCTS:
        raise ValueError("Unsupported fragment")
    if type(construct) is not str or construct not in {"Arc Soul", "Ionic Sentry"}:
        raise ValueError("Unsupported construct")
    elapsed = None
    if seconds_since_last_application is not None:
        if type(seconds_since_last_application) not in (int, str, Decimal):
            raise ValueError("Exact nonnegative seconds required; no float")
        try:
            elapsed = Decimal(str(seconds_since_last_application))
        except InvalidOperation as exc:
            raise ValueError("Invalid elapsed seconds") from exc
        if not elapsed.is_finite() or elapsed < 0:
            raise ValueError("Nonnegative finite seconds required")
    documented = construct in CONSTRUCTS[fragment]
    gate = None
    if status == "historical_patch_rule_only" and documented and elapsed is not None:
        gate = "inside_four_second_cooldown" if elapsed < Decimal(4) else "outside_four_second_cooldown_proc_not_guaranteed"
    return {
        **_base(activity=activity, observation_date=observation_date, status=status),
        "id": "d2:patch-rule:970:arc-construct-jolt-icd",
        "fragment": fragment, "construct": construct,
        "combination_documented": documented,
        "historical_internal_cooldown_seconds": 4 if documented and status == "historical_patch_rule_only" else None,
        "elapsed_since_last_application_supplied_seconds": str(elapsed) if elapsed is not None else None,
        "historical_timing_gate": gate,
        "cross_construct_shared_timer_verified": False,
        "jolt_damage_measured": None,
        "activation_guaranteed": False,
    }


def review_knockout_pvp(*, activity, observation_date, source_patch_version=PATCH_VERSION):
    """Return only the two explicitly documented PvP Knockout changes."""
    status = _context(activity=activity, observation_date=observation_date,
                      source_patch_version=source_patch_version)
    applicable = status == "historical_patch_rule_only" and activity != "pve"
    return {
        **_base(activity=activity, observation_date=observation_date, status=status),
        "id": "d2:patch-rule:970:titan-knockout-pvp-melee",
        "guardian_class": "titan", "pvp_specific_rule_applicable": applicable,
        "bonus_lunge_range_vs_players": False if applicable else None,
        "activating_melee_receives_early_knockout_bonus": False if applicable else None,
        "melee_base_damage_measured": None, "melee_lunge_distance_measured": None,
    }
