"""Patch-derived Collective Action event clock (Bungie 9.7.0, 2026-06-09).

Official: Firesprite/Void Breach +8s, Ionic Trace/Stasis Shard +4s,
Tangle destruction +4s, Tangle throw +4s additional duration, cap 16s.
Artifact elemental-orb duration is deliberately UNMODELLED until confirmed.
No damage ownership, proc cooldown, stacking or in-game measurements inferred.
"""
from math import isfinite

DURATIONS = {
    "firesprite": 8.0,
    "void_breach": 8.0,
    "ionic_trace": 4.0,
    "stasis_shard": 4.0,
    "tangle_detonation": 4.0,
    "tangle_throw_extension": 4.0,
}
MAX_DURATION = 16.0
DAMAGE_MULTIPLIERS = {
    "pve": {False: 1.30, True: 1.33},
    "pvp": {False: 1.10, True: 1.11},
}


def advance_collective_action(remaining, elapsed, event, *, enhanced=False, activity="pve"):
    """Return conservative event-clock state, not a measured activation timeline.

    Throw extension alone does not initiate a buff; a separately confirmed
    Tangle destruction event is required. Do not double-count a throw's impact
    without observing two separate events. No 'artifact_orb' numeric duration
    is asserted from the patch's qualitative equivalence statement.
    """
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               and isfinite(v) and v >= 0 for v in (remaining, elapsed)):
        raise ValueError("Remaining duration and elapsed seconds must be finite nonnegative numbers")
    if remaining > MAX_DURATION:
        raise ValueError("Remaining duration exceeds official cap")
    if not isinstance(enhanced, bool) or activity not in DAMAGE_MULTIPLIERS:
        raise ValueError("Invalid enhancement/activity")
    if event not in DURATIONS and event is not None:
        raise ValueError("Unverified event type; artifact orbs require explicit timing evidence")
    active_remaining = max(0.0, remaining - elapsed)
    if event == "tangle_throw_extension" and active_remaining == 0:
        new_remaining = 0.0
    else:
        new_remaining = min(MAX_DURATION, active_remaining + DURATIONS.get(event, 0.0))
    return {
        "remaining_seconds": new_remaining,
        "active": new_remaining > 0,
        "damage_multiplier_if_active": DAMAGE_MULTIPLIERS[activity][enhanced],
        "evidence": "official_patch_duration_and_multiplier__hypothetical_event_timeline",
        "measured_in_game": False,
    }
