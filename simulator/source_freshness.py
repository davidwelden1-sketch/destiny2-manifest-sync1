"""Fail-closed source suitability checks for current Destiny 2 calibration.

A recent repository commit does not override an explicit dataset warning.
Passing metadata screening is NOT gameplay certification. The optional current
version and activity constraints must be supplied by a verified caller; this
module does not fetch live game data or infer playlist equivalence.
"""
from datetime import date


def source_suitability(source, as_of, *, current_game_version=None, activity=None):
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
    if not isinstance(version, str) or not version.strip():
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
    if current_game_version is not None:
        if not isinstance(current_game_version, str) or not current_game_version.strip():
            raise ValueError("current_game_version must be a nonempty verified version")
        if version != current_game_version:
            return {"usable_for_current_calibration": False, "reason": "game_version_mismatch"}
    if activity is not None:
        if activity not in ("pve", "pvp"):
            raise ValueError("activity must be pve or pvp")
        observed_activity = source.get("activity")
        if observed_activity not in ("pve", "pvp"):
            return {"usable_for_current_calibration": False, "reason": "measurement_activity_missing"}
        if observed_activity != activity:
            return {"usable_for_current_calibration": False, "reason": "activity_mismatch"}
    return {"usable_for_current_calibration": True,
            "reason": "metadata_screen_only_not_gameplay_proof"}
