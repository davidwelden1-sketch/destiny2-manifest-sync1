"""Source-gated 9.7.0 defense and PvP opening-charge evidence for VAELTRION.

This is a patch-evidence index, not a live build certification. The published
Frost Armor values are approximate PvE anchors; do not interpolate stacks,
apply them to PvP, or combine them with other buffs without measured evidence.
"""
from datetime import date
from math import isfinite

PATCH = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
REVIEWED_UTC = "2026-11-02"
RULES = frozenset(("frost_armor", "no_backup_plans", "smoke_jumper", "pvp_multicharge"))
MODES = frozenset(("pve", "pvp", "competitive", "trials"))
CLASSES = frozenset(("hunter", "titan", "warlock"))
EVENTS = frozenset(("frost_armor_active", "shotgun_final_blow", "melee_final_blow",
                    "set_bonus_active", "match_start", "other"))
DEFENSIVE_BUFFS = frozenset(("void_overshield", "restoration", "amplified",
                             "frost_armor", "woven_mail"))


def assess_defense_970(*, mechanic, guardian_class, activity, observation_date,
                       event_kind, frost_stacks=None, whisper_of_rime=False,
                       active_defensive_buff=None, ability_max_charges=None,
                       manifest_version=None, artifact_name=None, artifact_perks=()):
    """Evaluate only source-stated eligibility, preserving all gameplay unknowns."""
    if mechanic not in RULES or guardian_class not in CLASSES:
        raise ValueError("Unknown mechanic or class")
    if activity not in MODES or event_kind not in EVENTS:
        raise ValueError("Unknown activity or event")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    if frost_stacks is not None and (type(frost_stacks) is not int or not 0 <= frost_stacks <= 7):
        raise ValueError("Invalid Frost Armor stack count")
    if type(whisper_of_rime) is not bool:
        raise ValueError("Whisper of Rime must be boolean")
    if active_defensive_buff is not None and active_defensive_buff not in DEFENSIVE_BUFFS:
        raise ValueError("Unknown defensive buff")
    if ability_max_charges is not None and (type(ability_max_charges) is not int or
                                            ability_max_charges < 1):
        raise ValueError("Invalid maximum ability charges")
    if manifest_version is not None and (type(manifest_version) is not str or
                                         not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if artifact_name is not None and (type(artifact_name) is not str or
                                      not artifact_name.strip()):
        raise ValueError("Invalid Artifact name")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require one named Artifact")

    postpatch = observed >= PATCH_DATE
    supported = False
    pve_dr_approx = None
    source_dr_cap = None
    start_charges = None
    note = ""
    if mechanic == "frost_armor":
        supported = (event_kind == "frost_armor_active" and frost_stacks is not None
                     and frost_stacks > 0 and (frost_stacks <= 5 or whisper_of_rime))
        # Only two anchors were explicitly published. Neither is a measured PvP value.
        if supported and activity == "pve":
            if frost_stacks == 5:
                pve_dr_approx = 0.35
            elif frost_stacks == 7 and whisper_of_rime:
                pve_dr_approx = 0.50
        note = "Stacks now expire one at a time; 5 stacks about 35% DR; Rime caps at 7 and 50%."
    elif mechanic == "no_backup_plans":
        supported = (guardian_class == "titan" and
                     event_kind in ("shotgun_final_blow", "melee_final_blow") and
                     active_defensive_buff is not None)
        note = ("Shotgun/melee final blows start health regeneration and extend an existing "
                "listed defensive buff; do not infer a newly granted Void Overshield.")
    elif mechanic == "smoke_jumper":
        supported = event_kind == "set_bonus_active"
        if supported and activity == "pve":
            source_dr_cap = 0.40
        note = "Two-piece Ride Together, Die Together maximum DR reduced from 50% to 40%."
    else:
        supported = (activity in ("pvp", "competitive", "trials") and
                     event_kind == "match_start" and
                     ability_max_charges is not None and ability_max_charges > 1)
        if supported:
            start_charges = 1
        note = "Multi-charge abilities start PvP matches with one charge, not all charges."

    supported = bool(postpatch and supported)
    if not supported:
        pve_dr_approx = None
        source_dr_cap = None
        start_charges = None
    # This EHP multiplier applies to a single approximate published DR anchor,
    # not a live build, and never includes an overshield or other stacked effects.
    ehp_single = (1.0 / (1.0 - pve_dr_approx)) if pve_dr_approx is not None else None
    return {
        "id": f"d2:patch-rule:970:defense:{mechanic}",
        "mechanic": mechanic, "guardian_class": guardian_class, "activity": activity,
        "event_kind": event_kind, "observation_date": observation_date,
        "patch_version": PATCH, "patch_date": PATCH_DATE.isoformat(),
        "source_url": SOURCE, "source_checked_at": REVIEWED_UTC,
        "manifest_version": manifest_version,
        "evidence_grade": ("official_historical_patch_not_live_measured" if postpatch
                           else "pre_patch_unverified"),
        "source_supported_candidate": supported,
        "published_pve_dr_approx": pve_dr_approx,
        "published_pve_max_dr_cap": source_dr_cap,
        "illustrative_single_source_ehp_multiplier": ehp_single,
        "published_pvp_match_start_charges": start_charges,
        "source_note": note,
        "frost_stacks": frost_stacks, "whisper_of_rime": whisper_of_rime,
        "active_defensive_buff": active_defensive_buff,
        "ability_max_charges": ability_max_charges,
        "artifact_name": artifact_name, "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "current_artifact_allocation_verified": False,
        "exact_weapon_hash_and_roll_verified": False,
        "armor_set_ownership_verified": False,
        "live_runtime_activation_verified": False,
        "pve_stacking_with_other_sources_verified": False,
        "measured_pve_boss_dps": None, "measured_pve_damage_resistance": None,
        "measured_pvp_guardian_damage": None, "measured_pvp_ttk": None,
        "measured_cooldown_or_buff_uptime": None,
        "certified_for_app_build_recommendation": False,
    }
