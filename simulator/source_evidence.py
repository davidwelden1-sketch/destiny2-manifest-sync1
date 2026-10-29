"""Structural source-evidence gate; NOT independent validation of source claims."""
from datetime import date
from urllib.parse import urlparse

ALLOWED_KINDS = {"official", "manifest", "measurement", "simulation"}
MEASUREMENT_FIELDS = {"damage", "stacking", "attribution", "cooldowns",
                      "resistance", "ttk", "calibration", "validation"}
FIELD_KINDS = {
    "manifest": {"manifest", "official"},
    "exact_hash": {"manifest", "official"},
    "active_frame": {"official", "measurement"},
    "legal_traits": {"manifest", "official"},
    "obtainability": {"official", "measurement"},
    "enhancement": {"official", "measurement"},
    "calibration": {"measurement"},
    "ttk": {"measurement"},
    "attribution": {"measurement"},
    "damage": {"official", "measurement"},
    "resistance": {"official", "measurement"},
    "cooldowns": {"official", "measurement"},
    "stacking": {"official", "measurement"},
    "validation": {"measurement"},
}

def _valid_measurement_protocol(record):
    if not isinstance(record.get("method"), str) or not record["method"].strip():
        return False
    if type(record.get("sample_size")) is not int or record["sample_size"] < 1:
        return False
    if not isinstance(record.get("game_version"), str) or not record["game_version"].strip():
        return False
    if not isinstance(record.get("activity"), str) or not record["activity"].strip():
        return False
    try:
        date.fromisoformat(record["measured_on"])
    except (KeyError, TypeError, ValueError):
        return False
    return True

def validate_evidence_record(field, record):
    """Require plausible source metadata; URLs and claims are NOT independently checked."""
    if not isinstance(record, dict) or record.get("status") != "verified":
        return False
    kind = record.get("kind")
    if kind not in ALLOWED_KINDS or kind not in FIELD_KINDS.get(field, ALLOWED_KINDS - {"simulation"}):
        return False
    url = record.get("source_url")
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    if kind == "measurement" and not _valid_measurement_protocol(record):
        return False
    return True

def sourced_phase_status(phase, records):
    from simulator.certification_gate import REQUIRED
    if phase not in REQUIRED:
        raise ValueError("unknown phase")
    if not isinstance(records, dict):
        raise TypeError("records must be a dict")
    gaps = tuple(k for k in REQUIRED[phase] if not validate_evidence_record(k, records.get(k)))
    return {"complete": not gaps, "gaps": gaps}
