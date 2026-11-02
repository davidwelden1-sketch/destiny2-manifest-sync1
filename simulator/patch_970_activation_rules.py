"""Historical activation evidence only, not measured gameplay or perk legality.

Bungie 9.7.0 (2026-06-09):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
"""
from datetime import date

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def historical_attrition_hits(*, weapon_type, frame):
    """Return only Bungie's two explicit frame/type thresholds; None otherwise.

    The returned count represents registered hits, not rounds fired or kills.
    """
    if type(weapon_type) is not str or type(frame) is not str:
        raise ValueError("Explicit weapon type and frame required")
    if weapon_type == "Grenade Launcher" and frame == "Wave Frame":
        return 4
    if weapon_type == "Rocket Launcher":
        return 3
    return None


def review_activation(*, perk, activity, observation_date, weapon_type=None,
                      frame=None, registered_hits=None,
                      precision_final_blow=False, rapid_final_blows=None,
                      reloaded=False, manifest_version=None):
    """Synthetic patch-condition review; never claims an in-game activation.

    'rapid_final_blows' must be independently verified as rapid by the caller.
    The patch does not specify the time window.
    """
    if perk not in ("Attrition Orbs", "Desperado") or type(perk) is not str:
        raise ValueError("Unsupported perk")
    if activity not in ACTIVITIES or type(activity) is not str:
        raise ValueError("Explicit activity required")
    if type(observation_date) is not str:
        raise ValueError("ISO date required")
    try:
        d = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if d.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    if d < PATCH_DATE:
        status = "pre_patch_observation"
    elif d == PATCH_DATE:
        status = "patch_day_activation_time_unknown"
    else:
        status = "historical_patch_condition_only"
    if manifest_version is not None and (type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if type(precision_final_blow) is not bool or type(reloaded) is not bool:
        raise ValueError("Booleans required for kill/reload flags")
    if registered_hits is not None and (type(registered_hits) is not int or registered_hits < 0):
        raise ValueError("Registered hits must be nonnegative integer")
    if rapid_final_blows is not None and (type(rapid_final_blows) is not int or rapid_final_blows < 0):
        raise ValueError("Rapid final blows must be nonnegative integer")
    if perk == "Attrition Orbs":
        if type(weapon_type) is not str or type(frame) is not str:
            raise ValueError("Frame/type required for Attrition Orbs")
        if precision_final_blow or rapid_final_blows is not None or reloaded:
            raise ValueError("Desperado-only fields on Attrition Orbs")
        threshold = historical_attrition_hits(weapon_type=weapon_type, frame=frame)
        candidate = threshold is not None and registered_hits is not None and registered_hits >= threshold
    else:
        if weapon_type is not None or frame is not None or registered_hits is not None:
            raise ValueError("Attrition-only fields on Desperado")
        threshold = None
        candidate = reloaded and (precision_final_blow or (rapid_final_blows is not None and rapid_final_blows >= 3))
    return {
        "id": "d2:patch-rule:970:" + ("attrition-frame-hits" if perk == "Attrition Orbs" else "desperado-reload"),
        "perk": perk, "activity": activity, "observation_date": observation_date,
        "source_url": SOURCE_URL, "source_published_at": PATCH_DATE.isoformat(),
        "reviewed_at": "2026-11-02", "patch_version": PATCH_VERSION,
        "manifest_version": manifest_version, "evidence": "official_historical",
        "status": status, "historical_hit_threshold": threshold,
        "historical_condition_candidate": candidate if status == "historical_patch_condition_only" else None,
        "hits_are_not_shots": True if perk == "Attrition Orbs" else None,
        "rapid_kill_window_measured": None,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "perk_pool_verified": False, "enhanced_perk_legality_verified": False,
        "weapon_hash_verified": False, "runtime_activation_verified": False,
        "pve_boss_dps_measured": None, "pve_damage_resistance_measured": None,
        "pvp_guardian_ttk_measured": None, "ability_cooldown_measured": None,
        "certified_for_app_build_recommendation": False,
    }
