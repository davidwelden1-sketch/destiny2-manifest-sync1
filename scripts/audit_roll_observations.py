"""Conservative exact-path observation join for game-wide weapon legality research.

Manifest plug membership is NOT proof of an obtainable roll. An independently
supplied snapshot can document an observed instance at a date, but never
automatically certifies current drops, enhancement, or gameplay damage.
"""
import argparse
import json
from datetime import date, datetime, timezone

from simulator.loot_pool_970_freshness import audit_loot_pool_freshness
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


def audit_roll_observations(pair_report, observations, checked_at_utc,
                            corrections=None, loot_source_claims=None):
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
    if corrections is None:
        corrections = []
    if not isinstance(corrections, list):
        raise ValueError("Patch corrections must be a list")
    correction_by_path = {}
    correction_ids = set()
    for correction in corrections:
        key = _path_key(correction)
        correction_id = correction.get("correction_id")
        if (not isinstance(correction_id, str) or not correction_id.strip()
                or correction_id in correction_ids):
            raise ValueError("Missing or duplicate correction_id")
        correction_ids.add(correction_id)
        effective = _utc(correction.get("effective_at_utc"))
        if effective > checked:
            raise ValueError("Future patch correction cannot be applied")
        source = correction.get("source_url")
        if not isinstance(source, str) or not source.startswith("https://www.bungie.net/"):
            raise ValueError("Patch correction requires a Bungie HTTPS source URL")
        if correction.get("correction_action") not in ("perk_removed", "perk_replaced"):
            raise ValueError("Unknown patch correction action")
        correction_by_path.setdefault(key, []).append({
            "correction_id": correction_id,
            "effective_at_utc": correction["effective_at_utc"],
            "source_url": source,
            "correction_action": correction["correction_action"],
            "evidence_grade": "submitted_patch_reference_not_independently_authenticated",
        })
    # External source classifications are keyed by exact item hash, never by
    # shared display name. They are unverified claims, not roll certificates.
    if loot_source_claims is None:
        loot_source_claims = []
    if not isinstance(loot_source_claims, list):
        raise ValueError("Loot source claims must be a list")
    source_by_hash = {}
    for claim in loot_source_claims:
        if not isinstance(claim, dict):
            raise ValueError("Loot source claim must be an object")
        item_hash = claim.get("item_hash")
        if type(item_hash) is not int or item_hash <= 0:
            raise ValueError("Loot source item_hash must be a positive integer")
        if item_hash in source_by_hash:
            raise ValueError("Duplicate loot source item_hash")
        source_url = claim.get("source_url")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            raise ValueError("Loot source claim requires an HTTPS source URL")
        freshness = audit_loot_pool_freshness(
            item_hash=item_hash, source_kind=claim.get("source_kind"),
            pre_edge_of_fate=claim.get("pre_edge_of_fate"),
            craftable=claim.get("craftable"),
            observation_date=claim.get("observation_date"),
            activity=claim.get("activity", "pve"),
            observed_manifest_version=claim.get("observed_manifest_version"),
            reference_manifest_version=version,
        )
        if date.fromisoformat(freshness["observation_date"]) > checked.date():
            raise ValueError("Future loot source claim cannot be used")
        source_by_hash[item_hash] = {
            **freshness, "claim_source_url": source_url,
            "claim_authenticated": False,
        }
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
        row_corrections = sorted(correction_by_path.get(key, []),
                                 key=lambda c: (c["effective_at_utc"], c["correction_id"]))
        predating = sorted({
            observation["evidence_id"]
            for observation in matched[key]
            if any(_utc(observation["observed_at_utc"]) <
                   _utc(c["effective_at_utc"]) for c in row_corrections)
        })
        row = {field: val for field, val in zip(KEY_FIELDS, key)}
        row.update({
            "weapon_name": keyed[key].get("weapon_name"),
            "historical_exact_path_observation": bool(matched[key]),
            "observations": sorted(matched[key], key=lambda e: e["evidence_id"]),
            "patch_correction_claims": row_corrections,
            "post_patch_revalidation_required": bool(row_corrections),
            "observations_predating_patch_correction": predating,
            "current_acquisition": "unverified",
            "roll_legality": "unverified",
            "enhanced_perk_legality": "unverified",
            "loot_source_freshness": source_by_hash.get(key[0]),
        })
        rows.append(row)
    return {
        "manifest_version": version,
        "checked_at_utc": checked_at_utc,
        "manifest_exact_socket_paths": len(rows),
        "historically_observed_paths": sum(r["historical_exact_path_observation"] for r in rows),
        "unmatched_evidence_ids": sorted(unmatched),
        "unmatched_loot_source_item_hashes": sorted(set(source_by_hash) -
                                                   {key[0] for key in keyed}),
        "unmatched_correction_ids": sorted(
            c["correction_id"] for key, rows in correction_by_path.items()
            if key not in keyed for c in rows),
        "per_exact_socket_path": rows,
        "interpretation": (
            "External captures are not authenticated by this audit. A matching historical "
            "item/plug/socket path does not prove a current obtainable roll, enhanced perk, "
            "active Artifact, or measured PvE/PvP outcome. Version mismatches remain historical. "
            "Submitted patch correction references require independent source verification and "
            "exact hash mapping; affected historical captures must be revalidated after a correction. "
            "Externally submitted loot-source classifications are not authenticated and cannot "
            "certify an obtainable or enhanceable weapon roll."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair-report", required=True)
    parser.add_argument("--observations", required=True)
    parser.add_argument("--checked-at-utc", required=True)
    parser.add_argument("--corrections", help="Optional exact-hash patch correction claims JSON")
    parser.add_argument("--loot-source-claims", help="Optional item-hash source freshness claims JSON")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    pair_report = json.loads(Path(args.pair_report).read_text(encoding="utf-8"))
    observations = json.loads(Path(args.observations).read_text(encoding="utf-8"))
    corrections = (json.loads(Path(args.corrections).read_text(encoding="utf-8"))
                   if args.corrections else None)
    loot_claims = (json.loads(Path(args.loot_source_claims).read_text(encoding="utf-8"))
                   if args.loot_source_claims else None)
    report = audit_roll_observations(pair_report, observations, args.checked_at_utc,
                                     corrections=corrections,
                                     loot_source_claims=loot_claims)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "per_exact_socket_path"}, indent=2))


if __name__ == "__main__":
    main()
