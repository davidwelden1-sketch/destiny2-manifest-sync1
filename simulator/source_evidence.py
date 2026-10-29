"""Source-aware evidence validation for build certification.

This is a structural check, not a claim that a cited source proves gameplay.
"""
from urllib.parse import urlparse

ALLOWED_KINDS = {"official", "manifest", "measurement", "simulation"}
MEASUREMENT_FIELDS = {"damage", "stacking", "attribution", "cooldowns", "resistance", "ttk", "calibration", "validation"}

def validate_evidence_record(field, record):
    if not isinstance(record, dict):
        return False
    if record.get("status") != "verified":
        return False
    kind = record.get("kind")
    if kind not in ALLOWED_KINDS:
        return False
    url = record.get("source_url")
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    if field in MEASUREMENT_FIELDS and kind == "simulation":
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
