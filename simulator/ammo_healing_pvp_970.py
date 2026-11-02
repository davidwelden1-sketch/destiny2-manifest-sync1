"""Bungie 9.7.0 ammo, movement-healing and PvP tick-spacing evidence.

Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published 2026-06-09; reviewed 2026-11-02.
These are published component deltas, NOT measured boss DPS, Guardian TTK,
healing uptime, ammo availability, or exact-hash item/Artifact legality.
"""
from datetime import date

SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH = "9.7.0"
PATCH_DATE = "2026-06-09"
CHECKED_AT = "2026-11-02"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))

# Enhanced means an enhanced ammo brick, NOT an enhanced weapon trait.
RULES = {
    "heavy_precision_linear_base_brick": ("pve", "heavy_precision_linear_brick", {"ammo_before": 3, "ammo_after": 5, "brick_type": "base"}),
    "heavy_precision_linear_enhanced_brick": ("pve", "heavy_precision_linear_brick", {"ammo_before": 4, "ammo_after": 6, "brick_type": "enhanced"}),
    "special_precision_linear_base_brick": ("pve", "special_precision_linear_brick", {"ammo_before": 3, "ammo_after": 5, "brick_type": "base"}),
    "special_precision_linear_enhanced_brick": ("pve", "special_precision_linear_brick", {"ammo_before": 6, "ammo_after": 10, "brick_type": "enhanced"}),
    "rapid_fire_machine_gun_crate": ("pvp", "rapid_fire_machine_gun_crate_pickup", {"maximum_ammo_before": 45, "maximum_ammo_after": 62, "magazine_dependent": True}),
    "deimosuffusion_player_tick": ("pvp", "deimosuffusion_damage_tick_against_player", {"seconds_between_ticks_before": 0.1, "seconds_between_ticks_after": 0.3}),
    "superluminal_motion_moving_heal": ("pve", "wayward_psyche_four_piece_moving", {"health_per_second_before": 15, "health_per_second_after": 30}),
    "superluminal_motion_pvp_unchanged": ("pvp", "wayward_psyche_four_piece_moving", {"pvp_performance_unchanged": True}),
}
RULE_IDS = {key: "d2:patch-rule:970:ammo-heal-pvp:" + key.replace("_", "-") for key in RULES}


def assess_ammo_healing_pvp_970(*, mechanic, guardian_class, activity,
                               event_kind, observation_date,
                               source_patch_version=PATCH, manifest_version=None,
                               item_hash=None, artifact_name=None,
                               artifact_perks=()):
    """Return conservative app-ready historical evidence with explicit unknowns."""
    if type(mechanic) is not str or mechanic not in RULES:
        raise ValueError("Unknown mechanic")
    if type(guardian_class) is not str or guardian_class not in CLASSES:
        raise ValueError("Unknown class")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if type(event_kind) is not str or not event_kind.strip():
        raise ValueError("Invalid event")
    if type(observation_date) is not str:
        raise ValueError("Canonical observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical observation date required")
    if type(source_patch_version) is not str or not source_patch_version.strip():
        raise ValueError("Invalid source patch")
    if manifest_version is not None and (type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if item_hash is not None and (type(item_hash) is not int or not 0 <= item_hash <= 0xFFFFFFFF):
        raise ValueError("Invalid unsigned item hash")
    if artifact_name is not None and (type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven selected Artifact perks")
    if any(type(x) is not str or not x.strip() for x in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perk")
    if artifact_perks and artifact_name is None:
        raise ValueError("Artifact perks require named Artifact")

    scope, event, published = RULES[mechanic]
    if source_patch_version != PATCH:
        status = "source_patch_version_mismatch"
    elif observed < date.fromisoformat(PATCH_DATE):
        status = "pre_patch"
    elif observed == date.fromisoformat(PATCH_DATE):
        status = "patch_day_deployment_time_unknown"
    elif (scope == "pve" and activity != "pve") or (scope == "pvp" and activity == "pve"):
        status = "activity_not_supported"
    elif event_kind != event:
        status = "event_not_supported"
    else:
        status = "official_historical_patch_component_only"
    applicable = status == "official_historical_patch_component_only"
    return {
        "id": RULE_IDS[mechanic], "mechanic": mechanic,
        "guardian_class": guardian_class, "activity": activity,
        "event_kind": event_kind, "status": status,
        "official_historical_rule_applicable": applicable,
        "published_component_change": dict(published) if applicable else None,
        "source_url": SOURCE, "source_date": PATCH_DATE,
        "source_checked_at": CHECKED_AT, "patch_version": PATCH,
        "evidence_grade": "official_historical_patch_not_gameplay_measured",
        "manifest_version_input_unverified": manifest_version,
        "item_hash_input_unverified": item_hash,
        "artifact_name": artifact_name, "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_item_hash_and_enhanced_perk_legality_verified": False,
        "pve_boss_dps_measured": None, "pve_damage_resistance_measured": None,
        "pve_healing_uptime_measured": None, "pvp_guardian_ttk_measured": None,
        "pvp_damage_per_tick_measured": None, "ammo_drop_rate_measured": None,
        "ability_cooldown_measured": None,
    }
