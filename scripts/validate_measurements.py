"""Validate a JSONL sandbox observation intake file without changing its data."""
import json
import sys
from pathlib import Path
from simulator.activity import ActivityContext
from simulator.measurements import SandboxMeasurement
from simulator.evidence_report import evidence_summary

def validate_lines(lines):
    measurements = []
    errors = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            context = ActivityContext(**row["context"])
            measurements.append(SandboxMeasurement(
                item_hash=row["item_hash"], metric=row["metric"], value=row["value"],
                unit=row["unit"], context=context, source_url=row["source_url"],
                observed_at=row["observed_at"], evidence_status=row["evidence_status"],
                conditions=row["conditions"]))
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            errors.append({"line": line_number, "error": str(exc)})
    summary = evidence_summary([{"evidence_status": x.evidence_status} for x in measurements])
    return {"valid": len(measurements), "errors": errors, "evidence": summary,
            "pve": sum(x.context.activity == "pve" for x in measurements),
            "pvp": sum(x.context.activity == "pvp" for x in measurements)}

if __name__ == "__main__":
    path = Path(sys.argv[1])
    result = validate_lines(path.read_text().splitlines())
    print(json.dumps(result, indent=2))
    if result["errors"]:
        raise SystemExit(1)
