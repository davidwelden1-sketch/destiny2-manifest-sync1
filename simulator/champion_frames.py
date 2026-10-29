"""Official 9.7.0 historical Anti-Champion 2.0 frame rules.

A frame label must come from independently reviewed weapon metadata.
This is NOT a Bungie manifest item-hash lookup, obtainability test,
current-patch certification, or claim of gameplay measurement.
Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Published: 2026-06-09; reviewed: 2026-10-29.
"""
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
REVIEWED_DATE = "2026-10-29"

BASE_FRAMES = {
    "aggressive": "unstoppable",
    "high impact": "unstoppable",
    "precision": "barrier",
    "adaptive": "barrier",
    "lightweight": "overload",
    "rapid-fire": "overload",
}
# Specific weapon-type/frame rows in Bungie's official table override
# generic frame families. Never assume a same-named frame on another type.
SPECIAL_FRAMES = {
    ("ar", "support"): "overload",
    ("lfr", "adaptive burst"): "barrier",
    ("breach gl", "area denial"): "overload",
    ("breach gl", "double fire"): "unstoppable",
    ("breach gl", "micro-missile"): "unstoppable",
    ("breach gl", "wave"): "unstoppable",
    ("drum gl", "compressed wave"): "unstoppable",
    ("hc", "heavy burst"): "unstoppable",
    ("hc", "spread shot"): "overload",
    ("smg", "aggressive burst"): "unstoppable",
    ("pulse", "aggressive burst"): "unstoppable",
    ("pulse", "heavy burst"): "unstoppable",
    ("pulse", "legacy pr-55 frame"): "barrier",
    ("pulse", "rocket-assisted"): "unstoppable",
    ("sidearm", "rocket-assisted"): "unstoppable",
    ("sniper rifle", "disruption"): "barrier",
    ("sword", "caster"): "barrier",
    ("sword", "vortex"): "overload",
    ("sword", "wave"): "unstoppable",
}
HEAT_FRAMES = {
    "dynamic heat weapons": "overload",
    "balanced heat weapons": "overload",
}

def _clean(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("weapon type and frame must be nonempty strings")
    return " ".join(value.casefold().strip().split())

def champion_effect(weapon_type, frame, *, metadata_reviewed=False):
    """Return historical effect, with explicit evidence gates.

    A supplied frame name is not proof of actual item identity. An unknown
    frame must not be assigned an effect by guessing its archetype.
    """
    kind, family = _clean(weapon_type), _clean(frame)
    base = {"effect": None, "source": SOURCE_URL, "source_date": SOURCE_DATE,
            "reviewed_date": REVIEWED_DATE, "gameplay_verified": False,
            "current_manifest_verified": False, "certified_weapon": False}
    if metadata_reviewed is not True:
        return {**base, "status": "weapon_frame_unreviewed"}
    if (kind, family) in SPECIAL_FRAMES:
        return {**base, "effect": SPECIAL_FRAMES[(kind, family)],
                "status": "official_historical_specific_frame"}
    if family in HEAT_FRAMES:
        return {**base, "effect": HEAT_FRAMES[family],
                "status": "official_historical_heat_frame"}
    if family in BASE_FRAMES:
        return {**base, "effect": BASE_FRAMES[family],
                "status": "official_historical_generic_frame"}
    return {**base, "status": "unknown_frame_requires_review"}

def artifact_policy(activity):
    """Fail closed for modes without an independently confirmed active Artifact.

    Bungie TWID 2026-05-29 states Trials and Competitive disable Artifacts.
    Other modes return None rather than claiming current perk availability.
    """
    mode = _clean(activity)
    if mode in {"trials", "trials of osiris", "competitive", "competitive crucible"}:
        return {"artifact_enabled": False, "status": "official_disabled",
                "source": "https://www.bungie.net/7/en/News/Article/twid_05_29_2026"}
    return {"artifact_enabled": None, "status": "current_artifact_review_required"}
