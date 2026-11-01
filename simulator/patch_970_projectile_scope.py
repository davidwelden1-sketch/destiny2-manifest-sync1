"""Historical 9.7.0 projectile shield and Meganeura evidence, not DPS.

Official Bungie patch (2026-06-09):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
No exact weapon hashes, obtainable rolls, damage ownership or current-game
measurements are certified by these name/family-level statements.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = date(2026, 6, 9)
PATCH_VERSION = "9.7.0"
SHIELD_PROJECTILE_FAMILIES = frozenset((
    "rocket_launcher_projectile",
    "hierarchy_of_needs_submunition",
    "caster_frame_sword_projectile",
))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def audit_projectile_patch(*, rule, family, activity, observation_date,
                           anti_barrier_capable=None,
                           source_patch_version=PATCH_VERSION):
    """Fail closed: expose official patch scope without inventing damage.

    Meganeura was corrected across archetypes but Bungie did not enumerate
    affected hashes, numerical changes or a PvP scalar. Anti-Barrier is
    explicitly conditional on the projectile having that capability.
    """
    if rule not in ("meganeura_detonation_scaling_fix", "anti_barrier_shield_overpenetration"):
        raise ValueError("unknown projectile rule")
    if not isinstance(family, str) or not family.strip():
        raise ValueError("family must be nonempty text")
    if activity not in ACTIVITIES:
        raise ValueError("unsupported activity")
    if type(anti_barrier_capable) not in (bool, type(None)):
        raise ValueError("anti_barrier_capable must be boolean or unknown")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be ISO date")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("noncanonical observation_date")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty text")

    status = "official_historical_patch_scope_only"
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif activity != "pve":
        status = "pvp_application_not_established"
    elif rule == "anti_barrier_shield_overpenetration":
        if family not in SHIELD_PROJECTILE_FAMILIES:
            status = "projectile_family_not_in_official_list"
        elif anti_barrier_capable is not True:
            status = ("anti_barrier_capability_absent" if anti_barrier_capable is False
                      else "anti_barrier_capability_unverified")
    elif family != "meganeura_trait_detonation":
        status = "trait_family_not_in_official_list"

    return {
        "status": status,
        "rule": rule,
        "family": family,
        "activity": activity,
        "anti_barrier_capable": anti_barrier_capable,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_scope",
        "artifact_enabled": False if activity in ("competitive", "trials") else None,
        "historical_effect": (
            "Meganeura detonation scaling was corrected across archetypes; "
            "most weapons had been dealing less damage than intended"
            if rule == "meganeura_detonation_scaling_fix" else
            "listed projectiles can over-penetrate combatant shields when Anti-Barrier capable"
        ) if status == "official_historical_patch_scope_only" else None,
        "affected_exact_item_hashes": None,
        "obtainable_roll_verified": False,
        "enhanced_perk_verified": False,
        "active_artifact_verified": False,
        "current_gameplay_verified": False,
        "gameplay_measured": False,
        "damage_ownership_measured": False,
        "champion_stun_verified": False,
        "guardian_shield_penetration_verified": False,
        "damage_multiplier": None,
        "boss_dps": None,
        "guardian_ttk": None,
    }
