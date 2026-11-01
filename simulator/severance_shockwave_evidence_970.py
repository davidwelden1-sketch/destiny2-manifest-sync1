"""Source-gated Titan Severance Enclosure shockwave evidence from Bungie 9.7.0.

Patch statements are not measured DPS, shockwave chain counts, or PvP
disorientation evidence. Do not infer that a removed repeated-hit exclusion
guarantees two hits, or that a relaxed occlusion check ignores all cover.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 9)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_CHECKED_AT = "2026-11-01"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
SCENARIOS = frozenset((
    "repeat_shockwave_combatant", "occluded_combatant",
    "shockwave_disorient_combatant", "repeat_shockwave_guardian",
    "finisher_chain", "weapon_kill",
))
PVE_PATCH_CHANGES = {
    "repeat_shockwave_combatant": "short_interval_repeat_hit_exclusion_removed",
    "occluded_combatant": "occlusion_requirement_relaxed_not_removed",
    "shockwave_disorient_combatant": "combatant_disorientation_added_duration_unspecified",
}


def assess_severance_shockwave(*, guardian_class, activity, observation_date,
                              scenario, artifact_name=None, artifact_perks=(),
                              manifest_version=None):
    """Return only official patch deltas; never invent activation or damage."""
    if guardian_class not in CLASSES or activity not in ACTIVITIES:
        raise ValueError("Unknown class or activity")
    if scenario not in SCENARIOS:
        raise ValueError("Unknown shockwave scenario")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")
    if type(artifact_perks) not in (list, tuple) or len(artifact_perks) > 7:
        raise ValueError("At most seven selected Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Artifact perks must be nonempty names")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Invalid Artifact name")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require one named Artifact")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")

    titan = guardian_class == "titan"
    eligible = activity not in ("competitive", "trials")
    # Bungie's wording concerns combatants; do not project these effects
    # onto Guardians, even when the PvP activity includes PvE enemies.
    official_change = (PVE_PATCH_CHANGES.get(scenario)
                       if titan and activity == "pve" and observed >= PATCH_DATE
                       else None)
    return {
        "guardian_class": guardian_class,
        "exotic_class_eligible": titan,
        "activity": activity,
        "scenario": scenario,
        "observation_date": observation_date,
        "official_patch_change": official_change,
        "evidence_grade": ("official_historical_patch_delta_not_measured"
                           if official_change else "unresolved_no_gameplay_claim"),
        "source_url": SOURCE_URL,
        "source_checked_at": SOURCE_CHECKED_AT,
        "patch_date": PATCH_DATE.isoformat(),
        "manifest_version": manifest_version,
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_mode_eligible": eligible,
        "artifact_effects_active": None if eligible else False,
        "artifact_allocation_legal_verified": False,
        "weapon_roll_verified": False,
        "shockwave_chain_count_measured": None,
        "repeated_hit_damage_measured": None,
        "disorient_duration_seconds_measured": None,
        "damage_ownership_measured": None,
        "kill_attribution_measured": None,
        "measured_pve_boss_dps": None,
        "measured_pvp_ttk": None,
    }
