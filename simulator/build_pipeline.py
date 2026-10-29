"""Conservative integration of manifest membership and build screening.

No manifest-only weapon check certifies a roll or its obtainability.
"""
from simulator.artifact_screen import screen_one_active_artifact
from simulator.loadout_completeness import loadout_gaps
from simulator.candidate_comparison import compare_candidates
from simulator.weapon_legality import check_pair

def evaluate_candidates(builds, artifact_catalog, weights, weapon_inventory=None):
    accepted, rejected = [], []
    for index, build in enumerate(builds):
        ident = build.get("id", index) if isinstance(build, dict) else index
        if not isinstance(build, dict):
            rejected.append((ident, "malformed_build"))
            continue
        if not loadout_gaps(build)["complete_fields"]:
            rejected.append((ident, "incomplete_loadout"))
            continue
        try:
            result = screen_one_active_artifact(build["class"], build["activity"],
                build.get("artifact_id"), build["artifact_perks"], artifact_catalog)
        except (ValueError, TypeError, KeyError):
            rejected.append((ident, "invalid_artifact_input"))
            continue
        if not result["eligible"]:
            rejected.append((ident, result["reason"]))
            continue
        checks = build.get("weapon_checks")
        if not isinstance(weapon_inventory, dict) or not isinstance(checks, (list, tuple)) or not checks:
            rejected.append((ident, "weapon_manifest_checks_required"))
            continue
        try:
            if any(not isinstance(c, dict) or
                   not check_pair(c["item_hash"], c["left_index"], c["left_plug"],
                                  c["right_index"], c["right_plug"], weapon_inventory)["possible"]
                   for c in checks):
                rejected.append((ident, "weapon_socket_membership_failed"))
                continue
        except (KeyError, TypeError, ValueError):
            rejected.append((ident, "invalid_weapon_check"))
            continue
        accepted.append({"id": ident, "class": build["class"], "legal": True,
                         "artifact_checked": True, "metrics": build.get("metrics")})
    ranked = compare_candidates(accepted, weights)
    ids = {r["id"] for r in ranked}
    rejected.extend((r["id"], "invalid_metrics") for r in accepted if r["id"] not in ids)
    return {"ranked": ranked, "rejected": rejected, "certified_builds": 0,
            "weapon_verification": "manifest_socket_membership_only"}
