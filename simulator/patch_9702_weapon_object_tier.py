"""Official 9.7.0.2 Turncoat and Cynosure weapon-interaction leads.

Bungie June 23 2026: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2
This is historical patch evidence, not a measured current weapon build.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
PATCH_VERSION = "9.7.0.2"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
EVENTS = frozenset(("turncoat_object_damage", "cynosure_higher_tier_extra_traits"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def review_weapon_interaction(*, event, activity, observation_date,
                              source_patch_version=PATCH_VERSION):
    """Triage source-scoped mechanics without certifying current playability."""
    if not isinstance(event, str) or event not in EVENTS:
        raise ValueError("Unsupported event")
    if not isinstance(activity, str) or activity not in ACTIVITIES:
        raise ValueError("Unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version:
        raise ValueError("Source patch version required")
    if not isinstance(observation_date, str):
        raise ValueError("Observation date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "historical_observation_requires_post_patch_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "official_historical_fix_not_current_measurement"
    facts = {
        "turncoat_object_damage": {
            "weapon": "Turncoat",
            "official_correction": "Can damage objects such as Gunpowder Gamble while empowered",
            "class_interaction_lead": "Hunter",
            "object_damage_ownership": None,
            "gunpowder_gamble_detonation_attribution": None,
        },
        "cynosure_higher_tier_extra_traits": {
            "weapon": "Cynosure",
            "official_correction": "Higher-tier Rocket Launcher drops can roll extra traits",
            "class_interaction_lead": "Hunter/Titan/Warlock",
            "exact_extra_trait_threshold": None,
            "obtainable_socket_pair": None,
        },
    }
    return {
        **facts[event],
        "event": event,
        "activity": activity,
        "status": status,
        "source_url": SOURCE_URL,
        "patch_version": PATCH_VERSION,
        "patch_date": PATCH_DATE.isoformat(),
        "evidence_grade": "official_historical_patch_not_live_gameplay",
        "exact_weapon_hash": None,
        "manifest_version": None,
        "current_artifact_allocation_verified": False,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "enhanced_perk_legality": "unverified",
        "current_obtainability": "unverified",
        "gameplay_measured": False,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
    }
