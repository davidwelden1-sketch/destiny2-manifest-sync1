"""Official 9.7.0.3 encounter-, class-, and mode-scoped historical corrections.

Bungie 2026-07-07: https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_3
These are source-scoped revalidation gates, not measured DPS/TTK, current
weapon roll legality, or proof that an Artifact is currently selectable.
"""
from datetime import date

PATCH_DATE = "2026-07-07"
PATCH_VERSION = "9.7.0.3"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_3"

CHANGES = {
    "pantheon_insurrection_prime_divinity_cage": {
        "scope": "pve_boss_damage",
        "modes": ("pve",),
        "encounter": "pantheon_insurrection_prime",
        "class": None,
        "artifact": False,
        "fact": "Divinity and damage applied to its cage no longer damage Insurrection Prime at any point in Pantheon; this is encounter-specific.",
    },
    "pantheon_consecrated_mind_remote_tether": {
        "scope": "pve_encounter_mechanics",
        "modes": ("pve",),
        "encounter": "pantheon_consecrated_mind",
        "class": None,
        "artifact": False,
        "fact": "Re-enabled remote tether functionality for Consecrated Mind in Pantheon.",
    },
    "hunter_phantom_surge_stylish_executioner": {
        "scope": "ability_perk_activation",
        "modes": ("pve", "pvp"),
        "encounter": None,
        "class": "hunter",
        "artifact": False,
        "fact": "Fixed Phantom Surge failing to hit or trigger perks on weakened or tethered targets while Stylish Executioner was active.",
    },
    "titan_ward_of_dawn_projectile_block": {
        "scope": "pvp_defense",
        "modes": ("pvp",),
        "encounter": None,
        "class": "titan",
        "artifact": False,
        "fact": "Fixed some projectiles and abilities passing through Ward of Dawn in PvP.",
    },
    "pack_tactics_performance": {
        "scope": "artifact_performance",
        "modes": ("pve", "pvp"),
        "encounter": None,
        "class": None,
        "artifact": True,
        "fact": "Fixed Pack Tactics Artifact perk causing performance issues during extended play; no damage or uptime scalar supplied.",
    },
    "backfang_drifter_focusing": {
        "scope": "weapon_acquisition_focusing",
        "modes": ("pve", "pvp"),
        "encounter": None,
        "class": None,
        "artifact": False,
        "fact": "Fixed some players being unable to focus the Backfang Glaive at the Drifter; no perk pool or roll guarantee supplied.",
    },
}


def audit_patch_9703(change_key, observation_date, *, activity, class_name=None,
                     encounter=None, source_patch_version=PATCH_VERSION):
    """Conservatively triage an observation without extrapolating patch scope.

    Patch-day deployment timing is unknown. A historical correction never
    proves current behavior, and a class/encounter mismatch cannot be used
    to calibrate a different build or activity.
    """
    if not isinstance(change_key, str) or change_key not in CHANGES:
        raise ValueError("Unknown patch correction")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("Unknown activity")
    if class_name not in (None, "hunter", "titan", "warlock"):
        raise ValueError("Unknown class")
    if encounter is not None and (not isinstance(encounter, str) or not encounter.strip()):
        raise ValueError("Encounter must be a nonempty string or None")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")

    change = CHANGES[change_key]
    mode = "pve" if activity == "pve" else "pvp"
    artifact_enabled = False if activity in ("competitive", "trials") else None
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif change["artifact"] and artifact_enabled is False:
        status = "artifact_disabled_in_activity"
    elif mode not in change["modes"]:
        status = "not_supported_for_activity"
    elif change["class"] is not None and class_name != change["class"]:
        status = "class_scope_not_established"
    elif change["encounter"] is not None and encounter != change["encounter"]:
        status = "encounter_scope_not_established"
    elif observed < date.fromisoformat(PATCH_DATE):
        status = "pre_fix_observation_requires_revalidation"
    elif observation_date == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "post_fix_not_gameplay_certification"

    return {
        "change_key": change_key,
        "official_fact": change["fact"],
        "scope": change["scope"],
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE,
        "source_patch_version": PATCH_VERSION,
        "observation_date": observation_date,
        "activity": activity,
        "class_name": class_name,
        "encounter": encounter,
        "status": status,
        "revalidation_required": status in (
            "pre_fix_observation_requires_revalidation",
            "patch_day_deployment_time_unknown",
        ),
        "artifact_enabled": artifact_enabled,
        "current_artifact_selection_verified": False,
        "current_weapon_hash_verified": False,
        "current_roll_or_enhancement_verified": False,
        "gameplay_measured": False,
        "damage_ownership": None,
        "pve_boss_dps": None,
        "pve_damage_resistance": None,
        "pvp_guardian_ttk": None,
        "evidence_grade": "official_historical_patch_note_only",
    }
