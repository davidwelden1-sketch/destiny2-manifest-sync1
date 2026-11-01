"""Hunter Lethal Current historical multi-activation bug evidence.

Bungie Update 9.7.0.2 (2026-06-23):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

Official patch says Lethal Current could activate multiple times on one attack,
causing PvP one-shots, and was fixed. It does NOT say all possible one-shots
were eliminated, give current damage numbers, or certify any Artifact synergy.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
PATCH_VERSION = "9.7.0.2"
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def review_lethal_current(*, activity, observation_date,
                          source_patch_version=PATCH_VERSION):
    if not isinstance(activity, str) or activity not in ACTIVITIES:
        raise ValueError("unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source patch required")
    if not isinstance(observation_date, str):
        raise ValueError("observation date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("noncanonical observation date")

    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_pvp_multi_proc_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif activity == "pve":
        status = "pve_transfer_not_supported_by_pvp_patch_note"
    else:
        status = "official_historical_pvp_multi_activation_bug_fixed"

    return {
        "class": "Hunter",
        "aspect": "Lethal Current",
        "activity": activity,
        "status": status,
        "patch_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "source_url": SOURCE_URL,
        "evidence_grade": "official_historical_patch_not_measured",
        "historical_bug": "multiple_activations_per_single_attack_caused_pvp_one_shots",
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "all_one_shots_eliminated": None,
        "damage_ownership": None,
        "activation_count_measured": None,
        "current_artifact_selection_verified": False,
        "gameplay_measured": False,
        "guardian_ttk": None,
        "pve_boss_dps": None,
    }
