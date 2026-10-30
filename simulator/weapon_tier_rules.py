"""Conservative Monument of Triumph weapon tier-upgrade evidence gates.

Official 2026-06-09 Bungie announcement:
https://www.bungie.net/7/en/News/Article/monument_of_triumph_is_live

Tier upgrades cannot add perks to weapon columns. This module does not
certify any particular weapon's enhanced perks, live inventory, or costs.
"""

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/monument_of_triumph_is_live"


def assess_tier_upgrade(*, crafted_legendary, integrated_gear_tiering,
                        owned_perk_hashes, desired_perk_hashes):
    """Check what a tier upgrade can and cannot establish.

    'owned_perk_hashes' means perks already present on a particular instance,
    not its manifest-wide possible perk pool. Crafting-table reshaping,
    drop acquisition, and live instance verification are separate operations.
    """
    if type(crafted_legendary) is not bool or type(integrated_gear_tiering) is not bool:
        raise ValueError("Eligibility indicators must be explicit booleans")

    def valid_hashes(values, field):
        if not isinstance(values, (list, tuple, set)):
            raise ValueError(f"{field} must be a collection of positive plug hashes")
        if any(type(h) is not int or h <= 0 for h in values):
            raise ValueError(f"{field} contains an invalid plug hash")
        return set(values)

    owned = valid_hashes(owned_perk_hashes, "owned_perk_hashes")
    desired = valid_hashes(desired_perk_hashes, "desired_perk_hashes")
    missing = sorted(desired - owned)
    return {
        "upgrade_path": ("documented_for_category"
                         if crafted_legendary or integrated_gear_tiering
                         else "not_established"),
        "desired_perks_absent_from_instance": missing,
        "tier_upgrade_can_add_missing_perks": False,
        "tier_upgrade_alone_cannot_supply_desired_roll": bool(missing),
        "enhanced_perk_legality": "unverified",
        "current_obtainability": "unverified",
        "live_instance_verified": False,
        "source": SOURCE_URL,
        "interpretation": (
            "Tier upgrading cannot add perks to existing columns. A documented "
            "upgrade path does not prove this weapon instance, its enhanced perk "
            "options, or its acquisition. Crafted weapon reshaping is separate."
        ),
    }
