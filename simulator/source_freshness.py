"""Fail-closed source suitability checks for current Destiny 2 calibration.

A recent repository commit does not override an explicit dataset warning.
"""
from datetime import date

def source_suitability(source, as_of):
    if not isinstance(source, dict):
        raise TypeError("source must be a mapping")
    if isinstance(as_of, str):
        as_of = date.fromisoformat(as_of)
    if not isinstance(as_of, date):
        raise TypeError("as_of must be a date")
    if source.get("explicitly_outdated") is True:
        return {"usable_for_current_calibration": False, "reason": "explicit_outdated_warning"}
    if source.get("independent_measurement") is not True:
        return {"usable_for_current_calibration": False, "reason": "not_independent_measurement"}
    version = source.get("game_version")
    if not isinstance(version, str) or not version:
        return {"usable_for_current_calibration": False, "reason": "game_version_missing"}
    tested = source.get("measured_on")
    try:
        measured = date.fromisoformat(tested)
    except (TypeError, ValueError):
        return {"usable_for_current_calibration": False, "reason": "measurement_date_missing"}
    if measured > as_of:
        return {"usable_for_current_calibration": False, "reason": "future_measurement_date"}
    if source.get("independently_reviewed") is not True:
        return {"usable_for_current_calibration": False, "reason": "independent_review_pending"}
    return {"usable_for_current_calibration": True,
            "reason": "metadata_screen_only_not_gameplay_proof"}
