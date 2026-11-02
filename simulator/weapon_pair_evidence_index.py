"""App-facing exact-hash weapon pair evidence from the conservative export.

This is a structural manifest query, never proof of an obtainable drop,
enhanced perk, simultaneous selection, PvE DPS or PvP Guardian TTK.
Input schema is scripts/export_weapon_legality_evidence.py output.
"""
from datetime import datetime, timezone
from urllib.parse import urlsplit

DATASET_ID = "vaeltrion:weapon-structural-evidence"
GRADE = "official_manifest_structural_only"
STATES = (
    ("explicit_current_flag_plug_hashes", "explicit_current_flag"),
    ("explicit_noncurrent_flag_plug_hashes", "explicit_noncurrent_flag"),
    ("unknown_current_flag_plug_hashes", "unknown_current_flag"),
)


def _hash(value, field):
    if type(value) is not int or not 0 < value <= 0xFFFFFFFF:
        raise ValueError(f"{field} must be a positive unsigned 32-bit integer")
    return value


def _hash_list(values, field):
    if not isinstance(values, list):
        raise ValueError(f"{field} must be a list")
    for value in values:
        _hash(value, field)
    if len(values) != len(set(values)):
        raise ValueError(f"{field} contains duplicate hashes")
    return set(values)


def _validate_source(source):
    if not isinstance(source, dict):
        raise ValueError("Missing source provenance")
    url = source.get("url")
    if type(url) is not str:
        raise ValueError("Missing source URL")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ("bungie.net", "www.bungie.net"):
        raise ValueError("Untrusted manifest provenance")
    digest = source.get("sha256")
    if (type(digest) is not str or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)):
        raise ValueError("Missing source digest")


def _validate_index(index):
    if not isinstance(index, dict) or index.get("dataset_id") != DATASET_ID:
        raise ValueError("Unexpected weapon evidence dataset")
    if index.get("schema_version") != "1.0.0":
        raise ValueError("Unsupported evidence schema")
    version = index.get("manifest_version")
    if type(version) is not str or not version.strip():
        raise ValueError("Missing manifest version")
    stamp = index.get("retrieved_at_utc")
    if type(stamp) is not str:
        raise ValueError("Missing source timestamp")
    try:
        observed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid source timestamp") from exc
    if observed.tzinfo is None or observed.utcoffset() != timezone.utc.utcoffset(observed):
        raise ValueError("Source timestamp must be UTC")
    provenance = index.get("provenance")
    if (not isinstance(provenance, dict)
            or provenance.get("publisher") != "Bungie"
            or provenance.get("evidence_grade") != GRADE):
        raise ValueError("Untrusted evidence grade")
    for key in ("inventory_definition", "plug_set_definition"):
        _validate_source(provenance.get(key))
    weapons = index.get("weapons")
    if not isinstance(weapons, list) or type(index.get("weapon_count")) is not int:
        raise ValueError("Invalid weapon catalog")
    if len(weapons) != index["weapon_count"]:
        raise ValueError("Weapon count does not match catalog")
    hashes = []
    for item in weapons:
        if not isinstance(item, dict):
            raise ValueError("Malformed weapon record")
        hashes.append(_hash(item.get("item_hash"), "item_hash"))
        if item.get("id") != f"d2:weapon:{item['item_hash']}":
            raise ValueError("Weapon stable ID mismatch")
    if len(hashes) != len(set(hashes)):
        raise ValueError("Duplicate exact weapon hashes")
    return version, stamp, weapons


def _validate_sockets(item):
    sockets = item.get("sockets")
    if not isinstance(sockets, list):
        raise ValueError("Missing socket records")
    result = []
    seen = set()
    for socket in sockets:
        if not isinstance(socket, dict):
            raise ValueError("Malformed socket record")
        index = socket.get("socket_index")
        if type(index) is not int or index < 0 or index in seen:
            raise ValueError("Invalid or duplicated socket index")
        seen.add(index)
        base = _hash_list(socket.get("randomized_plug_hashes"), "randomized")
        partitions = [(field, label, _hash_list(socket.get(field), field))
                      for field, label in STATES]
        if any(a[2] & b[2] for i, a in enumerate(partitions) for b in partitions[i + 1:]):
            raise ValueError("Overlapping roll-state partitions")
        if base != set().union(*(entry[2] for entry in partitions)):
            raise ValueError("Incomplete roll-state partition")
        ref = socket.get("randomized_plug_set_hash")
        if base:
            _hash(ref, "randomized_plug_set_hash")
        elif ref is not None:
            _hash(ref, "randomized_plug_set_hash")
        result.append((index, partitions))
    return sorted(result)



def _current_flag_diagnostic(weapons):
    """Audit the *entire* snapshot, not only the queried item.

    An all-current manifest flag population cannot discriminate retired
    sockets. This is never evidence of current item acquisition.
    """
    counts = {
        "explicit_current_flag_memberships": 0,
        "explicit_noncurrent_flag_memberships": 0,
        "unknown_current_flag_memberships": 0,
    }
    for item in weapons:
        for _, partitions in _validate_sockets(item):
            for _, label, hashes in partitions:
                counts[label + "_memberships"] += len(hashes)
    total = sum(counts.values())
    return {
        "randomized_memberships": total,
        **counts,
        "current_flag_filter_discriminates_retired_memberships":
            counts["explicit_noncurrent_flag_memberships"] > 0,
        "all_randomized_memberships_flagged_current":
            total > 0 and counts["explicit_current_flag_memberships"] == total,
        "current_obtainability_certified": False,
        "enhanced_perk_legality_certified": False,
    }



def query_pair(index, *, item_hash, plug_a, plug_b, expected_manifest_version):
    """Find same-item, different-socket candidates, never certify legal rolls.

    explicit_current_flag is a Bungie plug flag, NOT live acquisition proof.
    """
    _hash(item_hash, "item_hash")
    _hash(plug_a, "plug_a")
    _hash(plug_b, "plug_b")
    if plug_a == plug_b:
        raise ValueError("Supply two distinct plug hashes")
    if type(expected_manifest_version) is not str or not expected_manifest_version.strip():
        raise ValueError("Expected manifest version is required")
    version, stamp, weapons = _validate_index(index)
    base = {
        "id": f"d2:weapon-pair:{item_hash}:{min(plug_a, plug_b)}:{max(plug_a, plug_b)}",
        "item_hash": item_hash,
        "plug_hashes": [plug_a, plug_b],
        "manifest_version": version,
        "source_retrieved_at_utc": stamp,
        "confidence_grade": GRADE,
        "patch_version": None,
        "patch_version_verified": False,
        "provenance": {
            "publisher": "Bungie",
            "inventory_definition": dict(index["provenance"]["inventory_definition"]),
            "plug_set_definition": dict(index["provenance"]["plug_set_definition"]),
        },
        "pve_boss_dps_measured": None,
        "pve_damage_resistance_measured": None,
        "pvp_guardian_damage_measured": None,
        "pvp_guardian_ttk_measured": None,
        "enhanced_perk_legal": None,
        "current_obtainable_roll": None,
        "certified_for_app_build_recommendation": False,
        "candidate_socket_pairs": [],
        "both_explicit_current_flags": False,
        "structural_candidate": False,
        "current_flag_filter_diagnostic": None,
    }
    if version != expected_manifest_version:
        return dict(base, status="manifest_version_mismatch")
    item = next((row for row in weapons if row["item_hash"] == item_hash), None)
    if item is None:
        return dict(base, status="item_hash_not_in_index")
    diagnostic = _current_flag_diagnostic(weapons)
    sockets = _validate_sockets(item)
    matches = []
    for left_index, left_states in sockets:
        for right_index, right_states in sockets:
            if left_index == right_index:
                continue
            left = next((label for _, label, hashes in left_states if plug_a in hashes), None)
            right = next((label for _, label, hashes in right_states if plug_b in hashes), None)
            if left is not None and right is not None:
                matches.append({
                    "plug_a_socket_index": left_index,
                    "plug_b_socket_index": right_index,
                    "plug_a_state": left,
                    "plug_b_state": right,
                })
    matches.sort(key=lambda r: (r["plug_a_socket_index"], r["plug_b_socket_index"]))
    return dict(
        base,
        status="structural_candidate_only" if matches else "no_distinct_socket_membership",
        candidate_socket_pairs=matches,
        current_flag_filter_diagnostic=diagnostic,
        structural_candidate=bool(matches),
        both_explicit_current_flags=any(
            row["plug_a_state"] == row["plug_b_state"] == "explicit_current_flag"
            for row in matches),
    )
