"""Source-gated cross-class 9.7.0 Exotic/Super evidence.

Bungie official historical patch (2026-06-09):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

These rules document published mechanics, not measured gameplay, currently
legal loadouts, boss DPS, Guardian damage/TTK, or a current Artifact.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
SOURCE_CHECKED_AT = "2026-11-02"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
RULES = {
    "shards_of_galanor": {
        "id": "d2:patch-rule:970:hunter:shards-galanor-delayed-explosion",
        "class": "hunter",
        "event": "blade_barrage_most_knives_land",
        "published": {
            "delayed_solar_explosion": True,
            "releases_solar_shrapnel": True,
            "minimum_knives_required": None,
            "explosion_damage": None,
        },
    },
    "pyrogale_gauntlets": {
        "id": "d2:patch-rule:970:titan:pyrogale-cyclone-explosion",
        "class": "titan",
        "event": "super_cyclone_explosion",
        "published": {
            "explosion_damage_relative_to_prepatch": 1.10,
            "super_cyclone_tracking_increase_approx_fraction": 0.40,
            "scorch_per_tick_increased_unspecified": True,
        },
    },
    "ward_of_dawn_core": {
        "id": "d2:patch-rule:970:titan:ward-dawn-core-relocation",
        "class": "titan",
        "event": "ward_core_relocation",
        "published": {
            "maximum_core_relocations": 2,
            "ward_destroyed_if_core_destroyed": True,
            "weapons_of_light_for_allies_inside": True,
            "increased_melee_damage_for_owner": True,
            "weapons_of_light_damage_multiplier": None,
        },
    },
    "astrocyte_verse": {
        "id": "d2:patch-rule:970:warlock:astrocyte-blink-volatile",
        "class": "warlock",
        "event": "blink_or_dark_blink",
        "published": {
            "air_move_horizontal_dark_blink": True,
            "blink_grants_volatile_rounds": True,
            "volatile_rounds_duration_seconds": None,
            "guardian_damage": None,
        },
    },
}


def assess_exotic_super_970(*, mechanic, guardian_class, activity, event_kind,
                            observation_date, source_patch_version=PATCH_VERSION,
                            manifest_version=None, item_hash=None,
                            artifact_name=None, artifact_perks=(),
                            relocation_count=None):
    """Return historical evidence with fail-closed, activity-separated gates."""
    if type(mechanic) is not str or mechanic not in RULES:
        raise ValueError("Unknown mechanic")
    if type(guardian_class) is not str or guardian_class not in CLASSES:
        raise ValueError("Unknown guardian class")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if type(event_kind) is not str or not event_kind.strip():
        raise ValueError("Invalid event kind")
    if type(source_patch_version) is not str or not source_patch_version.strip():
        raise ValueError("Invalid patch version")
    if type(observation_date) is not str:
        raise ValueError("Canonical observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical observation date required")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if item_hash is not None and (
            type(item_hash) is not int or not 0 <= item_hash <= 0xFFFFFFFF):
        raise ValueError("Invalid unsigned item hash")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact name")
    if type(artifact_perks) not in (list, tuple) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perk")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require a named Artifact")
    if relocation_count is not None and (
            mechanic != "ward_of_dawn_core" or type(relocation_count) is not int
            or relocation_count < 0):
        raise ValueError("Invalid relocation count")

    rule = RULES[mechanic]
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif observed < PATCH_DATE:
        status = "pre_patch"
    elif observed == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif guardian_class != rule["class"]:
        status = "class_not_supported"
    elif event_kind != rule["event"]:
        status = "trigger_not_established"
    elif relocation_count is not None and relocation_count > 2:
        status = "exceeds_official_ward_relocation_limit"
    else:
        status = "official_historical_patch_only"
    applicable = status == "official_historical_patch_only"
    return {
        "id": rule["id"],
        "mechanic": mechanic,
        "guardian_class": guardian_class,
        "activity": activity,
        "event_kind": event_kind,
        "status": status,
        "official_historical_rule_applicable": applicable,
        "published_component_change": dict(rule["published"]) if applicable else None,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_checked_at": SOURCE_CHECKED_AT,
        "patch_version": PATCH_VERSION,
        "manifest_version_input_unverified": manifest_version,
        "item_hash_input_unverified": item_hash,
        "relocation_count_input_unverified": relocation_count,
        "evidence_grade": "official_historical_patch_not_gameplay_measured",
        "mode_applicability_verified": False,
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_item_hash_and_perk_legality_verified": False,
        "current_runtime_verified": False,
        "pve_boss_dps_measured": None,
        "pve_damage_resistance_measured": None,
        "pvp_guardian_damage_measured": None,
        "pvp_guardian_ttk_measured": None,
        "ability_cooldown_or_uptime_measured": None,
        "effect_stacking_verified": False,
        "certified_for_app_build_recommendation": False,
    }
