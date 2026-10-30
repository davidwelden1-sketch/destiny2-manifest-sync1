"""Conservative exact-path observation join for game-wide weapon legality research.

Manifest plug membership is NOT proof of an obtainable roll. An independently
supplied snapshot can document an observed instance at a date, but never
automatically certifies current drops, enhancement, or gameplay damage.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


KEY_FIELDS = ("item_hash", "perk_a_hash", "perk_b_hash",
              "a_socket_index", "b_socket_index")
SOURCE_KINDS = frozenset(("gameplay_drop_capture", "bungie_profile_instance"))


def _path_key(record):
    if not isinstance(record, dict):
        raise ValueError("Path must be an object")
    values = tuple(record.get(field) for field in KEY_FIELDS)
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError("Exact path hashes and socket indexes must be nonnegative integers")
    if min(values[:3]) == 0 or values[3] == values[4]:
        raise ValueError("Exact path requires positive hashes and distinct sockets")
    return values


def _utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("Timestamp must be UTC ISO-8601 ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid observation timestamp") from exc
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError("Timestamp must be UTC")
    return parsed


def audit_roll_observations(pair_report, observations, checked_at_utc):
    """Join source-labelled observations by exact hash AND socket path.

    Historical captures are leads, not authenticated current-roll certification.
    No observations are invented when the evidence list is empty.
    """
    if not isinstance(pair_report, dict):
        raise ValueError("Pair report must be an object")
    version = pair_report.get("manifest_version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Pair report requires a manifest version")
    paths = pair_report.get("per_exact_socket_path")
    if not isinstance(paths, list) or not isinstance(observations, list):
        raise ValueError("Paths and observations must be lists")
    checked = _utc(checked_at_utc)
    keyed = {}
    for path in paths:
        key = _path_key(path)
        if key in keyed:
            raise ValueError("Duplicate exact socket path in manifest report")
        keyed[key] = path
    matched = {key: [] for key in keyed}
    unmatched = []
    seen_ids = set()
    for observation in observations:
        key = _path_key(observation)
        evidence_id = observation.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip() or evidence_id in seen_ids:
            raise ValueError("Missing or duplicate evidence_id")
        seen_ids.add(evidence_id)
        if observation.get("source_kind") not in SOURCE_KINDS:
            raise ValueError("Unknown observation source kind")
        url = observation.get("source_url")
        if not isinstance(url, str) or not url.startswith("https://") or len(url) < 12:
            raise ValueError("Observation requires HTTPS source URL")
        observed = _utc(observation.get("observed_at_utc"))
        if observed > checked:
            raise ValueError("Future observation cannot be treated as evidence")
        observed_version = observation.get("manifest_version")
        if not isinstance(observed_version, str) or not observed_version.strip():
            raise ValueError("Observation requires its own manifest version")
        evidence = {
            "evidence_id": evidence_id,
            "source_kind": observation["source_kind"],
            "source_url": url,
            "observed_at_utc": observation["observed_at_utc"],
            "observed_manifest_version": observed_version,
            "same_manifest_version": observed_version == version,
            "evidence_grade": "unverified_external_capture",
        }
        if key in matched:
            matched[key].append(evidence)
        else:
            unmatched.append(evidence_id)
    rows = []
    for key in sorted(keyed):
        row = {field: val for field, val in zip(KEY_FIELDS, key)}
        row.update({
            "weapon_name": keyed[key].get("weapon_name"),
            "historical_exact_path_observation": bool(matched[key]),
            "observations": sorted(matched[key], key=lambda e: e["evidence_id"]),
            "current_acquisition": "unverified",
            "roll_legality": "unverified",
            "enhanced_perk_legality": "unverified",
        })
        rows.append(row)
    return {
        "manifest_version": version,
        "checked_at_utc": checked_at_utc,
        "manifest_exact_socket_paths": len(rows),
        "historically_observed_paths": sum(r["historical_exact_path_observation"] for r in rows),
        "unmatched_evidence_ids": sorted(unmatched),
        "per_exact_socket_path": rows,
        "interpretation": (
            "External captures are not authenticated by this audit. A matching historical "
            "item/plug/socket path does not prove a current obtainable roll, enhanced perk, "
            "active Artifact, or measured PvE/PvP outcome. Version mismatches remain historical."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair-report", required=True)
    parser.add_argument("--observations", required=True)
    parser.add_argument("--checked-at-utc", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    pair_report = json.loads(Path(args.pair_report).read_text(encoding="utf-8"))
    observations = json.loads(Path(args.observations).read_text(encoding="utf-8"))
    report = audit_roll_observations(pair_report, observations, args.checked_at_utc)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "per_exact_socket_path"}, indent=2))


if __name__ == "__main__":
    main()
