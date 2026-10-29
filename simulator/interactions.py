"""Explicit, evidence-gated interaction hypotheses for PvE and PvP."""
from dataclasses import dataclass
from simulator.activity import ActivityContext

@dataclass(frozen=True)
class Interaction:
    name: str
    trigger_hash: int
    effect_hash: int
    context: ActivityContext
    activation_rule: str
    stacking_rule: str
    evidence_status: str
    source_url: str

    def __post_init__(self):
        if not self.name.strip() or self.trigger_hash <= 0 or self.effect_hash <= 0:
            raise ValueError("Named trigger and effect hashes required")
        if not self.activation_rule.strip() or not self.stacking_rule.strip():
            raise ValueError("Activation and stacking rules required")
        if self.evidence_status not in {"official", "measured", "estimated", "hypothetical"}:
            raise ValueError("Invalid evidence status")
        if not self.source_url.startswith(("https://", "http://")):
            raise ValueError("Source URL required")

def interaction_candidates(interactions, context):
    return [x for x in interactions if x.context == context]

def confirmed_interactions(interactions, context):
    """A source label alone is not certification of a combination."""
    return [x for x in interaction_candidates(interactions, context)
            if x.evidence_status in {"official", "measured"}
            and x.activation_rule != "unknown" and x.stacking_rule != "unknown"]
