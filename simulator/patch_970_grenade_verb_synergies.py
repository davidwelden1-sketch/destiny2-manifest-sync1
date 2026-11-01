"""Official 9.7.0 nonstandard grenade activation and native debuff corrections.

Bungie 2026-06-09: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Historical patch-note evidence only. No observed proc, weapon roll, kill credit,
Guardian TTK, or boss DPS is implied by these corrections.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 9)
PATCH_VERSION = "9.7.0"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
TRIGGERS = {
    "adrenaline_junkie_nonstandard_grenade": frozenset(("hellion", "grapple_melee")),
    "bombardiers_native_debuff": frozenset(("arc_blind", "void_suppress")),
}
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
CLASSES = frozenset(("hunter", "titan", "warlock"))


def review_verb_activation(*, event, trigger, class_name, activity,
                           observation_date, source_patch_version=PATCH_VERSION):
    """Scope one official correction without certifying in-game activation."""
    if type(event) is not str or event not in TRIGGERS:
        raise ValueError("Unknown official correction")
    if type(trigger) is not str or trigger not in TRIGGERS[event]:
        raise ValueError("Trigger not established by this correction")
    if type(class_name) is not str or class_name not in CLASSES:
        raise ValueError("Unknown class")
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Unknown activity")
    if type(source_patch_version) is not str or not source_patch_version.strip():
        raise ValueError("Source patch version required")
    if type(observation_date) is not str:
        raise ValueError("Observation date must be canonical ISO")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Observation date must be canonical ISO")

    # Hellion is a Warlock Aspect; the cited correction does not make it
    # equippable on Hunter/Titan. Bombardiers are Hunter Exotic armor.
    class_supported = (
        (event == "bombardiers_native_debuff" and class_name == "hunter")
        or (event == "adrenaline_junkie_nonstandard_grenade"
            and (trigger == "grapple_melee" or class_name == "warlock"))
    )
    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif not class_supported:
        status = "class_trigger_scope_not_established"
    elif day < PATCH_DATE:
        status = "pre_fix_observation_requires_revalidation"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "official_historical_fix_not_gameplay_measurement"

    bombardiers = event == "bombardiers_native_debuff"
    return {
        "event": event, "trigger": trigger, "class_name": class_name,
        "activity": activity, "status": status,
        "source_url": SOURCE_URL, "source_date": PATCH_DATE.isoformat(),
        "source_patch_version": PATCH_VERSION,
        "official_correction": (
            "Adrenaline Junkie activation failure for non-standard grenade "
            "abilities such as Hellion or grapple melee was fixed"
            if not bombardiers else
            "The Bombardiers custom blind and suppress effects were replaced "
            "with Arc Blind and Void Suppress"
        ),
        "pve_arc_blind_seconds_official": (
            10 if bombardiers and trigger == "arc_blind" and activity == "pve"
            and class_supported else None
        ),
        "pve_void_suppress_seconds_official": (
            10 if bombardiers and trigger == "void_suppress" and activity == "pve"
            and class_supported else None
        ),
        "pvp_debuff_duration_seconds": None,
        "current_weapon_hash": None,
        "current_enhanced_perk_legality": "unverified",
        "current_artifact_allocation_verified": False,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "trigger_activation_measured": False,
        "damage_ownership": None,
        "kill_attribution": None,
        "cooldown_seconds": None,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "evidence_grade": "official_historical_patch_note_only",
    }
