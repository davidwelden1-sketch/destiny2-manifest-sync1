"""Source-gated weapon and ability corrections from Bungie 9.7.0.2.

Historical official patch statements, not live gameplay measurements.
Caller-supplied hashes and Artifact choices are never treated as verified.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
PATCH_VERSION = "9.7.0.2"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
SOURCE_CHECKED_AT = "2026-11-01"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
INTERACTIONS = frozenset((
    "ergo_sum_vortex_heavy",
    "hierarchy_precision_guidance",
    "hunter_lethal_current_multi_activation",
))


def assess_patch_9702_interaction(*, interaction_id, guardian_class, activity,
                                  observation_date, item_hash=None,
                                  manifest_version=None, artifact_name=None,
                                  artifact_perks=()):
    """Return narrow official evidence without extrapolating PvE/PvP or live rolls."""
    if type(interaction_id) is not str or interaction_id not in INTERACTIONS:
        raise ValueError("Unknown patch interaction")
    if guardian_class not in CLASSES or activity not in ACTIVITIES:
        raise ValueError("Unknown class or activity")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")
    if item_hash is not None and (type(item_hash) is not int or not 0 < item_hash < 2**32):
        raise ValueError("Item hash must be a positive unsigned 32-bit integer")
    if manifest_version is not None and (type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_name is not None and (type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact name")
    if artifact_perks and artifact_name is None:
        raise ValueError("Artifact perks require a named Artifact")

    post_patch = observed >= PATCH_DATE
    is_guardian_pvp = activity in ("pvp", "competitive", "trials")
    class_eligible = interaction_id != "hunter_lethal_current_multi_activation" or guardian_class == "hunter"
    scoped = post_patch and class_eligible and (
        interaction_id == "ergo_sum_vortex_heavy" or is_guardian_pvp)
    return {
        "id": f"d2:patch-rule:9702:{interaction_id}",
        "interaction_id": interaction_id,
        "guardian_class": guardian_class,
        "activity": activity,
        "observation_date": observation_date,
        "patch_version": PATCH_VERSION,
        "patch_date": PATCH_DATE.isoformat(),
        "source_url": SOURCE_URL,
        "source_checked_at": SOURCE_CHECKED_AT,
        "manifest_version": manifest_version,
        "item_hash_reported_by_caller": item_hash,
        "item_hash_identity_verified": False,
        "post_patch_scope": scoped,
        "evidence_grade": ("official_historical_patch_not_live_measured"
                           if scoped else "out_of_scope_or_pre_patch_unverified"),
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "artifact_allocation_legal_verified": False,
        "current_runtime_verified": False,
        "current_acquisition_verified": False,
        "enhanced_perk_legality_verified": False,
        "measured_pve_dps": None,
        "measured_pve_damage_resistance": None,
        "measured_pvp_ttk": None,
        "measured_cooldown_seconds": None,
        "ergo_sum_vortex_heavy_ammo_cost_official": 4 if scoped and interaction_id == "ergo_sum_vortex_heavy" else None,
        "ergo_sum_vortex_pre_fix_cost_official": 6 if scoped and interaction_id == "ergo_sum_vortex_heavy" else None,
        "hierarchy_precision_guardian_guidance_fixed": (
            True if scoped and is_guardian_pvp and interaction_id == "hierarchy_precision_guidance" else None),
        "lethal_current_multi_activation_pvp_one_shot_bug_fixed": (
            True if scoped and is_guardian_pvp and interaction_id == "hunter_lethal_current_multi_activation" else None),
    }
