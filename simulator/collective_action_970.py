"""Historical 9.7.0 Collective Action rule lookup; not a live TTK/DPS engine.

Fail closed on unknown activity, enhancement status, or pickup.
Do not infer current Artifact availability or obtainable weapon sockets.
"""
import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[1] / "data" / "patch970_collective_corruption_focused_20261102.json"


def _rule(rule_id):
    dataset = json.loads(_DATA.read_text(encoding="utf-8"))
    for record in dataset["records"]:
        if record["id"] == rule_id:
            if record["evidence"] != "official_historical" or record["patch_version"] != "9.7.0":
                raise ValueError("Missing official historical source gate")
            return record
    raise ValueError("Unverified rule")


def collective_action(activity, enhanced, pickup):
    """Return published bonus and initial duration, not an inferred damage result."""
    if activity not in ("pve", "pvp") or type(enhanced) is not bool:
        raise ValueError("Activity or enhanced status unverified")
    r = _rule("d2:patch-rule:970:collective-action-activity-split")
    if pickup not in r["duration_seconds"]:
        raise ValueError("Pickup activation not verified")
    key = activity + "_bonus_" + ("enhanced" if enhanced else "base")
    return {
        "damage_bonus": r[key],
        "initial_duration_seconds": r["duration_seconds"][pickup],
        "maximum_duration_seconds": r["maximum_duration_seconds"],
        "evidence": r["evidence"],
        "runtime_verified": False,
        "guardian_ttk_measured": r["pvp_guardian_ttk_measured"],
        "boss_dps_measured": r["pve_boss_dps_measured"],
    }


def corruption_categories():
    """Separate stacking Corruption from non-stacking Potent Corruption."""
    r = _rule("d2:patch-rule:970:corruption-potent-coexist")
    return {
        "corruption_sources": tuple(r["corruption_sources"]),
        "potent_corruption_sources": tuple(r["potent_corruption_sources"]),
        "can_coexist": r["two_effect_categories_can_coexist"],
        "potent_stacks_with_itself": r["potent_corruption_stacks_with_itself"],
        "tick_damage_measured": r["corruption_tick_damage_measured"],
    }
