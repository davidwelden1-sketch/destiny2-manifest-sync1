"""Patch-derived intrinsic anti-Champion rule lookup, NOT a manifest frame detector.

Bungie Destiny 2 Update 9.7.0 (2026-06-09) lists base archetypes and
specific weapon-frame overrides. Caller MUST supply independently verified
weapon type/frame; itemSubType or randomized sockets alone are insufficient.
No artifact, activation, stun uptime, or gameplay measurements inferred.
"""
SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
BASE = {
    "aggressive": "unstoppable",
    "high impact": "unstoppable",
    "precision": "barrier",
    "adaptive": "barrier",
    "lightweight": "overload",
    "rapid fire": "overload",
}
SPECIFIC = {
    ("support", "auto rifle"): "overload",
    ("adaptive burst", "linear fusion rifle"): "barrier",
    ("area denial", "breach grenade launcher"): "overload",
    ("double fire", "breach grenade launcher"): "unstoppable",
    ("micro missile", "breach grenade launcher"): "unstoppable",
    ("wave", "breach grenade launcher"): "unstoppable",
    ("compressed wave", "drum grenade launcher"): "unstoppable",
    ("heavy burst", "hand cannon"): "unstoppable",
    ("spread shot", "hand cannon"): "overload",
    ("aggressive burst", "submachine gun"): "unstoppable",
    ("aggressive burst", "pulse rifle"): "unstoppable",
    ("heavy burst", "pulse rifle"): "unstoppable",
    ("legacy pr 55 frame", "pulse rifle"): "barrier",
    ("rocket assisted", "pulse rifle"): "unstoppable",
    ("rocket assisted", "sidearm"): "unstoppable",
    ("disruption", "sniper rifle"): "barrier",
    ("caster", "sword"): "barrier",
    ("vortex", "sword"): "overload",
    ("wave", "sword"): "unstoppable",
}
HEAT_FRAMES = {"dynamic heat weapons": "overload",
               "balanced heat weapons": "overload"}
TYPE_ALIASES = {
    "ar": "auto rifle", "lfr": "linear fusion rifle",
    "breach gl": "breach grenade launcher", "drum gl": "drum grenade launcher",
    "hc": "hand cannon", "smg": "submachine gun",
    "pulse": "pulse rifle",
}


def _normal(value):
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Classification labels must be nonempty strings or None")
    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())


def intrinsic_champion_rule(archetype=None, frame=None, weapon_type=None):
    """Return a patch rule, or unknown if exact frame/weapon evidence is absent.

    'provisional_base_rule' is never a certified exact-weapon classification.
    """
    archetype = _normal(archetype)
    frame = _normal(frame)
    weapon_type = _normal(weapon_type)
    weapon_type = TYPE_ALIASES.get(weapon_type, weapon_type)
    if frame in HEAT_FRAMES:
        return {"effect": HEAT_FRAMES[frame], "evidence": "official_heat_frame_rule",
                "weapon_verified": False, "source": SOURCE}
    if frame is not None:
        if weapon_type is None:
            return {"effect": None, "evidence": "weapon_type_required_for_frame",
                    "weapon_verified": False, "source": SOURCE}
        effect = SPECIFIC.get((frame, weapon_type))
        if effect is not None:
            return {"effect": effect, "evidence": "official_specific_frame_rule",
                    "weapon_verified": False, "source": SOURCE}
        if any(f == frame for f, _ in SPECIFIC):
            return {"effect": None, "evidence": "frame_weapon_type_mismatch",
                    "weapon_verified": False, "source": SOURCE}
        # An unrecognized frame could override the base archetype. Fail closed.
        return {"effect": None, "evidence": "unverified_frame",
                "weapon_verified": False, "source": SOURCE}
    if archetype in BASE:
        return {"effect": BASE[archetype], "evidence": "provisional_base_rule",
                "weapon_verified": False, "source": SOURCE}
    return {"effect": None, "evidence": "insufficient_archetype_or_frame",
            "weapon_verified": False, "source": SOURCE}
