"""Source-scoped 9.7.0 exotic weapon activation/ammo leads.

Bungie 2026-06-09: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Historical patch values are NOT a measured scorch cadence, ignition count,
reload speed, boss DPS, Guardian TTK, or a certified live build.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
SOURCE_CHECKED_AT = "2026-11-02"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
EVENTS = frozenset(("scorch_trigger", "buff_active", "weapon_hit", "weapon_final_blow"))
RULES = {
    "prometheus_lens": {
        "event": "scorch_trigger",
        "id": "d2:patch-rule:970:prometheus-lens:scorch-per-trigger",
        "before": {"max_base_scorch_stacks": 10, "conditional_extra_stacks": 10},
        "after": {"max_base_scorch_stacks": 20, "conditional_extra_stacks": 10},
    },
    "slayers_fang": {
        "event": "buff_active",
        "id": "d2:patch-rule:970:slayers-fang:buff-reload-ammo",
        "after": {
            "magazine_size_delta": 2,
            "reserve_ammo_delta": 10,
            "slow_self_reload_while_buff_active": True,
        },
    },
}


def assess_exotic_weapon_970(*, weapon, guardian_class, activity, event_kind,
                             observation_date, manifest_version=None,
                             item_hash=None, artifact_name=None,
                             artifact_perks=()):
    """Return official historical parameters and explicitly unknown runtime facts."""
    if type(weapon) is not str or weapon not in RULES:
        raise ValueError("Unknown exotic weapon")
    if (type(guardian_class) is not str or guardian_class not in CLASSES or\n            type(activity) is not str or activity not in ACTIVITIES):
        raise ValueError("Unknown class or activity")
    if type(event_kind) is not str or event_kind not in EVENTS:
        raise ValueError("Unknown event")
    if type(observation_date) is not str:
        raise ValueError("Canonical date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical date required")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if item_hash is not None and (
            type(item_hash) is not int or item_hash < 0 or item_hash > 0xFFFFFFFF):
        raise ValueError("Invalid unsigned item hash")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact name")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require a named Artifact")

    rule = RULES[weapon]
    after_patch = observed > PATCH_DATE
    event_matches = event_kind == rule["event"]
    if observed == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif observed < PATCH_DATE:
        status = "pre_patch"
    elif not event_matches:
        status = "official_mechanic_event_not_matched"
    else:
        status = "official_historical_patch_candidate_unmeasured"
    supported = after_patch and event_matches
    return {
        "id": rule["id"],
        "weapon": weapon,
        "guardian_class": guardian_class,
        "activity": activity,
        "event_kind": event_kind,
        "observation_date": observation_date,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_checked_at": SOURCE_CHECKED_AT,
        "patch_version": PATCH_VERSION,
        "manifest_version": manifest_version,
        "item_hash_input_unverified": item_hash,
        "status": status,
        "official_historical_rule_applicable": supported,
        "prepatch_parameters": dict(rule.get("before", {})) if supported else None,
        "postpatch_parameters": dict(rule["after"]) if supported else None,
        "evidence_grade": "official_historical_patch_not_gameplay_measured",
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_item_hash_and_perk_legality_verified": False,
        "runtime_trigger_frequency_verified": False,
        "scorch_to_ignition_threshold_verified": False,
        "self_reload_rate_verified": False,
        "self_reload_while_stowed_verified": False,
        "specific_exotic_armor_synergy_verified": False,
        "measured_pve_boss_dps": None,
        "measured_pve_damage_resistance": None,
        "measured_pvp_guardian_ttk": None,
        "measured_cooldown_or_uptime": None,
    }


def official_prometheus_stack_delta():
    """Arithmetic on published per-trigger maxima only, not gameplay ticks."""
    old = RULES["prometheus_lens"]["before"]
    new = RULES["prometheus_lens"]["after"]
    return {
        "published_max_base_stack_delta": (
            new["max_base_scorch_stacks"] - old["max_base_scorch_stacks"]),
        "published_conditional_extra_stacks_unchanged": (
            old["conditional_extra_stacks"] == new["conditional_extra_stacks"]),
        "published_max_if_conditional_applies_before": (
            old["max_base_scorch_stacks"] + old["conditional_extra_stacks"]),
        "published_max_if_conditional_applies_after": (
            new["max_base_scorch_stacks"] + new["conditional_extra_stacks"]),
        "not_an_ignition_or_ttk_prediction": True,
        "measured_pve_dps": None,
        "measured_pvp_ttk": None,
    }
