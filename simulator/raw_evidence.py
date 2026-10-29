"""Fail-closed raw gameplay observation validation.

Only validates evidence structure; it never certifies gameplay accuracy by itself.
"""
from datetime import datetime, timezone

REQUIRED = ("observation_id", "game_version", "observed_at_utc", "activity_mode",
            "subject_id", "configuration", "test_conditions", "source_url",
            "source_kind", "measurement_method", "raw_events", "sample_count")

def validate_observation(item):
    errors = []
    if not isinstance(item, dict):
        return ["observation_must_be_object"]
    for key in REQUIRED:
        if key not in item or item[key] is None or item[key] == "":
            errors.append("missing_" + key)
    if item.get("activity_mode") not in ("PvE", "PvP"):
        errors.append("invalid_activity_mode")
    if not isinstance(item.get("configuration"), dict) or not item.get("configuration"):
        errors.append("invalid_configuration")
    if not isinstance(item.get("test_conditions"), dict) or not item.get("test_conditions"):
        errors.append("invalid_test_conditions")
    events = item.get("raw_events")
    if not isinstance(events, list) or not events:
        errors.append("missing_raw_events")
    elif any(not isinstance(e, dict) or "value" not in e or isinstance(e["value"], bool)
             or not isinstance(e["value"], (int, float)) for e in events):
        errors.append("invalid_raw_event")
    n = item.get("sample_count")
    if type(n) is not int or n < 1 or (isinstance(events, list) and n != len(events)):
        errors.append("invalid_sample_count")
    if item.get("source_kind") not in ("first_party_capture", "independently_reproducible", "third_party"):
        errors.append("invalid_source_kind")
    if item.get("source_kind") == "simulation" or item.get("is_simulated") is True:
        errors.append("simulated_data_not_measurement")
    if item.get("validation_state") == "verified_current" and not item.get("independent_review_reference"):
        errors.append("independent_review_required")
    try:
        stamp = datetime.fromisoformat(item["observed_at_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp > datetime.now(timezone.utc):
            errors.append("invalid_observation_timestamp")
    except (KeyError, AttributeError, ValueError, TypeError):
        errors.append("invalid_observation_timestamp")
    return sorted(set(errors))
