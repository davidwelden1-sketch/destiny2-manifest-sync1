"""Rank missing interaction research by evidence and rule completeness."""
from simulator.interactions import Interaction

def interaction_research_queue(interactions):
    result = []
    for interaction in interactions:
        if not isinstance(interaction, Interaction):
            raise TypeError("Expected Interaction")
        missing = []
        if interaction.activation_rule == "unknown":
            missing.append("activation_rule")
        if interaction.stacking_rule == "unknown":
            missing.append("stacking_rule")
        if interaction.evidence_status in {"estimated", "hypothetical"}:
            missing.append("official_or_measured_evidence")
        if missing:
            result.append({"name": interaction.name,
                           "activity": interaction.context.activity,
                           "mode": interaction.context.mode,
                           "trigger_hash": interaction.trigger_hash,
                           "effect_hash": interaction.effect_hash,
                           "missing": missing})
    return sorted(result, key=lambda x: (-len(x["missing"]), x["activity"], x["name"]))
