"""Activity-scoped sandbox evidence. PvE and PvP observations never mix silently."""
from dataclasses import dataclass
from math import isfinite

ACTIVITIES = {"pve", "pvp"}
MODES = {"pve": {"general", "raid", "dungeon", "nightfall", "grandmaster", "boss", "add_clear"},
         "pvp": {"general", "6v6", "3v3", "trials", "competitive", "private_match"}}

@dataclass(frozen=True)
class ActivityContext:
    activity: str
    mode: str
    sandbox_version: str
    artifact_enabled: bool | None = None

    def __post_init__(self):
        if self.activity not in ACTIVITIES or self.mode not in MODES[self.activity]:
            raise ValueError("Unknown or mismatched activity/mode")
        if not self.sandbox_version.strip():
            raise ValueError("Sandbox version required")
        if self.artifact_enabled is not None and not isinstance(self.artifact_enabled, bool):
            raise ValueError("Artifact enabled must be true, false, or unknown")

@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    unit: str
    context: ActivityContext
    source_url: str
    evidence_status: str

    def __post_init__(self):
        if not isfinite(self.value):
            raise ValueError("Metric must be finite")
        if not self.unit or not self.source_url.startswith(("https://", "http://")):
            raise ValueError("Unit and source required")
        if self.evidence_status not in {"official", "measured", "estimated", "hypothetical"}:
            raise ValueError("Invalid evidence status")

def filter_metrics(metrics, context):
    return [m for m in metrics if m.context == context]
