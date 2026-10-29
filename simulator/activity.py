"""Activity-scoped sandbox evidence. PvE and PvP observations never mix silently."""
from dataclasses import dataclass
from math import isfinite

ACTIVITIES = {"pve", "pvp"}
MODES = {"pve": {"general", "raid", "dungeon", "nightfall", "grandmaster", "boss", "add_clear"},
         "pvp": {"general", "6v6", "3v3", "trials", "competitive", "private_match"}}


def _artifact_2_0_or_unknown(version: str) -> bool:
    """Fail closed for unknown versions; historical pre-9.7.0 contexts remain representable."""
    components = version.split(".")
    if len(components) < 3 or any(not part.isdecimal() for part in components[:3]):
        return True
    return tuple(map(int, components[:3])) >= (9, 7, 0)


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
        # Official Bungie 9.7.0 (2026-06-09): Artifact mods disabled in Glory/Competitive and Trials.
        if (self.activity == "pvp" and self.mode in {"competitive", "trials"}
                and self.artifact_enabled is True and _artifact_2_0_or_unknown(self.sandbox_version)):
            raise ValueError("Artifact perks are disabled in Competitive and Trials from 9.7.0 onward")

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
