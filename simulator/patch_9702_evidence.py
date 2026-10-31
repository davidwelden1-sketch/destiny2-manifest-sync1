"""Fail-closed official Destiny 2 9.7.0.2 historical patch evidence.

Source: Bungie, 2026-06-23
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

These facts invalidate some pre-patch roll and combat observations. They do
not certify current weapon hashes, acquisition, Artifact selection, DPS, TTK,
or post-fix gameplay measurements.
"""
from datetime import date

PATCH_DATE = "2026-06-23"
PATCH_VERSION = "9.7.0.2"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"

# Source-level scope, not a list of current obtainable item hashes.
CHANGES = {
    "europa_moon_rocket_lead_from_gold": {
        "scope": "weapon_roll", "affected_modes": ("pve", "pvp"),
        "fact": "Lead from Gold was unintended on Europa/Moon rockets; existing instances were changed to Impromptu Ammunition.",
    },
    "raid_adept_perk_sync": {
        "scope": "weapon_roll", "affected_modes": ("pve", "pvp"),
        "fact": "Some raid Adepts had perk pools out of sync with base versions; affected inventory traits were updated.",
    },
    "cynosure_higher_tier_extra_traits": {
        "scope": "weapon_roll", "affected_modes": ("pve", "pvp"),
        "fact": "Fixed Cynosure not dropping extra traits on higher-tier versions.",
    },
    "ergo_sum_vortex_heavy_ammo": {
        "scope": "weapon_ammo", "affected_modes": ("pve", "pvp"),
        "fact": "Ergo Sum vortex heavy attack ammo cost corrected from 6 to 4.",
    },
    "frostees_frost_armor_pvp": {
        "scope": "armor_uptime", "affected_modes": ("pvp",),
        "fact": "Reduced the rate at which Frostees generate Frost Armor in PvP.",
    },
    "hunter_lethal_current_multi_proc": {
        "scope": "ability_damage", "affected_modes": ("pvp",),
        "fact": "Fixed Lethal Current activating multiple times on one attack and causing PvP one-shots.",
    },
    "pit_of_heresy_four_piece": {
        "scope": "armor_damage", "affected_modes": ("pve", "pvp"),
        "fact": "Fixed instant ignition loop and changed four-piece scorch from 30+10 to 20+10.",
    },
    "vile_weave_tangle_cooldown": {
        "scope": "artifact_cooldown", "affected_modes": ("pve", "pvp"),
        "fact": "Fixed Tablet of Ruin Vile Weave not reducing Tangle cooldown as intended.",
    },
    "unto_the_breach_prismatic": {
        "scope": "artifact_activation", "affected_modes": ("pve", "pvp"),
        "fact": "Fixed Unto the Breach not benefiting Prismatic subclasses.",
    },
    "artifact_duplicate_restriction": {
        "scope": "artifact_legality", "affected_modes": ("pve", "pvp"),
        "fact": "Fixed certain conditions bypassing the no-duplicate Artifact perk restriction.",
    },
}


def audit_patch_9702(change_key, observation_date, *, activity,
                     source_patch_version=PATCH_VERSION):
    """Screen historical evidence, never infer post-fix playability.

    PvE/PvP scope is *research relevance*, not a claim that the affected
    perk or Artifact works in every activity. Patch-day order is unknown.
    """
    if not isinstance(change_key, str) or change_key not in CHANGES:
        raise ValueError("change_key must be a recognized patch correction")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be YYYY-MM-DD")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("observation_date must be YYYY-MM-DD") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("activity must be explicit")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")

    change = CHANGES[change_key]
    research_mode = "pve" if activity == "pve" else "pvp"
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif research_mode not in change["affected_modes"]:
        status = "not_supported_for_this_activity_by_source"
    elif observed < date.fromisoformat(PATCH_DATE):
        status = "pre_fix_observation_requires_revalidation"
    elif observation_date == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "post_fix_observation_not_gameplay_certification"

    return {
        "change_key": change_key,
        "scope": change["scope"],
        "official_fact": change["fact"],
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE,
        "source_patch_version": PATCH_VERSION,
        "observation_date": observation_date,
        "activity": activity,
        "status": status,
        "revalidation_required": status in (
            "pre_fix_observation_requires_revalidation",
            "patch_day_deployment_time_unknown",
        ),
        "artifact_enabled": False if activity in ("competitive", "trials") else None,
        "current_weapon_hash_verified": False,
        "current_roll_or_enhancement_verified": False,
        "current_artifact_selection_verified": False,
        "gameplay_measured": False,
        "pve_boss_dps": None,
        "pve_damage_resistance": None,
        "pvp_guardian_ttk": None,
        "damage_ownership": None,
        "evidence_grade": "official_historical_patch_note_only",
    }
