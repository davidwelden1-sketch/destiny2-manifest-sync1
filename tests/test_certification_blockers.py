import unittest
from forge_certify import certify

class CertificationBlockerTests(unittest.TestCase):
    def test_empty_build_has_actionable_blockers(self):
        result = certify({}, as_of="2026-10-29")
        self.assertEqual(result["status"], "NOT_CERTIFIED")
        self.assertEqual(result["blocker_count"], 10)
        self.assertEqual(len(result["blockers"]), 10)
        self.assertTrue(all(b["next_action"] for b in result["blockers"]))

    def test_unverified_gameplay_never_passes(self):
        result = certify({"weapon_roll_evidence": [{"item_hash": 1, "roll_legal": True}]}, as_of="2026-10-29")
        self.assertNotEqual(result["status"], "CERTIFIED")
        self.assertNotEqual(result["checks"]["weapon_legality"], "PASS")
        self.assertNotEqual(result["checks"]["defensive_uptime"], "PASS")
        self.assertNotEqual(result["checks"]["gameplay_evidence"], "PASS")

    def test_missing_artifact_is_explicit(self):
        result = certify({"name": "Titan Zero"}, as_of="2026-10-29")
        self.assertEqual(result["blockers"][0]["check"], "artifact")
        self.assertIn("Artifact", result["blockers"][0]["next_action"])

if __name__ == "__main__":
    unittest.main()
