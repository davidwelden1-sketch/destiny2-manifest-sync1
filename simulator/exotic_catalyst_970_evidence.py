"""Bungie 9.7.0 Exotic catalyst trait changes, not random Legendary rolls.

Official 2026-06-09 patch:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
This catalog records *historical patch statements* only. It cannot prove a
catalyst is currently installed, unlocked, active, enhanced, or measured.
"""

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
PATCH_VERSION = "9.7.0"

# Only explicitly named *catalyst* traits in Bungie's 9.7.0 notes.
# Do not merge with random-roll socket columns or non-catalyst weapon changes.
_CATALYST_CHANGES = {
    "crimson": {"added": ("To the Pain",)},
    "coldheart": {"added": ("Supercharged Magazine",)},
    "merciless": {"added": ("Heal Clip",)},
    "sunshot": {"added": ("Loose Change",)},
    "skyburner's oath": {"added": ("Incandescent", "Burning Ambition")},
    "riskrunner": {"added": ("Chain Reaction",)},
    "the prospector": {"added": ("Danger Zone",)},
    "borealis": {"added": ("Shield Disorient",)},
    "touch of malice": {"added": ("Precision Instrument",), "removed": ("Rapid Hit",)},
    "heirloom": {"added": ("Incandescent",)},
    # Bungie explicitly redacted Hard Light's catalyst trait name.
    "hard light": {"redacted": True},
}


def screen_exotic_catalyst_trait(weapon, trait, *, activity, enhanced=False,
                                 source_patch_version=PATCH_VERSION):
    """Return fail-closed patch evidence for a named Exotic catalyst trait.

    Positive assignment is only official *historical* catalyst membership.
    It never implies that the Exotic has a Legendary random-perk socket,
    the player owns the catalyst, or that the trait activates in an activity.
    """
    if not isinstance(weapon, str) or not weapon.strip():
        raise ValueError("weapon must be a nonempty name")
    if not isinstance(trait, str) or not trait.strip():
        raise ValueError("trait must be a nonempty name")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("activity must be explicit")
    if type(enhanced) is not bool:
        raise ValueError("enhanced must be boolean")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    name = weapon.strip().casefold()
    perk = trait.strip().casefold()
    base = {
        "weapon": weapon.strip(), "trait": trait.strip(), "activity": activity,
        "source_url": SOURCE_URL, "source_date": SOURCE_DATE,
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_catalyst_assignment",
        "socket_kind": "exotic_catalyst_not_randomized_legendary_trait_column",
        "current_catalyst_equipped_verified": False,
        "current_catalyst_acquisition_verified": False,
        "current_game_verified": False,
        "enhanced_roll_certified": False,
        "gameplay_measured": False,
        "artifact_legality_certified": False,
        "pve_boss_dps": None, "pvp_guardian_ttk": None,
        "damage_multiplier": None, "kill_attribution": None,
        "perk_activation": None, "perk_uptime": None,
    }
    if source_patch_version.strip() != PATCH_VERSION:
        return {**base, "status": "source_patch_version_mismatch"}
    if enhanced:
        return {**base, "status": "enhanced_catalyst_trait_not_sourced"}
    change = _CATALYST_CHANGES.get(name)
    if change is None:
        return {**base, "status": "weapon_not_in_this_catalyst_patch_index"}
    if change.get("redacted"):
        return {**base, "status": "official_catalyst_trait_name_redacted"}
    if perk in (x.casefold() for x in change.get("added", ())):
        return {**base, "status": "official_historical_catalyst_trait_added"}
    if perk in (x.casefold() for x in change.get("removed", ())):
        return {**base, "status": "official_historical_catalyst_trait_replaced"}
    return {**base, "status": "trait_not_listed_for_weapon_in_patch"}
