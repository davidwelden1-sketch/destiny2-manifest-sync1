"""Historical 9.7.0 Anarchy and Divinity changes, never current DPS/TTK.

Bungie: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published 2026-06-09. Name-level patch evidence only, not exact item hashes,
obtainable rolls, current Artifact allocations, or measured gameplay.
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = date(2026, 6, 9)
PATCH_VERSION = "9.7.0"
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
BASELINES = frozenset(("pre_9_7_0", "post_9_7_0", "unknown"))
# Values are historical old -> new, or a multiplier relative to the old value.
RULES = {
    "anarchy": {
        "armed_trap_lifetime_seconds": (10, 15),
        "trap_damage_vs_combatants_factor": (1.0, 1.30),
        "detonation_damage_vs_combatants_factor": (1.0, 2.0),
        "trait_replacement": ("Moving Target", "Impromptu Ammunition"),
    },
    "divinity": {
        "penance_damage_factor": (1.0, 1.20),
        "penance_activation_seconds": (4, 3),
        "cage_activation_shots": (14, 10),
    },
}
DAMAGE_KEYS = frozenset((
    "trap_damage_vs_combatants_factor",
    "detonation_damage_vs_combatants_factor",
    "penance_damage_factor",
))


def audit_exotic_mechanic(*, weapon, mechanic, activity, observation_date,
                          source_patch_version=PATCH_VERSION,
                          reference_baseline="pre_9_7_0"):
    """Expose only dated named-weapon patch deltas, not current simulation.

    A PvP or post-patch observation cannot reuse the pre-patch change as
    an absolute scalar. Patch-day deployment timing is not known.
    """
    if not isinstance(weapon, str) or not isinstance(mechanic, str):
        raise ValueError("weapon and mechanic must be strings")
    weapon = weapon.strip().casefold()
    mechanic = mechanic.strip()
    if weapon not in RULES or mechanic not in RULES[weapon]:
        raise ValueError("unknown named weapon or mechanic")
    if activity not in ACTIVITIES:
        raise ValueError("unsupported activity")
    if reference_baseline not in BASELINES:
        raise ValueError("unsupported reference baseline")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be ISO date")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("noncanonical observation_date")

    status = "historical_named_weapon_patch_delta_only"
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif activity != "pve":
        status = "pvp_application_not_established"
    elif reference_baseline != "pre_9_7_0":
        status = "not_a_pre_patch_reference"

    applicable = status == "historical_named_weapon_patch_delta_only"
    old, new = RULES[weapon][mechanic]
    return {
        "status": status,
        "weapon": weapon.title(),
        "mechanic": mechanic,
        "activity": activity,
        "artifact_enabled": False if activity in {"competitive", "trials"} else None,
        "source_url": SOURCE_URL,
        "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_named_weapon_patch",
        "reference_baseline": reference_baseline,
        "historical_previous": old if applicable else None,
        "historical_post_patch": new if applicable else None,
        "historical_relative_factor": new if applicable and mechanic in DAMAGE_KEYS else None,
        "exact_item_hash_verified": False,
        "current_roll_certified": False,
        "current_artifact_selection_verified": False,
        "current_game_verified": False,
        "gameplay_measured": False,
        "damage_ownership_measured": False,
        "boss_dps": None,
        "guardian_ttk": None,
        "damage_per_tick": None,
        "tick_frequency": None,
    }
