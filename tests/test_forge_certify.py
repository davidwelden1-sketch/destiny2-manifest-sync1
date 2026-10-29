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

    def test_structural_checks_are_not_evidence_validation(self):
        b = {"name":"fabricated", "artifact":{"selected":["A"],"budget":7,
             "catalog":{"A":{"source":"unverified","verified_on":"2026-10-29","tier":1}},
             "valid_on":"2026-10-29","unlock_rules_verified":True,"allocation_verified":True,"season_id":"unknown"},
             "effects":[{"trigger":"jolt","stack_group":"DR","stack_rule":"multiplicative",
              "source":"unverified","verified_on":"2026-10-29","evidence":"official",
              "evidence_url":"https://example.invalid","interaction_verified":True}],
             "audits":{x:"verified" for x in ("subclass","armor","weapons","stats","rotation")},
             "audit_sources":{x:"https://example.invalid" for x in ("subclass","armor","weapons","stats","rotation")}}
        b.update({x:{"selected":"placeholder"} for x in ("subclass","armor","weapons","stats","rotation")})
        # This tests structural checks only: actual evidence must be checked externally.
        self.assertEqual(certify(b, "2026-10-29")["status"], "CERTIFIED")

if __name__ == "__main__":
    unittest.main()
