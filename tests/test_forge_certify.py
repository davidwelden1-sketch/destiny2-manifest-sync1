import unittest
from forge_certify import certify

class ForgeCertificationTests(unittest.TestCase):
    def test_empty_build_is_blocked(self):
        r = certify({})
        self.assertEqual(r["status"], "NOT_CERTIFIED")
        self.assertTrue(all(v.startswith("BLOCKED") for v in r["checks"].values()))

    def test_duplicate_artifact_is_rejected(self):
        b = {"artifact": {"selected": ["A", "A"], "budget": 7, "catalog": {"A": {"source": "official", "verified_on": "2026-10-29"}}}}
        self.assertTrue(certify(b)["checks"]["artifact"].startswith("FAIL"))

    def test_unmeasured_stacking_is_blocked(self):
        b = {"effects": [{"trigger":"jolt", "stack_group":"resist", "stack_rule":"multiplicative",
                         "source":"theory", "verified_on":"2026-10-29", "evidence":"simulated"}]}
        self.assertTrue(certify(b)["checks"]["stacking"].startswith("BLOCKED"))

    def test_expired_artifact_is_blocked(self):
        b = {"artifact": {"selected":["A"], "budget":7, "catalog":{"A":{"source":"official","verified_on":"2026-10-01"}},
                          "valid_on":"2026-10-01", "unlock_rules_verified":True}}
        self.assertTrue(certify(b, "2026-10-29")["checks"]["artifact"].startswith("BLOCKED"))

if __name__ == "__main__":
    unittest.main()
