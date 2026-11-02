"""Conservative synthetic 9.7.0 Exotic activation checks; NOT gameplay measurements.
Official source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0 (2026-06-09).
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = date(2026, 6, 9)
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))

def _review_date(value):
    if type(value) is not str:
        raise ValueError("ISO observation date required")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if parsed.isoformat() != value:
        raise ValueError("Canonical ISO observation date required")
    return parsed

def review_tarrabah(*, activity, observation_date, target_scorched, registered_damage, final_blow=False):
    """Historical PvE eligibility only. 33% is increased *meter progress*, not damage."""
    if activity not in ACTIVITIES or type(activity) is not str:
        raise ValueError("Explicit activity required")
    when = _review_date(observation_date)
    if any(type(x) is not bool for x in (target_scorched, registered_damage, final_blow)):
        raise ValueError("Boolean flags required")
    eligible = activity == "pve" and when > PATCH_DATE and target_scorched and registered_damage
    return {
        "weapon": "Tarrabah", "source_url": SOURCE_URL, "patch_version": "9.7.0",
        "observation_date": observation_date, "evidence": "official_historical",
        "scorched_combatant_meter_progress_bonus_percent": 33 if activity == "pve" else None,
        "kill_meter_progress_percent": 10 if activity == "pve" else None,
        "historical_scorch_condition_candidate": eligible if when > PATCH_DATE else None,
        "pvp_guardian_activation_verified": False, "runtime_activation_verified": False,
        "scorch_ownership_verified": False, "pve_boss_dps_measured": None,
        "pvp_guardian_ttk_measured": None, "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "certified_for_app_build_recommendation": False
    }

def jade_rabbit_transition(*, activity, observation_date, stacks, event, catalyst_active=False):
    """Patch-described one-event stack arithmetic, not observed damage/proc behavior."""
    if activity not in ACTIVITIES or type(activity) is not str:
        raise ValueError("Explicit activity required")
    when = _review_date(observation_date)
    if type(stacks) is not int or not 0 <= stacks <= 15:
        raise ValueError("Stacks must be integer 0..15")
    if type(catalyst_active) is not bool:
        raise ValueError("Catalyst flag must be bool")
    if event not in ("precision_kill", "direct_body_damage", "reload", "firefly_splash", "special_reload"):
        raise ValueError("Unsupported event")
    if when <= PATCH_DATE:
        next_stacks = None
    elif event == "precision_kill":
        next_stacks = min(15, stacks + 1)
    elif event == "direct_body_damage":
        next_stacks = max(0, stacks - 1)
    elif event == "special_reload" and catalyst_active:
        next_stacks = 0
    else:
        next_stacks = stacks
    return {
        "weapon": "Jade Rabbit", "source_url": SOURCE_URL, "patch_version": "9.7.0",
        "evidence": "official_historical", "observation_date": observation_date,
        "historical_next_stacks": next_stacks,
        "historical_micro_missile_candidate": (event == "special_reload" and catalyst_active and stacks > 0) if when > PATCH_DATE else None,
        "magazine_refill_candidate": event == "precision_kill" if when > PATCH_DATE else None,
        "firefly_splash_preserves_stacks": event == "firefly_splash" if when > PATCH_DATE else None,
        "runtime_activation_verified": False, "measured_micro_missile_damage": None,
        "measured_firefly_damage": None, "pvp_guardian_ttk_measured": None,
        "pve_boss_dps_measured": None,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "certified_for_app_build_recommendation": False
    }
