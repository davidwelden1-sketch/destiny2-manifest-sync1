"""Official historical 9.7.0.2 named weapon interaction evidence, not gameplay data.
Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2
"""
from datetime import date

PATCH_VERSION = "9.7.0.2"
PATCH_DATE = date(2026, 6, 23)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
GRADE = "official_historical_patch_note_not_measured"
EVENTS = {
    "forge_kin_black_armory_non_enhanced": (
        "Forge's Kin",
        "Fixed non-enhanced Forge's Kin not receiving increased benefits when multiple Black Armory weapons were equipped",
    ),
    "lingering_dread_discord": (
        "Lingering Dread",
        "Fixed Lingering Dread Grenade Launcher not benefiting from Discord perk",
    ),
}
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def review_patch_interaction(*, event, activity, observation_date,
                             weapon_version="unknown", black_armory_count=None,
                             manifest_version=None, artifact_name=None,
                             artifact_perks=(), source_patch_version=PATCH_VERSION):
    """Evidence-only result. Claimed equipment and versions are not verified."""
    if type(event) is not str or event not in EVENTS:
        raise ValueError("Unknown official event")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Explicit activity required")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")
    if type(weapon_version) is not str or weapon_version not in (
        "unknown", "non_enhanced", "enhanced"
    ):
        raise ValueError("Invalid weapon version")
    if black_armory_count is not None and (
        type(black_armory_count) is not int or black_armory_count < 0
    ):
        raise ValueError("Invalid Black Armory count")
    if event == "lingering_dread_discord" and (
        weapon_version != "unknown" or black_armory_count is not None
    ):
        raise ValueError("Unrelated weapon-version/count claim")
    if manifest_version is not None and (
        type(manifest_version) is not str or not manifest_version.strip()
    ):
        raise ValueError("Invalid manifest version")
    if type(source_patch_version) is not str or not source_patch_version.strip():
        raise ValueError("Source patch version required")
    if type(artifact_perks) not in (list, tuple) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(x) is not str or not x.strip() for x in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_name is not None and (
        type(artifact_name) is not str or not artifact_name.strip()
    ):
        raise ValueError("Invalid Artifact name")
    if artifact_perks and artifact_name is None:
        raise ValueError("Artifact name required for selections")

    if source_patch_version != PATCH_VERSION:
        status = "source_patch_mismatch"
    elif observed < PATCH_DATE:
        status = "pre_fix_observation_invalid_for_post_fix_calibration"
    elif observed == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif event == "forge_kin_black_armory_non_enhanced" and weapon_version == "enhanced":
        status = "enhanced_variant_not_addressed_by_patch"
    elif event == "forge_kin_black_armory_non_enhanced" and weapon_version == "unknown":
        status = "weapon_variant_unresolved"
    elif event == "forge_kin_black_armory_non_enhanced" and (
        black_armory_count is None or black_armory_count < 2
    ):
        status = "multiple_black_armory_equipment_not_established"
    else:
        status = "historical_patch_candidate_only"

    weapon, fact = EVENTS[event]
    return {
        "id": f"d2:patch-rule:9702:{event}",
        "event": event, "weapon_name": weapon, "official_fact": fact,
        "source_url": SOURCE_URL, "source_published_at": PATCH_DATE.isoformat(),
        "source_checked_at": "2026-11-02", "patch_version": PATCH_VERSION,
        "source_patch_version_supplied": source_patch_version,
        "manifest_version": manifest_version, "activity": activity,
        "observation_date": observation_date, "status": status,
        "evidence_grade": GRADE, "weapon_version_claimed": weapon_version,
        "black_armory_equipped_count_claimed": black_armory_count,
        "weapon_version_verified": False, "equipment_membership_verified": False,
        "exact_weapon_hash_verified": False, "current_obtainability_verified": False,
        "perk_pool_verified": False, "enhanced_perk_legality_verified": False,
        "artifact_name": artifact_name, "selected_artifact_perks": list(artifact_perks),
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "artifact_allocation_verified": False,
        "pve_boss_dps_measured": None, "pve_damage_resistance_measured": None,
        "pvp_guardian_ttk_measured": None, "activation_cooldown_measured": None,
        "kill_attribution_verified": False, "damage_ownership_verified": False,
        "certified_for_app_build_recommendation": False,
    }
