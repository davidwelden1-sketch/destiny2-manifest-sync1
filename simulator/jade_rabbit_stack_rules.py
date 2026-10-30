"""Conservative Jade Rabbit Fate of All Fools event/stack interval model.

Official source: Destiny 2 Update 9.7.0, 2026-06-09:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

Precision kills add one stack (cap 15), direct body-shot damage removes
one stack, Firefly splash damage does not remove stacks, and catalyst
special reload consumes stacks for a single Micro Missile round.
The patch does not quantify normal-reload stack retention or missile
damage. Those outcomes must remain uncertain, not simulated as measured.
"""
MAX_STACKS = 15
EVENTS = frozenset(("precision_final_blow", "direct_body_hit",
                    "firefly_splash_damage", "normal_reload", "special_reload"))


def project_jade_rabbit_events(events, initial_stacks=0):
    """Return source-graded possible stack bounds after ordered events.

    Events describe *Jade Rabbit* weapon events, not arbitrary allied kills.
    An interval rather than a fabricated exact number represents an ordinary
    reload, whose stack retention quantity is not specified in patch notes.
    """
    if not isinstance(events, (list, tuple)):
        raise ValueError("events must be an ordered list or tuple")
    if type(initial_stacks) is not int or not 0 <= initial_stacks <= MAX_STACKS:
        raise ValueError("initial_stacks must be an integer between 0 and 15")
    low = high = initial_stacks
    rows = []
    for index, event in enumerate(events):
        if not isinstance(event, str) or event not in EVENTS:
            raise ValueError(f"Unknown Jade Rabbit event at index {index}")
        missile = "none"
        if event == "precision_final_blow":
            low, high = min(MAX_STACKS, low + 1), min(MAX_STACKS, high + 1)
        elif event == "direct_body_hit":
            low, high = max(0, low - 1), max(0, high - 1)
        elif event == "normal_reload":
            # Patch says reload no longer fully removes stacks, but does not
            # state a retention formula. Do not assert a numerical floor.
            low = 0
        elif event == "special_reload":
            if low > 0:
                missile = "one_round_official_rule_damage_unmeasured"
            elif high > 0:
                missile = "one_round_possible_stack_uncertain"
            else:
                missile = "zero_stack_activation_unverified"
            low = high = 0
        # Firefly splash does not subtract stacks, even though its damage
        # scaling with stacks is official and its exact curve is unmeasured.
        rows.append({"index": index, "event": event,
                     "stacks_min": low, "stacks_max": high,
                     "micro_missile": missile})
    return {"events": rows, "stacks_min": low, "stacks_max": high,
            "evidence": "official_2026_06_09_patch_rule_not_gameplay_measurement",
            "micro_missile_damage": None, "pve_dps": None, "pvp_ttk": None,
            "current_artifact_selection": "unverified",
            "current_roll_enhancement": "not_applicable_exotic"}
