"""Source-gated Helm of Saint-14 + movable Ward of Dawn research.

Official historical Bungie Update 9.7.0, 2026-06-09:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

This models *eligibility to investigate*, not measured stack generation,
suppression uptime, damage attribution, Ward duration, or Guardian TTK.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 9)
PATCH_VERSION = "9.7.0"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
CLASSES = frozenset(("hunter", "titan", "warlock"))
EVENTS = frozenset(("kill", "sustained_damage", "ward_pickup"))
DAMAGE_TYPES = frozenset(("kinetic", "void", "other", "unknown"))


def review_saint_ward(*, class_name, activity, event, damage_type,
                      weapons_of_light_active, observation_date,
                      source_patch_version=PATCH_VERSION):
    """Review the class, mode and official activation boundary."""
    if type(class_name) is not str or class_name not in CLASSES:
        raise ValueError("Unknown class")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if type(event) is not str or event not in EVENTS:
        raise ValueError("Unknown event")
    if type(damage_type) is not str or damage_type not in DAMAGE_TYPES:
        raise ValueError("Unknown damage type")
    if type(weapons_of_light_active) is not bool:
        raise ValueError("Weapons of Light state must be boolean")
    if type(source_patch_version) is not str or not source_patch_version.strip():
        raise ValueError("Source patch version required")
    if type(observation_date) is not str:
        raise ValueError("Observation date must be canonical ISO")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Observation date must be canonical ISO")

    # Helm of Saint-14 is Titan-only. Other classes may benefit from
    # allied Weapons of Light but cannot equip the Helm to create stacks.
    helm_equippable = class_name == "titan"
    valid_patch = source_patch_version == PATCH_VERSION and day > PATCH_DATE
    eligible = helm_equippable and valid_patch and weapons_of_light_active
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_rework_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif not helm_equippable:
        status = "helm_not_equippable_on_class"
    elif not weapons_of_light_active:
        status = "weapons_of_light_not_active"
    else:
        status = "official_historical_rule_not_measured"

    return {
        "class_name": class_name,
        "activity": activity,
        "event": event,
        "damage_type": damage_type,
        "status": status,
        "helm_equippable": helm_equippable,
        "official_max_ward_relocations": 2 if helm_equippable and valid_patch else None,
        "the_saint_stack_generation_eligible": eligible and event in ("kill", "sustained_damage"),
        "void_or_kinetic_suppression_eligible": (
            eligible and event in ("kill", "sustained_damage")
            and damage_type in ("void", "kinetic")
        ),
        "ward_pickup_consumes_stacks_and_extends_duration_official": (
            eligible and event == "ward_pickup"
        ),
        "ward_duration_extension_seconds": None,
        "the_saint_stack_threshold": None,
        "stack_gain_per_kill": None,
        "stack_gain_per_damage": None,
        "suppression_radius_meters": None,
        "suppression_duration_seconds": None,
        "damage_ownership": None,
        "kill_attribution": None,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "current_artifact_allocation_verified": False,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_rule_not_gameplay_measurement",
    }
