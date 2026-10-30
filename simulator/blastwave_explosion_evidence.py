"""Evidence gate for Blastwave Striders explosive-perk event attribution.

Bungie Update 9.7.0 (2026-06-09) distinguishes explosions made by
on-kill perks (Firefly, Dragonfly) from passive explosive perks
(Explosive Payload, Explosive Head). The former no longer trigger the
Blastwave Striders blast; the latter still can. This does NOT imply
that an arbitrary explosion activates the Exotic: charge, ability,
self-damage, Shiver Strike, mode, and trigger timing remain unmeasured.

Official: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
"""

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
REVIEWED_DATE = "2026-10-30"

_ON_KILL_EXCLUDED = {"firefly", "dragonfly"}
_PASSIVE_NOT_EXCLUDED = {"explosive payload", "explosive head"}
_KNOWN_ACTIVITIES = {"pve", "pvp"}
_KNOWN_EVENTS = {"on_kill_explosion", "passive_explosion"}


def blastwave_explosion_gate(*, exotic_equipped, perk_name, event_kind,
                             activity, weapon_item_hash=None):
    """Classify only the *published exclusion gate*, not activation or DPS.

    This function is intentionally conservative: it does not prove a
    perk roll is obtainable, an explosion damages the user, an Exotic
    charge is ready, or that the behavior was measured in either mode.
    """
    if exotic_equipped is not None and type(exotic_equipped) is not bool:
        raise ValueError("exotic_equipped must be bool or None")
    if perk_name is not None and (
            not isinstance(perk_name, str) or not perk_name.strip()):
        raise ValueError("perk_name must be nonempty text or None")
    if event_kind is not None and event_kind not in _KNOWN_EVENTS:
        raise ValueError("event_kind must identify the explosion mechanism")
    if activity is not None and activity not in _KNOWN_ACTIVITIES:
        raise ValueError("activity must be pve, pvp, or None")
    if weapon_item_hash is not None and (
            type(weapon_item_hash) is not int or weapon_item_hash <= 0):
        raise ValueError("weapon_item_hash must be positive integer or None")

    perk = perk_name.strip().casefold() if perk_name is not None else None
    if exotic_equipped is False:
        gate = "exotic_not_equipped"
    elif exotic_equipped is None or perk is None or event_kind is None or activity is None:
        gate = "insufficient_inputs"
    elif perk in _ON_KILL_EXCLUDED and event_kind == "on_kill_explosion":
        gate = "officially_excluded_from_blast_trigger"
    elif perk in _PASSIVE_NOT_EXCLUDED and event_kind == "passive_explosion":
        gate = "officially_not_excluded_activation_unverified"
    else:
        gate = "source_event_pair_not_classified"

    return {
        "gate": gate,
        "weapon_item_hash": weapon_item_hash,
        "perk_name": perk_name,
        "event_kind": event_kind,
        "activity": activity,
        "source_url": SOURCE_URL,
        "source_date": SOURCE_DATE,
        "reviewed_date": REVIEWED_DATE,
        "evidence_grade": "official_patch_text_not_gameplay_measurement",
        "trigger_certified": False,
        "weapon_roll_legality_certified": False,
        "enhanced_perk_legality_certified": False,
        "artifact_selection_certified": False,
        "explosion_damage": None,
        "self_damage": None,
        "charge_threshold": None,
        "kill_attribution": None,
        "pve_boss_dps": None,
        "pvp_ttk": None,
    }
