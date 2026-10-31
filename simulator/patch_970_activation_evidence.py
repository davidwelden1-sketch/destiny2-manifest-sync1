"""Official 9.7.0 weapon activation / attribution corrections, not measured procs.

Bungie 2026-06-09: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Manifest membership, current acquisition, enhanced variants, damage ownership,
and Guardian/boss coefficients require independent evidence. Never promote a
historical bug fix into a certified present-day gameplay interaction.
"""
from datetime import date

PATCH_DATE = "2026-06-09"
PATCH_VERSION = "9.7.0"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"

# Event labels describe the *specific bug fix*, not an exhaustive proc list.
CORRECTIONS = {
    "paracausal_fluid_sword_activation": {
        "event": "sword_activation", "class": None, "weapon": None,
        "fact": "Paracausal Fluid failing to activate on Swords was fixed.",
        "scope": "weapon_perk_activation",
    },
    "paracausal_fluid_high_health_activation": {
        "event": "high_health_target_activation", "class": None, "weapon": None,
        "fact": "Paracausal Fluid sometimes failing on sufficiently high-health enemies was fixed.",
        "scope": "weapon_perk_activation",
    },
    "paracausal_fluid_hud_stack": {
        "event": "hud_x2_display", "class": None, "weapon": None,
        "fact": "Paracausal Fluid could display x2 although multiple stacks gave no extra benefit.",
        "scope": "hud_not_damage_stacking",
    },
    "aggregate_charge_hunter_tether": {
        "event": "tether_only_debuff", "class": "hunter", "weapon": None,
        "fact": "Hunter tether previously failed to activate Aggregate Charge unless another debuff was present.",
        "scope": "weapon_perk_debuff_activation",
    },
    "cusp_sempiternal_withering_gaze": {
        "event": "aim_released_before_projectile_impact", "class": None,
        "weapon": "cusp sempiternal",
        "fact": "Withering Gaze on Cusp Sempiternal previously required aiming at projectile impact to weaken.",
        "scope": "named_weapon_debuff_activation",
    },
    "merciless_banner_shield": {
        "event": "fire_through_banner_shield", "class": None,
        "weapon": "merciless",
        "fact": "Merciless previously failed to gain Conserve Momentum stacks when firing through a Banner Shield.",
        "scope": "named_weapon_buff_activation",
    },
    "monte_carlo_bayonet": {
        "event": "bayonet_kill_ammo_meter", "class": None,
        "weapon": "monte carlo",
        "fact": "Monte Carlo bayonet kills previously failed to grant ammo meter progress.",
        "scope": "kill_attribution_ammo_meter",
    },
}


def _canonical_day(value):
    if not isinstance(value, str):
        raise ValueError("observation_date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if parsed.isoformat() != value:
        raise ValueError("observation_date must be canonical YYYY-MM-DD")
    return parsed


def audit_weapon_activation(change_key, observation_date, *, activity, event,
                            class_name=None, weapon_name=None,
                            source_patch_version=PATCH_VERSION):
    """Return a conservative historical patch revalidation screen.

    Matching an event is not evidence it actually activated in-game.
    PvE and PvP are separate experiments even when a patch note names neither.
    """
    if change_key not in CORRECTIONS:
        raise ValueError("Unknown activation correction")
    observed = _canonical_day(observation_date)
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("Unknown activity")
    if class_name not in (None, "hunter", "titan", "warlock"):
        raise ValueError("Unknown class")
    if not isinstance(event, str) or not event.strip():
        raise ValueError("event must be nonempty")
    if weapon_name is not None and (
        not isinstance(weapon_name, str) or not weapon_name.strip()
    ):
        raise ValueError("weapon_name must be nonempty when supplied")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")

    correction = CORRECTIONS[change_key]
    actual_weapon = weapon_name.strip().casefold() if weapon_name else None
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif event != correction["event"]:
        status = "event_scope_not_established"
    elif correction["class"] is not None and class_name != correction["class"]:
        status = "class_scope_not_established"
    elif correction["weapon"] is not None and actual_weapon != correction["weapon"]:
        status = "weapon_identity_not_established"
    elif observed < date.fromisoformat(PATCH_DATE):
        status = "pre_fix_observation_requires_revalidation"
    elif observation_date == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "post_fix_not_gameplay_certification"
    return {
        "change_key": change_key,
        "official_fact": correction["fact"],
        "scope": correction["scope"],
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE,
        "source_patch_version": PATCH_VERSION,
        "activity": activity,
        "event": event,
        "class_name": class_name,
        "weapon_name": weapon_name,
        "status": status,
        "revalidation_required": status in (
            "pre_fix_observation_requires_revalidation",
            "patch_day_deployment_time_unknown",
        ),
        "artifact_enabled": False if activity in ("competitive", "trials") else None,
        "current_weapon_hash_verified": False,
        "current_roll_or_enhancement_verified": False,
        "damage_ownership": None,
        "buff_stacks_verified": False,
        "activation_measured": False,
        "pve_boss_dps": None,
        "pve_damage_resistance": None,
        "pvp_guardian_ttk": None,
        "evidence_grade": "official_historical_patch_note_only",
    }
