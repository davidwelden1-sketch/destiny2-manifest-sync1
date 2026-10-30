"""Patch-grounded Frost Armor endpoints, not interpolated gameplay measurements.

Bungie Update 9.7.0 (2026-06-09):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Five stacks: approximately 35% damage resistance. Whisper of Rime:
maximum seven stacks and maximum 50% resistance. Stacks decay one by one.
PvP damage-resistance values and intermediate-stack curves are NOT inferred.
"""

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"


def frost_armor_endpoint(*, stacks, whisper_of_rime, mode):
    """Return only officially stated DR endpoints; unknowns stay unknown."""
    if type(stacks) is not int or stacks < 0:
        raise ValueError("stacks must be a nonnegative integer")
    if type(whisper_of_rime) is not bool:
        raise ValueError("whisper_of_rime must be boolean")
    if mode not in ("pve", "pvp"):
        raise ValueError("mode must be pve or pvp")
    maximum = 7 if whisper_of_rime else 5
    if stacks > maximum:
        raise ValueError("stacks exceed documented cap")
    # These numerical endpoints are patch-note descriptions, not player tests.
    approximate_dr = None
    if mode == "pve":
        if stacks == 0:
            approximate_dr = 0.0
        elif stacks == 5:
            approximate_dr = 0.35
        elif stacks == 7 and whisper_of_rime:
            approximate_dr = 0.50
    return {
        "mode": mode,
        "stacks": stacks,
        "max_stacks": maximum,
        "approximate_dr": approximate_dr,
        "evidence_grade": ("official_patch_approximate_endpoint"
                           if approximate_dr is not None else "unmeasured"),
        "decay_model": "one_stack_at_a_time",
        "stack_duration_seconds": None,
        "stacking_with_other_buffs": "unverified",
        "source": SOURCE_URL,
        "interpretation": ("Do not interpolate unknown stacks, apply PvE numbers "
                           "to PvP, or treat this as gameplay-measured DR."),
    }


def shatter_champion_stun():
    """Current official intrinsic Stasis shatter anti-Champion relationship."""
    return {"stuns": "unstoppable", "not_stunned_by_shatter": "overload",
            "source": SOURCE_URL, "evidence_grade": "official_patch"}
