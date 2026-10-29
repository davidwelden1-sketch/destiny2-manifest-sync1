"""Require source metadata for calibration records."""
from datetime import datetime

def validate_measurement(record):
    required = ("name", "value", "unit", "source_url", "observed_at", "context", "status")
    missing = [k for k in required if not record.get(k) and record.get(k) != 0]
    if missing:
        raise ValueError("Missing measurement fields: " + ", ".join(missing))
    if record["status"] not in ("measured", "official", "estimated", "hypothetical"):
        raise ValueError("Unsupported evidence status")
    if not isinstance(record["value"], (int, float)):
        raise ValueError("Measurement value must be numeric")
    datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
    return dict(record)
