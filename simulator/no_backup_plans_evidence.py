"""9.7.0 No Backup Plans shotgun/melee final-blow evidence, NOT gameplay measurements.

Bungie 2026-06-09: qualifying final blows start health regeneration and
extend timers of existing Void Overshield, Restoration, Amplified, Frost
Armor or Woven Mail. Damage-bonus condition is any listed active buff.
Exact shotgun item hashes, buff duration, healing, DR and damage are unknown.
"""
from simulator.activity_rules import activity_constraints

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
REVIEWED_DATE = "2026-10-31"
DEFENSIVE_BUFFS = frozenset({"void overshield", "restoration", "amplified",
                              "frost armor", "woven mail"})
EVENTS = frozenset({"shotgun_final_blow", "melee_final_blow",
                    "shotgun_hit", "melee_hit", "other_final_blow"})
ACTIVITIES = frozenset({"pve", "pvp", "trials", "trials of osiris",
                        "competitive", "competitive crucible"})


def no_backup_plans_evidence(*, class_name, exotic_equipped, event_kind,
                             active_defensive_buffs, activity, weapon_type=None):
    """Classify published trigger conditions, never certify a playable build."""
    if not isinstance(class_name, str) or not class_name.strip():
        raise ValueError("class_name must be nonempty")
    if exotic_equipped is not None and type(exotic_equipped) is not bool:
        raise ValueError("exotic_equipped must be bool or None")
    if event_kind not in EVENTS:
        raise ValueError("unknown event_kind")
    if not isinstance(activity, str) or activity.strip().casefold() not in ACTIVITIES:
        raise ValueError("unknown activity")
    if weapon_type is not None and (not isinstance(weapon_type, str) or not weapon_type.strip()):
        raise ValueError("weapon_type must be a nonempty string or None")
    if active_defensive_buffs is not None:
        if not isinstance(active_defensive_buffs, (tuple, list, set, frozenset)):
            raise ValueError("active_defensive_buffs must be a collection or None")
        if any(not isinstance(v, str) or not v.strip() for v in active_defensive_buffs):
            raise ValueError("buff names must be nonempty strings")
        active = frozenset(" ".join(v.strip().casefold().split())
                           for v in active_defensive_buffs)
    else:
        active = None
    mode = activity.strip().casefold()
    rules = activity_constraints(mode)
    kind = None if weapon_type is None else " ".join(weapon_type.strip().casefold().split())
    shotgun_event = event_kind.startswith("shotgun_")
    trigger = event_kind in {"shotgun_final_blow", "melee_final_blow"}
    if shotgun_event and kind not in (None, "shotgun"):
        trigger = False
    conditions = {
        "titan": class_name.strip().casefold() == "titan",
        "exotic_equipped": exotic_equipped,
        "trigger_event": trigger,
        "shotgun_type_confirmed": (None if shotgun_event and kind is None
                                   else kind == "shotgun" if shotgun_event else True),
    }
    if False in conditions.values():
        status = "official_trigger_conditions_not_met"
    elif None in conditions.values():
        status = "insufficient_trigger_evidence"
    else:
        status = "official_trigger_conditions_met_not_gameplay_measured"
    eligible = frozenset() if active is None else active & DEFENSIVE_BUFFS
    exotic_active = class_name.strip().casefold() == "titan" and exotic_equipped is True
    damage_condition = (None if active is None or
                        (exotic_equipped is None and class_name.strip().casefold() == "titan")
                        else bool(eligible) and exotic_active)
    qualified = status == "official_trigger_conditions_met_not_gameplay_measured"
    return {
        "status": status, "activity": mode, "artifact_enabled": rules["artifact_enabled"],
        "event_kind": event_kind, "conditions": conditions,
        "published_on": SOURCE_DATE, "reviewed_date": REVIEWED_DATE,
        "source_url": SOURCE_URL,
        "health_regeneration_trigger_described": qualified,
        "listed_active_buffs": sorted(eligible),
        "buff_state": ("unknown_existing_buff_state" if active is None
                       else "listed_defensive_buff_active" if eligible
                       else "no_listed_defensive_buff_active"),
        "buff_timer_extension_described": qualified and bool(eligible),
        "damage_bonus_condition_described": damage_condition,
        "buffs_granted_by_trigger": [],
        "void_overshield_partial_heal_condition": (
            "existing_void_overshield_and_qualifying_final_blow"
            if qualified and "void overshield" in eligible else None),
        "duration_extension_seconds": None, "damage_bonus_multiplier": None,
        "healing_per_second": None, "pve_damage_resistance": None,
        "pve_boss_dps": None, "pvp_ttk": None,
        "exact_shotgun_hash_verified": False,
        "enhanced_perk_roll_verified": False,
        "current_artifact_selection_verified": False,
        "gameplay_measured": False,
        "evidence_grade": "official_historical_patch_text_only",
    }
