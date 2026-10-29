"""Read-only checks for simulator evidence and candidate index artifacts."""
import json
import sys
from pathlib import Path

SOURCE_KEYS = ("randomized_candidate_plug_hashes", "reusable_candidate_plug_hashes",
               "initial_candidate_plug_hashes")


def audit(root):
    root = Path(root)
    report = json.loads((root / "validation_report.json").read_text())
    candidates = json.loads((root / "item_socket_candidates.json").read_text())
    errors = []
    if not report.get("manifest_version"):
        errors.append("Missing manifest version")
    hashes = [x["item_hash"] for x in candidates]
    if hashes != sorted(set(hashes)):
        errors.append("Candidate index not sorted and unique")
    for item in candidates:
        if item.get("roll_legality") != "unverified":
            errors.append("Unexpected legality certification")
        if item.get("enhanced_perk_legality", "unverified") != "unverified":
            errors.append("Unexpected enhanced legality certification")
        seen_socket_indices = set()
        for socket in item.get("sockets", []):
            index = socket.get("socket_index")
            if index is not None:
                if index in seen_socket_indices:
                    errors.append("Duplicate socket index")
                seen_socket_indices.add(index)
            plugs = socket.get("candidate_plug_hashes", [])
            if plugs != sorted(set(plugs)):
                errors.append("Candidate plugs not sorted and unique")
            if any(k in socket for k in SOURCE_KEYS):
                union = set()
                for key in SOURCE_KEYS:
                    values = socket.get(key, [])
                    if values != sorted(set(values)):
                        errors.append("Source-specific plugs not sorted and unique")
                    union.update(values)
                if sorted(union) != plugs:
                    errors.append("Candidate union disagrees with source-specific plugs")
                fields = {r.get("field") for r in socket.get("plugset_references", [])}
                for key, field in zip(SOURCE_KEYS,
                                      ("randomizedPlugSetHash", "reusablePlugSetHash",
                                       "singleInitialItemHash")):
                    if socket.get(key) and field not in fields:
                        errors.append("Candidate source missing plugset reference")
    result = {"candidate_items": len(candidates), "errors": errors,
              "manifest_version": report.get("manifest_version")}
    (root / "candidate_audit.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    result = audit(sys.argv[1] if len(sys.argv) > 1 else "output")
    print(json.dumps(result))
    if result["errors"]:
        raise SystemExit(1)
