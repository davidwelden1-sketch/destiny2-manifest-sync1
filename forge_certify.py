"""Fail-closed Forge build certification. Evidence is not inferred from names."""
import json
import sys
from datetime import date, datetime

CRITICAL = ("artifact", "stacking", "subclass", "armor", "weapons", "stats", "rotation")
def _dated(s, as_of):
    try:
        return bool(s) and date.fromisoformat(s) <= date.fromisoformat(as_of)
    except (ValueError, TypeError):
        return False

def certify(build, as_of=None):
    as_of = as_of or date.today().isoformat()
    checks = {}
    a = build.get("artifact") or {}
    picks = a.get("selected") or []
    catalog = a.get("catalog") or {}
    budget = a.get("budget")
    if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0 or not catalog or not picks:
        checks["artifact"] = "BLOCKED: missing valid catalog, budget or selections"
    elif len(picks) != len(set(picks)) or len(picks) > budget:
        checks["artifact"] = "FAIL: duplicate selections or exceeded budget"
    elif any(p not in catalog for p in picks):
        checks["artifact"] = "FAIL: unknown Artifact perk"
    elif any(not catalog[p].get("source") or not _dated(catalog[p].get("verified_on"), as_of) for p in picks):
        checks["artifact"] = "BLOCKED: perk lacks valid dated source"
    elif not _dated(a.get("valid_on"), as_of) or not a.get("unlock_rules_verified") or not a.get("season_id"):
        checks["artifact"] = "BLOCKED: Artifact version or unlock rules not established"
    elif any(type(catalog[p].get("tier")) is not int or catalog[p]["tier"] not in (1, 2, 3) for p in picks):
        checks["artifact"] = "BLOCKED: tier data missing"
    elif sum(catalog[p]["tier"] == 3 for p in picks) > 2 or sum(catalog[p]["tier"] >= 2 for p in picks) > 5:
        checks["artifact"] = "FAIL: seven-slot 2/3/2 tier allocation exceeded"
    elif not a.get("allocation_verified"):
        checks["artifact"] = "BLOCKED: tier allocation not independently validated"
    else:
        checks["artifact"] = "PASS"

    effects = build.get("effects") or []
    if not effects:
        checks["stacking"] = "BLOCKED: no effect interactions"
    elif any(not all(e.get(k) for k in ("trigger", "stack_group", "stack_rule", "source", "verified_on")) or not _dated(e.get("verified_on"), as_of) for e in effects):
        checks["stacking"] = "BLOCKED: incomplete or future-dated stacking evidence"
    elif any(e.get("evidence") not in ("measured", "official") or not e.get("evidence_url") or not e.get("interaction_verified") for e in effects):
        checks["stacking"] = "BLOCKED: stacking interaction not independently evidenced"
    else:
        checks["stacking"] = "PASS"

    for field in ("subclass", "armor", "weapons", "stats", "rotation"):
        value = build.get(field)
        checks[field] = "PASS" if value and build.get("audits", {}).get(field) == "verified" and build.get("audit_sources", {}).get(field) else "BLOCKED: missing or unaudited"
    blockers = [{"check": k, "reason": v, "next_action": {
        "artifact": "Import current Artifact catalog and verify legal selection, tiers, unlocks, and activity",
        "stacking": "Attach official or measured evidence for each interaction and test combined effects",
        "subclass": "Validate aspects, fragments, abilities and activity legality",
        "armor": "Validate Exotic and armor mod legality",
        "weapons": "Validate manifest socket pools and obtainable perk combinations",
        "stats": "Validate stat totals, breakpoints and cooldown inputs",
        "rotation": "Validate triggers, durations and ability regeneration sequence",
    }[k]} for k, v in checks.items() if v != "PASS"]
    return {"build": build.get("name", "unnamed"), "as_of": as_of,
            "blockers": blockers, "blocker_count": len(blockers),
            "status": "READY_FOR_EVIDENCE_REVIEW" if all(v == "PASS" for v in checks.values()) else "NOT_CERTIFIED",
            "checks": checks}

if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        result = certify(json.load(f))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "CERTIFIED" else 1)
