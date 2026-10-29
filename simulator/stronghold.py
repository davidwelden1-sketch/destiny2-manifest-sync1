"""Stronghold infinite-guard *eligibility* gate, not a guard/DR simulator.

Bungie Destiny 2 update 9.7.0 (2026-06-09): Stronghold's infinite guard
capability only works on Heavy-ammo swords. A Heavy sword is eligible, not
proof that a particular live instance is guarding or that DR is known.
Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
"""


def stronghold_infinite_guard_eligibility(is_sword, ammo_type):
    """Bungie ammo enum: 1 primary, 2 special, 3 heavy, 0/4 unknown."""
    if type(is_sword) is not bool:
        raise ValueError("is_sword must be an explicit boolean")
    if type(ammo_type) is not int or ammo_type not in (0, 1, 2, 3, 4):
        raise ValueError("ammo_type must be a Bungie ammunition enum integer")
    if not is_sword:
        return {"eligible": False, "reason": "not_a_sword",
                "active_guard": "unverified", "damage_resistance": "unverified"}
    if ammo_type == 3:
        return {"eligible": True, "reason": "heavy_ammo_sword",
                "active_guard": "unverified", "damage_resistance": "unverified"}
    if ammo_type in (1, 2):
        return {"eligible": False, "reason": "not_heavy_ammo_sword",
                "active_guard": "unverified", "damage_resistance": "unverified"}
    return {"eligible": None, "reason": "unknown_ammo_type",
            "active_guard": "unverified", "damage_resistance": "unverified"}
