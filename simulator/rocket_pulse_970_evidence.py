"""Official 9.7.0 Rocket Pulse patch gates, NOT calibrated gameplay DPS.

Bungie, 2026-06-09:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

Keep the general PvE 10% reduction and additional boss 25% reduction
separate: the note says "on top" but does not measure a live damage event.
The generic Special-ammo +20% elite change explicitly EXCLUDES Rocket Pulses.
No PvP TTK, item-hash roll, enhanced perk, Artifact or damage ownership
is established by this historical archetype-level patch.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DAY = date(2026, 6, 9)
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
TARGETS = frozenset(("minor", "elite", "champion", "boss", "guardian"))
CLASSES = frozenset(("hunter", "titan", "warlock"))


def review_rocket_pulse(*, activity, target, class_name, observation_date,
                        source_patch_version=PATCH_VERSION):
    """Return evidence-gated patch inputs, never measured gameplay outputs."""
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if type(target) is not str or target not in TARGETS:
        raise ValueError("Unknown target")
    if type(class_name) is not str or class_name not in CLASSES:
        raise ValueError("Unknown class")
    if type(source_patch_version) is not str or not source_patch_version:
        raise ValueError("Source patch version required")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")

    valid = source_patch_version == PATCH_VERSION and day > PATCH_DAY
    pve = activity == "pve" and target != "guardian"
    pvp = activity != "pve" and target == "guardian"
    if source_patch_version != PATCH_VERSION:
        status = "patch_version_mismatch"
    elif day < PATCH_DAY:
        status = "pre_patch_observation_requires_revalidation"
    elif day == PATCH_DAY:
        status = "patch_day_deployment_time_unknown"
    elif not (pve or pvp):
        status = "activity_target_mismatch"
    else:
        status = "historical_official_archetype_rule_not_measured"

    eligible = valid and pve
    return {
        "status": status,
        "class_name": class_name,
        "activity": activity,
        "target": target,
        "general_pve_damage_change_percent": -10 if eligible else None,
        "additional_boss_damage_change_percent":
            -25 if eligible and target == "boss" else None,
        "generic_special_elite_20_percent_bonus_applies":
            False if eligible and target == "elite" else None,
        "projectile_explosion_radius_change_percent": -25 if valid else None,
        "roaming_super_generation_change_percent": -25 if valid else None,
        "standard_super_generation_change_percent": -33 if valid else None,
        "combined_boss_damage_multiplier_measured": None,
        "measured_pve_dps": None,
        "measured_pvp_ttk": None,
        "damage_ownership": None,
        "kill_attribution": None,
        "exact_item_hash_verified": False,
        "enhanced_roll_verified": False,
        "current_artifact_allocation_verified": False,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DAY.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_rule_not_gameplay_measurement",
    }
