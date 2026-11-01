"""Official 9.7.0 ability-charge and cooldown-cap evidence, not gameplay uptime.

Bungie: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published 2026-06-09. Source distinguishes PvP match-start charge rules
from the general ability-stat cooldown-cap changes. Neither gives actual
ability base cooldowns, regeneration, DR, or PvP damage.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
ACTIVITIES = frozenset({"pve", "pvp", "competitive", "trials"})
CLASSES = frozenset({"hunter", "titan", "warlock"})


def _validate(observation_date, activity, class_name, source_patch_version):
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    if activity not in ACTIVITIES or class_name not in CLASSES:
        raise ValueError("unsupported activity or class")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    if source_patch_version != PATCH_VERSION:
        return "source_patch_version_mismatch"
    if day < PATCH_DATE:
        return "pre_patch_observation_requires_revalidation"
    if day == PATCH_DATE:
        return "patch_day_deployment_time_unknown"
    return None


def _base(activity, class_name):
    return {
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "activity": activity,
        "class_name": class_name,
        "artifact_enabled": False if activity in {"competitive", "trials"} else None,
        "evidence_grade": "official_historical_patch_rule_not_gameplay_measurement",
        "gameplay_measured": False,
        "ability_cooldown_seconds": None,
        "ability_regeneration_uptime": None,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "current_artifact_allocation_verified": False,
    }


def audit_match_start_charges(*, observation_date, activity, class_name,
                              multi_charge_ability, match_start,
                              source_patch_version=PATCH_VERSION):
    """PvP match starts with ONE charge for multi-charge abilities, not all."""
    freshness = _validate(observation_date, activity, class_name, source_patch_version)
    if type(multi_charge_ability) is not bool or type(match_start) is not bool:
        raise ValueError("multi_charge_ability and match_start must be bool")
    if freshness is not None:
        status = freshness
    elif activity == "pve":
        status = "pvp_only_rule_not_applicable_to_pve"
    elif not multi_charge_ability:
        status = "not_a_multi_charge_ability"
    elif not match_start:
        status = "mid_match_charges_not_established"
    else:
        status = "official_pvp_multi_charge_match_start_rule"
    return {
        **_base(activity, class_name),
        "status": status,
        "starting_charges_official":
            1 if status == "official_pvp_multi_charge_match_start_rule" else None,
        "maximum_ability_charges": None,
        "match_start_supplied_not_measured": match_start,
        "multi_charge_supplied_not_verified": multi_charge_ability,
    }


def audit_ability_stat_cooldown_caps(*, observation_date, activity, class_name,
                                    source_patch_version=PATCH_VERSION):
    """Record only Bungie's cap changes, not exact ability cooldowns.

    Passive maximum was reduced by approximately 20% (no absolute cap given).
    Active maximum bonus was reduced from 190% to 125%; these are not
    equivalent to cooldown seconds or an exact 65-percentage-point loss of uptime.
    """
    freshness = _validate(observation_date, activity, class_name, source_patch_version)
    status = freshness or "official_general_cooldown_stat_cap_changes_only"
    valid = freshness is None
    return {
        **_base(activity, class_name),
        "status": status,
        "passive_maximum_bonus_relative_reduction_approx_percent": 20 if valid else None,
        "previous_active_maximum_bonus_percent": 190 if valid else None,
        "post_patch_active_maximum_bonus_percent": 125 if valid else None,
        "passive_exact_bonus_curve": None,
        "active_exact_bonus_curve": None,
        "specific_ability_base_cooldown_seconds": None,
    }
