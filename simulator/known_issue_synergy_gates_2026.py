"""Source-gated Destiny 2 synergy blockers from Bungie's known-issues list.

This is NOT a simulator of measured gameplay. It prevents a catalog candidate
from being promoted to a certified build while relevant known issues remain
unresolved. Source section last updated 2026-07-07, checked 2026-11-01:
https://help.bungie.net/hc/en-us/articles/39007140765204-Destiny-2-Known-Issues-and-Vital-Information
"""
from datetime import date

SOURCE_URL = ("https://help.bungie.net/hc/en-us/articles/"
              "39007140765204-Destiny-2-Known-Issues-and-Vital-Information")
SOURCE_SECTION_UPDATED = date(2026, 7, 7)
SOURCE_REVIEWED = date(2026, 11, 1)
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
ISSUE_CONDITIONS = {
    "forerunner_prismatic_gunpowder_gamble": (
        "hunter_prismatic", "forerunner_catalyst_grenade"),
    "controlled_burst_charge_time_masterwork": (
        "fusion_rifle", "controlled_burst", "charge_time_masterwork"),
    "mantle_solar_super_weapon_surge": (
        "warlock", "mantle_of_battle_harmony", "solar_super_equipped"),
    "argent_blade_only_armor_charge_source": (
        "argent_blade_selected", "only_armor_charge_source"),
}
OFFICIAL_NOTES = {
    "forerunner_prismatic_gunpowder_gamble":
        "Forerunner catalyst grenade does not grant Gunpowder Gamble charge on Prismatic.",
    "controlled_burst_charge_time_masterwork":
        "Controlled Burst does not function on Fusion Rifles with Charge Time masterwork.",
    "mantle_solar_super_weapon_surge":
        "Mantle of Battle Harmony stops granting weapon surge with Solar super equipped.",
    "argent_blade_only_armor_charge_source":
        "Argent Blade alone cannot generate armor charges when it is the only charge-generating perk.",
}


def assess_synergy_issue(*, issue, activity, conditions, observation_date,
                         manifest_version=None):
    """Return a conservative build-certification blocker, not gameplay data.

    'Conditions not all met' never proves the alternative configuration works.
    This known-issue list is not a live reproducibility test.
    """
    if issue not in ISSUE_CONDITIONS:
        raise ValueError("Unsupported known-issue key")
    if activity not in ACTIVITIES:
        raise ValueError("Unsupported activity")
    if not isinstance(conditions, dict) or set(conditions) != set(ISSUE_CONDITIONS[issue]):
        raise ValueError("Supply all and only the issue's named conditions")
    if any(type(value) is not bool for value in conditions.values()):
        raise ValueError("Conditions must be true booleans")
    if type(observation_date) is not str:
        raise ValueError("Canonical observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    if manifest_version is not None and (
            not isinstance(manifest_version, str) or not manifest_version.strip()):
        raise ValueError("Manifest version must be a nonempty string or None")
    matches = all(conditions.values())
    artifact_issue = issue == "argent_blade_only_armor_charge_source"
    artifact_enabled = activity not in ("competitive", "trials")
    if artifact_issue and not artifact_enabled:
        status = "artifact_disabled_no_artifact_synergy"
    elif observed < SOURCE_SECTION_UPDATED:
        status = "observation_predates_known_issue_snapshot"
    elif matches:
        status = "official_known_issue_blocks_certification_pending_retest"
    else:
        status = "conditions_not_all_met_no_positive_certification"
    return {
        "issue": issue,
        "activity": activity,
        "conditions": dict(conditions),
        "status": status,
        "official_issue_description": OFFICIAL_NOTES[issue],
        "source_url": SOURCE_URL,
        "source_section_last_updated": SOURCE_SECTION_UPDATED.isoformat(),
        "source_checked_at": SOURCE_REVIEWED.isoformat(),
        "evidence_grade": "official_known_issue_not_measured_gameplay",
        "manifest_version": manifest_version,
        "affected_configuration_matches": matches,
        "artifact_effects_enabled": artifact_enabled,
        "current_artifact_allocation_verified": False,
        "gameplay_retest_required": True,
        "exact_weapon_hash": None,
        "enhanced_roll_legality_verified": False,
        "current_obtainability_verified": False,
        "measured_pve_boss_dps": None,
        "measured_pvp_guardian_ttk": None,
        "measured_damage_resistance": None,
        "measured_cooldown_seconds": None,
    }
