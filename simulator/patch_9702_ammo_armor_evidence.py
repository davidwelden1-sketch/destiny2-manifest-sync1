"""Source-gated historical 9.7.0.2 ammo, weapon and armor evidence.

Bungie patch published 2026-06-23:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

Never treat reductions to a BONUS as reductions to total ammo progress.
Neither historical patch notes nor synthetic checks measure current DPS,
Guardian TTK, Frost Armor cadence or exact Artifact legality.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
PATCH_VERSION = "9.7.0.2"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
PVP_MODES = frozenset(("pvp", "competitive", "trials"))
MODES = frozenset(("pve", "pvp", "competitive", "trials"))

# (activity family, historical previous, post-patch, unit)
RULES = {
    "kings_fall_special_ammo_progress_bonus": ("pve", 1.0, 0.30, "fraction_of_old_bonus_not_total_progress"),
    "kings_fall_heavy_ammo_progress_bonus": ("pve", 1.0, 0.25, "fraction_of_old_bonus_not_total_progress"),
    "ergo_sum_vortex_heavy_attack_ammo_cost": ("pve", 6, 4, "ammo_per_heavy_attack"),
    "truth_maximum_ammo_reserves": ("pve", 14, 10, "reserve_ammo"),
    "hierarchy_precision_player_guidance": ("pvp", False, True, "bug_fixed_guidance_energy_on_precision_player_damage"),
    "frostees_pvp_frost_armor_generation": ("pvp", "higher_pre_patch", "reduced_amount_unspecified", "rate_change_no_numeric_value"),
    "ex_diris_mothkeeper_requires_active_moth_charge": ("pve", True, False, "bug_condition_removed"),
}


def audit_patch_9702(*, mechanic, activity, observation_date,
                     source_patch_version=PATCH_VERSION):
    if not isinstance(mechanic, str) or mechanic not in RULES:
        raise ValueError("unknown mechanic")
    if not isinstance(activity, str) or activity not in MODES:
        raise ValueError("unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version required")
    if not isinstance(observation_date, str):
        raise ValueError("ISO observation_date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("noncanonical observation_date")

    scope, previous, after, unit = RULES[mechanic]
    in_scope = activity == "pve" if scope == "pve" else activity in PVP_MODES
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif not in_scope:
        status = "cross_mode_transfer_not_supported"
    else:
        status = "official_historical_patch_delta_only"

    applicable = status == "official_historical_patch_delta_only"
    return {
        "mechanic": mechanic,
        "activity": activity,
        "status": status,
        "unit": unit,
        "historical_previous": previous if applicable else None,
        "historical_post_patch": after if applicable else None,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_not_measured",
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "total_ammo_meter_progress": None,
        "guidance_energy_per_precision_hit": None,
        "frost_armor_generation_rate": None,
        "current_weapon_hash_verified": False,
        "current_artifact_selection_verified": False,
        "enhanced_perk_legality_verified": False,
        "gameplay_measured": False,
        "boss_dps": None,
        "guardian_ttk": None,
        "damage_ownership": None,
    }
