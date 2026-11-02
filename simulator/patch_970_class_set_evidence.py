"""Source-gated 9.7.0 / 9.7.0.2 class, grenade and armor-set changes.

Official Bungie patch notes:
2026-06-09 https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
2026-06-23 https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2
Published deltas are not measured PvE DPS, Guardian TTK, uptime or exact
equipment/Artifact legality. A percentage change to a component is not a
percentage change to an entire damage or regeneration loop.
"""
from datetime import date

SOURCE_CHECKED_AT = "2026-11-02"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
PATCHES = {
    "9.7.0": ("2026-06-09", "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"),
    "9.7.0.2": ("2026-06-23", "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"),
}
# "any" scope means Bungie did not specify activity-specific activation.
RULES = {
    "pale_heart_two_piece": {
        "patch": "9.7.0.2", "class": "any", "scope": "any",
        "event": "stack_em_up_stack_gained",
        "id": "d2:patch-rule:9702:pale-heart:two-piece-transcendence",
        "published": {"light_energy_per_stack": None, "dark_energy_per_stack": None,
                      "flat_amounts_instead_of_multiplier": True},
    },
    "scatter_grenade_chase": {
        "patch": "9.7.0", "class": "any", "scope": "pvp",
        "event": "scatter_seekers_chase_player",
        "id": "d2:patch-rule:970:scatter-grenade:player-chase-distance",
        "published": {"chase_distance_relative_to_prepatch": 0.5},
    },
    "scatter_grenade_perk_energy": {
        "patch": "9.7.0", "class": "any", "scope": "any",
        "event": "scatter_grenade_receives_perk_energy",
        "id": "d2:patch-rule:970:scatter-grenade:perk-energy",
        "published": {"perk_energy_gain_relative_to_prepatch": 0.875},
    },
    "hammer_strike_combatant": {
        "patch": "9.7.0", "class": "titan", "scope": "pve",
        "event": "hammer_strike_hits_combatant",
        "id": "d2:patch-rule:970:titan:hammer-strike-combatant-damage",
        "published": {"attack_damage_relative_to_prepatch": 2.0},
    },
    "shield_bash_combatant": {
        "patch": "9.7.0", "class": "titan", "scope": "pve",
        "event": "shield_bash_hits_combatant",
        "id": "d2:patch-rule:970:titan:shield-bash-combatant-damage",
        "published": {"attack_damage_relative_to_prepatch": 2.0},
    },
    "seismic_strike_combatant": {
        "patch": "9.7.0", "class": "titan", "scope": "pve",
        "event": "seismic_strike_hits_combatant",
        "id": "d2:patch-rule:970:titan:seismic-strike-combatant-damage",
        "published": {"attack_damage_relative_to_prepatch": 2.0},
    },
}


def assess_patch_970_class_set(*, mechanic, guardian_class, activity, event_kind,
                               observation_date, source_patch_version=None,
                               manifest_version=None, item_hash=None,
                               artifact_name=None, artifact_perks=()):
    """Return app-ready official historical evidence, never a certified build."""
    if type(mechanic) is not str or mechanic not in RULES:
        raise ValueError("Unknown mechanic")
    if type(guardian_class) is not str or guardian_class not in CLASSES:
        raise ValueError("Unknown guardian class")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if type(event_kind) is not str or not event_kind.strip():
        raise ValueError("Invalid event kind")
    if type(observation_date) is not str:
        raise ValueError("Canonical observation date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Canonical observation date required")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if item_hash is not None and (
            type(item_hash) is not int or not 0 <= item_hash <= 0xFFFFFFFF):
        raise ValueError("Invalid unsigned item hash")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(x) is not str or not x.strip() for x in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perk")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require named Artifact")

    rule = RULES[mechanic]
    patch = rule["patch"]
    patch_date, source_url = PATCHES[patch]
    in_class = rule["class"] == "any" or guardian_class == rule["class"]
    in_scope = (rule["scope"] == "any" or
                (rule["scope"] == "pve" and activity == "pve") or
                (rule["scope"] == "pvp" and activity in ("pvp", "competitive", "trials")))
    if source_patch_version is not None and source_patch_version != patch:
        status = "source_patch_version_mismatch"
    elif day < date.fromisoformat(patch_date):
        status = "pre_patch"
    elif day == date.fromisoformat(patch_date):
        status = "patch_day_deployment_time_unknown"
    elif not in_class:
        status = "class_not_supported"
    elif not in_scope:
        status = "activity_not_supported_by_official_rule"
    elif event_kind != rule["event"]:
        status = "trigger_not_established"
    else:
        status = "official_historical_patch_delta_only"
    applicable = status == "official_historical_patch_delta_only"
    return {
        "id": rule["id"],
        "mechanic": mechanic,
        "guardian_class": guardian_class,
        "activity": activity,
        "event_kind": event_kind,
        "status": status,
        "official_historical_rule_applicable": applicable,
        "published_component_change": dict(rule["published"]) if applicable else None,
        "source_url": source_url,
        "source_date": patch_date,
        "source_checked_at": SOURCE_CHECKED_AT,
        "patch_version": patch,
        "manifest_version_input_unverified": manifest_version,
        "item_hash_input_unverified": item_hash,
        "evidence_grade": "official_historical_patch_not_gameplay_measured",
        "mode_applicability_verified": applicable and rule["scope"] != "any",
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_item_hash_and_enhanced_roll_legality_verified": False,
        "set_bonus_activation_measured": False,
        "transcendence_energy_amount_measured": None,
        "scatter_grenade_tracking_distance_measured": None,
        "perk_energy_return_measured": None,
        "melee_damage_measured": None,
        "pve_boss_dps_measured": None,
        "pve_damage_resistance_measured": None,
        "pvp_guardian_ttk_measured": None,
        "ability_cooldown_or_uptime_measured": None,
    }
