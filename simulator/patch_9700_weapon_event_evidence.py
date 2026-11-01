"""Historical Bungie 9.7.0 weapon-event fixes; no playable-build certification.

Official 2026-06-09 patch: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
The notes do not give ammo-meter amounts, timer seconds, exact damage ownership,
or activity-specific measurements. Do not infer those from a bug-fix statement.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 9)
PATCH_VERSION = "9.7.0"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
MODES = frozenset(("pve", "pvp", "competitive", "trials"))
CORRECTIONS = {
    "trinity_ghoul_lightning_rod_chain_kill_ammo_progress":
        "Lightning Rod chain kills no longer fail to grant ammo progress",
    "new_land_beyond_bullseye_bolster_precision_timer_refresh":
        "precision hits refresh Bullseye Bolster while the perk is already active",
}


def audit_weapon_event(*, mechanic, activity, observation_date,
                       source_patch_version=PATCH_VERSION):
    """Expose official historical correction without fabricating proc metrics."""
    if not isinstance(mechanic, str) or mechanic not in CORRECTIONS:
        raise ValueError("unknown weapon event")
    if not isinstance(activity, str) or activity not in MODES:
        raise ValueError("unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source patch version required")
    if not isinstance(observation_date, str):
        raise ValueError("canonical ISO observation date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("noncanonical observation date")

    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "official_historical_correction_activity_scope_unverified"

    artifact_eligible = activity not in ("competitive", "trials")
    return {
        "mechanic": mechanic,
        "activity": activity,
        "status": status,
        "historical_correction": CORRECTIONS[mechanic] if status.startswith("official_") else None,
        "source_url": SOURCE_URL,
        "source_patch_version": PATCH_VERSION,
        "source_date": PATCH_DATE.isoformat(),
        "evidence_grade": "official_historical_patch_not_measured",
        "activity_specific_activation_verified": False,
        "artifact_mode_eligible": artifact_eligible,
        "artifact_effects_active": None if artifact_eligible else False,
        "ammo_progress_per_chain_kill": None,
        "ammo_bricks_per_kill": None,
        "bullseye_bolster_timer_seconds": None,
        "damage_ownership": None,
        "kill_attribution_measured": False,
        "boss_dps": None,
        "guardian_ttk": None,
        "current_artifact_rotation_verified": False,
        "exact_weapon_hash_verified": False,
        "gameplay_measured": False,
    }
