"""Source-scoped 9.7.0 class survivability leads; not a gameplay simulator.

No weapon roll, Exotic proc, damage multiplier, cooldown, or PvP TTK is
certified here. A source-supported condition is NOT a measured activation.
"""
from datetime import date

PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_CHECKED_AT = "2026-11-02"
RULES = {
    "shieldburst_rally": {"class": "titan", "event": "rally_cover"},
    "rope_dart_catch": {"class": "hunter", "event": "dart_catch"},
    "heat_rises_accuracy": {"class": "warlock", "event": "heat_rises_active"},
}
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
EVENTS = frozenset(("rally_cover", "dart_catch", "heat_rises_active", "weapon_final_blow"))


def assess_survivability_lead(*, mechanic, guardian_class, activity,
                              observation_date, event_kind, weapon_element=None,
                              ally_target=None, dart_defeats=None,
                              manifest_version=None, artifact_name=None,
                              artifact_perks=()):
    """Return only official historical mechanics and explicit uncertainty."""
    if type(mechanic) is not str or mechanic not in RULES:
        raise ValueError("Unknown mechanic")
    if guardian_class not in ("hunter", "titan", "warlock"):
        raise ValueError("Unknown class")
    if activity not in ACTIVITIES or event_kind not in EVENTS:
        raise ValueError("Unknown activity or event")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    if weapon_element is not None and weapon_element not in (
            "solar", "kinetic", "arc", "void", "stasis", "strand"):
        raise ValueError("Unknown weapon element")
    if ally_target is not None and type(ally_target) is not bool:
        raise ValueError("ally_target must be boolean")
    if dart_defeats is not None and (
            type(dart_defeats) is not int or dart_defeats < 0):
        raise ValueError("dart_defeats must be nonnegative integer")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perk")
    if artifact_perks and artifact_name is None:
        raise ValueError("Artifact perks require one named Artifact")

    rule = RULES[mechanic]
    in_scope = guardian_class == rule["class"] and observed >= PATCH_DATE
    event_matches = event_kind == rule["event"]
    # These are *source text* conditions, not confirmation of in-game procs.
    if mechanic == "shieldburst_rally":
        condition = (event_matches and ally_target is True and
                     weapon_element in ("solar", "kinetic"))
        described = "allied_solar_or_kinetic_weapon_scorching_rounds"
        pvp_scope = "not_independently_measured"
    elif mechanic == "rope_dart_catch":
        condition = event_matches and dart_defeats is not None and dart_defeats > 0
        described = "woven_mail_on_successful_catch_scaled_by_targets_defeated"
        pvp_scope = "guardian_defeat_behavior_not_measured"
    else:
        condition = event_matches and activity == "pve"
        described = "reduced_combatant_attack_accuracy_while_heat_rises_active"
        pvp_scope = "no_guardian_accuracy_claim_in_source"

    return {
        "id": f"d2:patch-rule:970:survival-lead:{mechanic}",
        "guardian_class": guardian_class,
        "activity": activity,
        "event_kind": event_kind,
        "observation_date": observation_date,
        "patch_version": PATCH_VERSION,
        "patch_date": PATCH_DATE.isoformat(),
        "source_url": SOURCE_URL,
        "source_checked_at": SOURCE_CHECKED_AT,
        "manifest_version": manifest_version,
        "evidence_grade": ("official_historical_patch_not_live_measured" if in_scope
                           else "out_of_scope_or_pre_patch_unverified"),
        "official_mechanic": described if in_scope else None,
        "source_supported_candidate": bool(in_scope and condition),
        "pvp_scope": pvp_scope,
        "weapon_element": weapon_element,
        "ally_target": ally_target,
        "dart_defeats": dart_defeats,
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_weapon_hash_and_roll_verified": False,
        "specific_exotic_proc_verified": False,
        "runtime_activation_verified": False,
        "measured_pve_dps": None,
        "measured_pve_damage_resistance": None,
        "measured_pvp_ttk": None,
        "measured_cooldown_or_uptime": None,
    }
