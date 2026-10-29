"""Compare build metrics only within the same activity context.

No game balance values are assumed. Inputs are sourced or explicitly hypothetical.
"""
from dataclasses import dataclass
from math import isfinite
from simulator.activity import ActivityContext

@dataclass(frozen=True)
class BuildScore:
    build_id: str
    context: ActivityContext
    damage: float
    survivability: float
    uptime: float
    evidence_status: str

    def __post_init__(self):
        if not self.build_id.strip():
            raise ValueError("Build ID required")
        if any(not isfinite(v) or v < 0 for v in (self.damage, self.survivability, self.uptime)):
            raise ValueError("Finite nonnegative metrics required")
        if self.evidence_status not in {"official", "measured", "estimated", "hypothetical"}:
            raise ValueError("Invalid evidence status")

def pareto_frontier(builds):
    """Return nondominated builds, maximizing all three metrics."""
    builds = list(builds)
    if builds and any(b.context != builds[0].context for b in builds):
        raise ValueError("Cannot rank builds from different activities or sandbox contexts")
    return [b for b in builds if not any(
        other is not b
        and other.damage >= b.damage
        and other.survivability >= b.survivability
        and other.uptime >= b.uptime
        and (other.damage > b.damage or other.survivability > b.survivability or other.uptime > b.uptime)
        for other in builds)]
