"""Forge build certification: fail closed on missing evidence.

Usage: python -m forge_certify path/to/build.json
No game mechanic is treated as measured without an evidence record.
"""
import json
import sys
from datetime import date

CRITICAL = ("artifact", "stacking", "subclass", "armor", "weapons", "stats", "rotation")

def certify(build, as_of=None):
    as_of = as_of or date.today().isoformat()
    checks = {}
    artifact = build.get("artifact", {})
    picks = artifact.get("selected", [])
    catalog = artifact.get("catalog", {})
    budget = artifact.get("budget")
    if not catalog or budget is None or not picks:
        checks["artifact"] = "BLOCKED: missing catalog, budget or selections"
    elif len(picks) != len(set(picks)) or len(picks) > budget:
        checks["artifact"] = "FAIL: duplicate selections or exceeded budget"
    elif any(p not in catalog for p in picks):
        checks["artifact"] = "FAIL: unknown Artifact perk"
    elif any(not catalog[p].get("source") or not catalog[p].get("verified_on") for p in picks):
        checks["artifact"] = "BLOCKED: selection lacks dated evidence"
    elif artifact.get("valid_on") != as_of or not artifact.get("unlock_rules_verified"):
        checks["artifact"] = "BLOCKED: current-date or unlock legality not verified"
    else:
        checks["artifact"] = "PASS"
    effects = build.get("effects", [])
    if not effects:
        checks["stacking"] = "BLOCKED: no effect interactions"
    elif any(not all(e.get(k) for k in ("trigger", "stack_group", "stack_rule", "source", "verified_on")) for e in effects):
        checks["stacking"] = "BLOCKED: incomplete stacking evidence"
    elif any(e.get("evidence") not in ("measured", "official") for e in effects):
        checks["stacking"] = "BLOCKED: simulated or unknown stacking"
    else:
        checks["stacking"] = "PASS"
    for field in ("subclass", "armor", "weapons", "stats", "rotation"):
        value = build.get(field)
        checks[field] = "PASS" if value and build.get("audits", {}).get(field) == "verified" else "BLOCKED: missing or unaudited"
    return {"build": build.get("name", "unnamed"), "as_of": as_of,
            "status": "CERTIFIED" if all(v == "PASS" for v in checks.values()) else "NOT_CERTIFIED",
            "checks": checks}

if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        result = certify(json.load(f))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "CERTIFIED" else 1)
