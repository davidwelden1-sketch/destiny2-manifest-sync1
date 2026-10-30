"""Conservative kill-location ammo-brick event projection.

Official source: Destiny 2 Update 9.7.0 (2026-06-09), Ammo System:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
An enemy defeated while floating over a pit cannot drop the brick, even
when its defeat completes the ammo meter; meter progress is retained and
an owed brick is spawned on a later kill not over a pit.

This model accepts meter-completion as an INPUT; it does not estimate meter
progress, actual spawn counts, ammo quantity, mode scalars, or DPS. Multiple
meter completions while one brick is owed are explicitly ambiguous.
"""


def project_ammo_brick_events(kills):
    """Project source-backed event order, never a measured brick count.

    Each kill must be a dict with two booleans: ``over_pit`` and
    ``meter_completed``. This models the kill-location gate in any mode but
    makes no claim that ammo meter rates are the same in PvE and PvP.
    """
    if not isinstance(kills, (list, tuple)):
        raise ValueError("kills must be an ordered list or tuple")
    pending = False
    ambiguous = False
    projected = []
    for index, kill in enumerate(kills):
        if not isinstance(kill, dict) or set(kill) != {"over_pit", "meter_completed"}:
            raise ValueError(f"kill {index} must have exactly the two event fields")
        pit, filled = kill["over_pit"], kill["meter_completed"]
        if type(pit) is not bool or type(filled) is not bool:
            raise ValueError(f"kill {index} requires boolean event fields")
        if pit:
            if filled and pending:
                ambiguous = True  # Unknown whether multiple owed bricks can queue.
                event = "multiple_meter_completions_unresolved"
            elif filled:
                pending = True
                event = "meter_completed_brick_deferred"
            else:
                event = "no_brick_from_pit_kill"
        elif pending:
            pending = False
            if filled:
                ambiguous = True  # A simultaneous new completion may affect count.
                event = "owed_brick_due_new_completion_unresolved"
            else:
                event = "owed_brick_due"
        else:
            event = "meter_completion_spawn_candidate" if filled else "no_brick_trigger"
        projected.append({"kill_index": index, "event": event,
                          "owed_brick_pending": pending})
    return {"events": projected, "owed_brick_pending": pending,
            "multiple_brick_count_unresolved": ambiguous,
            "evidence": "official_patch_rule_not_measured_gameplay",
            "ammo_brick_count": None,
            "ammo_meter_progress": None}
