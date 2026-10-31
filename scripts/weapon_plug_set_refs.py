"""Resolve manifest weapon socket plug-set references without certifying rolls.

Bungie schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Sockets-DestinyPlugSetDefinition.html
A definition's currentlyCanRoll flag is not live acquisition, enhancement,
instance validity, or evidence that plugs in different sockets can co-occur.
"""


def _hash(value, label):
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError(f"{label} must be a uint32")
    return value


def build_weapon_plug_set_reference_index(weapon_socket_refs, plug_sets, item_definitions=None):
    """Join exact item/socket hashes to the same-version plug-set definitions.

    Output includes missing and redacted definitions, and preserves tri-state
    currentlyCanRoll. Optional same-manifest item definitions resolve display
    names without inferring socket purpose, enhancement or playable perk pairs.
    """
    if not isinstance(weapon_socket_refs, list) or not isinstance(plug_sets, dict):
        raise TypeError("weapon socket references must be a list and plug sets a mapping")
    if item_definitions is not None and not isinstance(item_definitions, dict):
        raise TypeError("item definitions must be a mapping or None")
    result = []
    for weapon in weapon_socket_refs:
        if not isinstance(weapon, dict):
            raise ValueError("malformed weapon reference")
        item_hash = _hash(weapon.get("hash"), "item hash")
        sockets = weapon.get("sockets")
        if not isinstance(sockets, list):
            raise ValueError("malformed weapon sockets")
        resolved = []
        for socket in sockets:
            if not isinstance(socket, dict):
                raise ValueError("malformed socket reference")
            position = socket.get("socketIndex")
            if type(position) is not int or position < 0:
                raise ValueError("socketIndex must be a nonnegative integer")
            for field, kind in (("randomizedPlugSetHash", "randomized"),
                                ("reusablePlugSetHash", "reusable")):
                set_hash = socket.get(field)
                if set_hash is None:
                    continue
                _hash(set_hash, field)
                definition = plug_sets.get(str(set_hash))
                if definition is None:
                    resolved.append({"socketIndex": position, "kind": kind,
                                     "plugSetHash": set_hash, "definitionFound": False,
                                     "isFakePlugSet": None, "redacted": None,
                                     "plugs": None})
                    continue
                if not isinstance(definition, dict):
                    raise ValueError("malformed plug set definition")
                items = definition.get("reusablePlugItems") or []
                if not isinstance(items, list):
                    raise ValueError("malformed plug set items")
                plugs = []
                for plug in items:
                    if not isinstance(plug, dict):
                        raise ValueError("malformed plug entry")
                    can_roll = plug.get("currentlyCanRoll")
                    if can_roll is not None and type(can_roll) is not bool:
                        raise ValueError("currentlyCanRoll must be bool or null")
                    plug_hash = _hash(plug.get("plugItemHash"), "plugItemHash")
                    plug_definition = (item_definitions.get(str(plug_hash))
                                       if item_definitions is not None else None)
                    if plug_definition is not None and not isinstance(plug_definition, dict):
                        raise ValueError("malformed plug item definition")
                    display = (plug_definition.get("displayProperties") or {}) if plug_definition else {}
                    if not isinstance(display, dict):
                        raise ValueError("malformed plug display properties")
                    name = display.get("name")
                    if not isinstance(name, str) or not name.strip():
                        name = None
                    plugs.append({"plugItemHash": plug_hash,
                                  "currentlyCanRoll": can_roll,
                                  "plugName": name,
                                  "plugDefinitionFound": plug_definition is not None})
                fake, redacted = definition.get("isFakePlugSet"), definition.get("redacted")
                if any(x is not None and type(x) is not bool for x in (fake, redacted)):
                    raise ValueError("plug-set flags must be bool or null")
                resolved.append({"socketIndex": position, "kind": kind,
                                 "plugSetHash": set_hash, "definitionFound": True,
                                 "isFakePlugSet": fake, "redacted": redacted,
                                 "plugs": plugs})
        result.append({"itemHash": item_hash, "name": weapon.get("name", ""),
                       "resolvedPlugSets": resolved,
                       "evidenceGrade": "same_manifest_definition_join_only",
                       "certifiedObtainableRoll": False,
                       "certifiedEnhancedPerks": False,
                       "certifiedCrossSocketPair": False})
    return sorted(result, key=lambda row: row["itemHash"])
