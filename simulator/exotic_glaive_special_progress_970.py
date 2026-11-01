"""Source-gated *nominal* special-shot progress for the three Exotic Glaives.

Bungie 2025-01-23: six weapon hits (projectile or melee) to special reload.
Bungie 2025-02-20: previously class-locked glaives intentionally usable on
all three classes. Bungie 2026-06-09 Update 9.7.0: projectiles grant DOUBLE
progress. The combination is a theoretical event counter, not a measured
activation, DPS, PvP TTK, or proof of an exact obtainable item roll.
"""
from datetime import date

SOURCE_2025_BASELINE = "https://www.bungie.net/7/en/News/article/twid-01-23-25"
SOURCE_CROSS_CLASS = "https://www.bungie.net/7/en/News/article/twid_02_20_2025"
SOURCE_970 = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = date(2026, 6, 9)
SOURCE_CHECKED_AT = "2026-11-01"
NOMINAL_THRESHOLD = 6
GLAIVES = {
    "edge_of_action": "destabilizing_rounds_intrinsic",
    "edge_of_concurrence": "jolting_feedback_intrinsic",
    "edge_of_intent": "incandescent_intrinsic",
}
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def assess_exotic_glaive_progress(*, weapon, guardian_class, activity,
                                  projectile_hits, melee_hits,
                                  observation_date, artifact_name=None,
                                  artifact_perks=(), manifest_version=None):
    """Compute *nominal* post-9.7.0 progress, not a gameplay measurement.

    A returned threshold crossing is a TEST PREDICTION only. No projectile
    accuracy, on-hit credit, cooldown, real-time buff state, or perk stacking
    is observed here. No Artifact slot legality is inferred.
    """
    if weapon not in GLAIVES or guardian_class not in CLASSES:
        raise ValueError("Unknown Exotic Glaive or Guardian class")
    if activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if any(type(n) is not int or n < 0 for n in (projectile_hits, melee_hits)):
        raise ValueError("Hit counts must be nonnegative integers")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")
    if not isinstance(artifact_perks, (tuple, list)) or len(artifact_perks) > 7:
        raise ValueError("At most seven selected perks from one Artifact")
    if (any(type(p) is not str or not p.strip() for p in artifact_perks)
            or len(set(artifact_perks)) != len(artifact_perks)):
        raise ValueError("Selected Artifact perks must be unique nonempty names")
    if artifact_name is not None and (type(artifact_name) is not str
                                      or not artifact_name.strip()):
        raise ValueError("Artifact name must be nonempty or None")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require one named Artifact")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Manifest version must be nonempty or None")

    post_patch = observed >= PATCH_DATE
    nominal_progress = 2 * projectile_hits + melee_hits if post_patch else None
    artifact_mode_eligible = activity not in ("competitive", "trials")
    return {
        "weapon": weapon,
        "guardian_class": guardian_class,
        "activity": activity,
        "intrinsic_trait_effect": GLAIVES[weapon],
        "cross_class_use_officially_supported": True,
        "observation_date": observation_date,
        "patch_date": PATCH_DATE.isoformat(),
        "status": ("post_patch_theoretical_progress_only" if post_patch
                   else "pre_patch_no_retroactive_double_progress"),
        "nominal_special_progress_units": nominal_progress,
        "nominal_threshold_units": NOMINAL_THRESHOLD,
        "nominal_threshold_reached": (
            nominal_progress >= NOMINAL_THRESHOLD if post_patch else None),
        "projectile_progress_units_per_hit": 2 if post_patch else None,
        "melee_progress_units_per_hit": 1 if post_patch else None,
        "source_urls": (SOURCE_2025_BASELINE, SOURCE_CROSS_CLASS, SOURCE_970),
        "source_checked_at": SOURCE_CHECKED_AT,
        "evidence_grade": "official_patch_inputs_synthetic_counter_not_gameplay",
        "manifest_version": manifest_version,
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_mode_eligible": artifact_mode_eligible,
        "artifact_effects_active": None if artifact_mode_eligible else False,
        "artifact_allocation_legal_verified": False,
        "exact_weapon_hash_verified": False,
        "enhanced_perk_legality_verified": False,
        "special_shot_ready_in_game_verified": False,
        "measured_pve_boss_dps": None,
        "measured_pvp_guardian_ttk": None,
        "measured_damage_resistance": None,
        "measured_cooldown_seconds": None,
    }
