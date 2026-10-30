"""Official, event-specific Hierarchy of Needs evidence gates (not measured DPS).

9.7.0 (2026-06-09): seekers apply +15 (+5) Scorch on hit;
submunitions can penetrate combatant shields IF Anti-Barrier is active.
9.7.0.2 (2026-06-23): precision damage to players once again grants
Guidance Energy. These are distinct events, not interchangeable triggers.

Do not assume the parenthetical +5 condition, kill attribution, a
Dawn Chorus ignition bonus, or Guardian damage/Scorch scaling.
"""
from simulator.activity_rules import activity_constraints

SOURCE_970 = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_9702 = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
REVIEWED_DATE = "2026-10-30"
EVENTS = {"seeker_hit", "precision_hit", "seeker_shield_contact"}
TARGETS = {"combatant", "guardian"}
ACTIVITIES = {"pve", "pvp", "trials", "trials of osiris", "competitive", "competitive crucible"}


def hierarchy_event_evidence(*, weapon_name, event_kind, target_kind,
                             activity, anti_barrier_active=None,
                             catalyst_equipped=None):
    """Classify published event rules, never certify a current playable build."""
    if not isinstance(weapon_name, str) or not weapon_name.strip():
        raise ValueError("weapon_name must be nonempty")
    if event_kind not in EVENTS:
        raise ValueError("event_kind must be a recognized weapon event")
    if target_kind not in TARGETS:
        raise ValueError("target_kind must be combatant or guardian")
    if not isinstance(activity, str) or activity.strip().casefold() not in ACTIVITIES:
        raise ValueError("activity must identify a known PvE/PvP playlist")
    for flag in (anti_barrier_active, catalyst_equipped):
        if flag is not None and type(flag) is not bool:
            raise ValueError("flags must be bool or None")
    mode = activity.strip().casefold()
    rules = activity_constraints(mode)
    status = "source_event_not_classified"
    scorch = None
    parenthetical = None
    if weapon_name.strip().casefold() != "hierarchy of needs":
        status = "different_weapon"
    elif mode == "pve" and target_kind == "guardian":
        status = "activity_target_mismatch"
    elif mode != "pve" and target_kind == "combatant":
        status = "activity_target_mismatch"
    elif event_kind == "seeker_hit":
        if target_kind == "combatant":
            status = "official_seeker_scorch_text_not_gameplay_measured"
            scorch, parenthetical = 15, 5
        else:
            status = "official_seeker_scorch_text_guardian_values_unverified"
    elif event_kind == "seeker_shield_contact":
        if target_kind != "combatant":
            status = "guardian_shield_overpenetration_not_established"
        elif anti_barrier_active is True:
            status = "official_conditional_combatant_shield_overpenetration"
        elif anti_barrier_active is False:
            status = "anti_barrier_condition_not_met"
        else:
            status = "anti_barrier_condition_unknown"
    elif event_kind == "precision_hit" and target_kind == "guardian":
        status = "official_pvp_guidance_energy_fix_amount_unverified"
    else:
        status = "precision_hit_amount_unverified"

    return {
        "status": status, "activity": mode, "target_kind": target_kind,
        "event_kind": event_kind, "catalyst_equipped": catalyst_equipped,
        "artifact_enabled": rules["artifact_enabled"],
        "published_seeker_scorch_text": "+15 (+5)" if event_kind == "seeker_hit" else None,
        "combatant_seeker_base_scorch": scorch,
        "parenthetical_bonus_stacks": parenthetical,
        "parenthetical_bonus_condition": None,
        "scorch_source_ownership": None,
        "guidance_energy_amount": None,
        "dawn_chorus_ignition_bonus": None,
        "current_weapon_identity_verified": False,
        "current_artifact_verified": False,
        "gameplay_activation_measured": False,
        "pve_boss_dps": None, "pvp_ttk": None,
        "source_urls": [SOURCE_970, SOURCE_9702],
        "reviewed_date": REVIEWED_DATE,
        "evidence_grade": "official_patch_text_not_gameplay_measurement",
    }
