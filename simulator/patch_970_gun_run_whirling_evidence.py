"""Historical Bungie 9.7.0 origin-trait and Rocket Pulse compensation evidence.

Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Official patch statements are NOT measured activation, DPS or TTK.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = "2026-06-09"
PATCH_VERSION = "9.7.0"
RULES = {
    "gun_and_run": {
        "family": "gambit_origin_trait",
        "activation": ("final_blows_build_stacks", "sprinting_consumes_stack"),
        "effect": "Partial magazine reload from reserves; on Bows, brief draw-speed improvement.",
        "relative_anticipation_gain": None,
    },
    "whirling_ovation": {
        "family": "named_weapon",
        "activation": ("damage_grants_anticipation",),
        "effect": "Anticipation gained per point of damage increased by just over 11%.",
        "relative_anticipation_gain": "just_over_11_percent_not_exact",
    },
}


def review_970_trigger(key, *, activity, class_name, observation_date,
                       event, weapon_type=None, source_patch_version=PATCH_VERSION):
    """Conservative event gate for a patch note, never a gameplay certification."""
    if key not in RULES:
        raise ValueError("Unknown official correction")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("Unknown activity")
    if class_name not in ("hunter", "titan", "warlock"):
        raise ValueError("Unknown class")
    if weapon_type not in (None, "bow", "other"):
        raise ValueError("Unknown weapon type")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("Missing source patch version")
    if not isinstance(event, str) or not event.strip():
        raise ValueError("Missing event")
    if not isinstance(observation_date, str):
        raise ValueError("Date must be canonical ISO")
    try:
        when = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if when.isoformat() != observation_date:
        raise ValueError("Date must be canonical ISO")
    rule = RULES[key]
    if source_patch_version != PATCH_VERSION:
        status = "source_version_mismatch"
    elif event not in rule["activation"]:
        status = "event_not_in_official_activation"
    elif when < date.fromisoformat(PATCH_DATE):
        status = "historical_pre_fix_revalidation_required"
    elif observation_date == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "post_patch_not_gameplay_measured"
    return {
        "key": key,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE,
        "source_patch_version": PATCH_VERSION,
        "activity": activity,
        "class_name": class_name,
        "weapon_type": weapon_type,
        "event": event,
        "status": status,
        "official_family": rule["family"],
        "official_activation_conditions": rule["activation"],
        "official_effect": rule["effect"],
        "official_relative_anticipation_gain": rule["relative_anticipation_gain"],
        "bow_specific_draw_speed_effect": (key == "gun_and_run" and weapon_type == "bow"),
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "weapon_hash_verified": False,
        "perk_membership_verified": False,
        "enhanced_legality_verified": False,
        "measured_trigger_rate": None,
        "measured_reload_amount": None,
        "measured_anticipation_per_damage": None,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "damage_resistance": None,
        "evidence_grade": "official_historical_patch_note_only",
    }
