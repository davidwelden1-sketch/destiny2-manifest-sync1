"""Conservative PvE/PvP measurement-input gate for VAELTRION.

Outputs are derived from supplied observations, never independent gameplay
verification. A source URL and repeated samples do not certify the source.
"""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
import re

VALID_MODES = {"pve_dps", "pve_dr", "pvp_ttk"}


def _positive(value, name, *, zero=False):
    if type(value) not in (int, float, str, Decimal):
        raise ValueError(f"{name}: numeric value required")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{name}: invalid decimal") from exc
    if not number.is_finite() or (number < 0 if zero else number <= 0):
        raise ValueError(f"{name}: positive finite value required")
    return number


def _utc(value, name):
    if type(value) is not str:
        raise ValueError(f"{name}: UTC timestamp required")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name}: invalid timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
        raise ValueError(f"{name}: timestamp must be UTC")
    return timestamp


def _decimal_string(value):
    return format(value.normalize(), "f")


def evaluate_observation(record):
    """Calculate conditional figures; never upgrade an observation to verified."""
    if not isinstance(record, dict):
        raise ValueError("Observation must be an object")
    mode = record.get("mode")
    if mode not in VALID_MODES:
        raise ValueError("Unknown PvE/PvP mode")
    oid = record.get("observation_id")
    if type(oid) is not str or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", oid):
        raise ValueError("Invalid stable observation ID")
    patch = record.get("patch_version")
    manifest = record.get("manifest_version")
    if any(type(x) is not str or not x.strip() for x in (patch, manifest)):
        raise ValueError("Patch and manifest version are mandatory")
    source = record.get("source")
    if not isinstance(source, dict):
        raise ValueError("Source provenance required")
    url = source.get("url")
    if type(url) is not str:
        raise ValueError("Source URL required")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or
            parsed.password or parsed.hostname in ("localhost", "127.0.0.1") or
            parsed.hostname.endswith(".local")):
        raise ValueError("Source must be a public HTTPS URL")
    published = _utc(source.get("published_at_utc"), "published_at_utc")
    observed = _utc(record.get("recorded_at_utc"), "recorded_at_utc")
    if published > observed:
        raise ValueError("Source publication cannot follow evidence recording")
    samples = record.get("sample_count")
    if type(samples) is not int or samples < 1:
        raise ValueError("Positive integer sample_count required")
    scenario = record.get("scenario")
    if type(scenario) is not str or not scenario.strip():
        raise ValueError("Reproducible scenario description required")
    inputs = record.get("inputs")
    if not isinstance(inputs, dict):
        raise ValueError("Input values required")
    derived = {}
    if mode == "pve_dps":
        damage = _positive(inputs.get("total_damage"), "total_damage")
        duration = _positive(inputs.get("duration_seconds"), "duration_seconds")
        derived["conditional_dps"] = _decimal_string(damage / duration)
    elif mode == "pve_dr":
        baseline = _positive(inputs.get("baseline_hit"), "baseline_hit")
        reduced = _positive(inputs.get("mitigated_hit"), "mitigated_hit", zero=True)
        if reduced > baseline:
            raise ValueError("Mitigated hit cannot exceed control hit for DR")
        derived["conditional_dr_fraction"] = _decimal_string(1 - reduced / baseline)
    else:
        precision = _positive(inputs.get("precision_damage"), "precision_damage")
        body = _positive(inputs.get("body_damage"), "body_damage")
        health = _positive(inputs.get("target_health"), "target_health")
        rpm = _positive(inputs.get("rpm"), "rpm")
        sequence = inputs.get("hit_sequence")
        if type(sequence) is not str or not re.fullmatch(r"[PB]+", sequence):
            raise ValueError("Hit sequence must be P/B")
        total = Decimal(0)
        for i, hit in enumerate(sequence):
            total += precision if hit == "P" else body
            if total >= health and i != len(sequence) - 1:
                raise ValueError("Sequence includes shots after lethal hit")
        if total < health:
            raise ValueError("Sequence is not lethal at supplied health")
        derived["conditional_ttk_seconds"] = _decimal_string(
            Decimal(len(sequence) - 1) * 60 / rpm)
        derived["lethal_shots"] = len(sequence)
    return {
        "id": f"d2:observation:{mode}:{oid}",
        "mode": mode,
        "patch_version": patch,
        "manifest_version": manifest,
        "recorded_at_utc": record["recorded_at_utc"],
        "source": dict(source),
        "sample_count": samples,
        "scenario": scenario,
        "derived": derived,
        "confidence_grade": "sourced_observation_unreplicated",
        "gameplay_measurement_independently_verified": False,
        "stacking_verified": False,
        "artifact_legality_verified": False,
        "exact_weapon_roll_legality_verified": False,
        "certified_for_app_build_recommendation": False,
    }
