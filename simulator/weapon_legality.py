"""Conservative exact-hash weapon socket membership checks.

Manifest socket membership alone does not establish obtainable rolls,
active intrinsic frames, or enhanced perk availability.
"""

def check_socket_membership(item_hash, socket_index, plug_hash, inventory):
    """Check a single item's explicit socket index, never merge names/variants."""
    if not all(type(x) is int and x >= 0 for x in (item_hash, socket_index, plug_hash)):
        raise ValueError("hashes and socket index must be nonnegative integers")
    if not isinstance(inventory, dict):
        raise TypeError("inventory must be a mapping")
    item = inventory.get(item_hash)
    if item is None:
        return {"possible": False, "reason": "item_hash_absent", "certified_roll": False}
    if not isinstance(item, dict):
        return {"possible": False, "reason": "malformed_item", "certified_roll": False}
    sockets = item.get("sockets", {})
    if not isinstance(sockets, dict):
        return {"possible": False, "reason": "malformed_sockets", "certified_roll": False}
    plugs = sockets.get(socket_index, ())
    if not isinstance(plugs, (list, tuple, set, frozenset)):
        return {"possible": False, "reason": "malformed_socket_plugs", "certified_roll": False}
    present = plug_hash in plugs
    return {"possible": present, "reason": "manifest_membership_only" if present else "plug_not_in_socket",
            "certified_roll": False}

def check_pair(item_hash, left_index, left_plug, right_index, right_plug, inventory):
    if left_index == right_index:
        return {"possible": False, "reason": "same_socket", "certified_roll": False}
    a = check_socket_membership(item_hash, left_index, left_plug, inventory)
    b = check_socket_membership(item_hash, right_index, right_plug, inventory)
    return {"possible": a["possible"] and b["possible"],
            "reason": "same_hash_socket_membership_not_obtainability" if a["possible"] and b["possible"] else "membership_failed",
            "certified_roll": False}
