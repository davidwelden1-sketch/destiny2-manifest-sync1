import unittest
from simulator.certification_gate import phase_status, build_certified, REQUIRED

class CertificationGateTests(unittest.TestCase):
    def test_missing_evidence_fails_closed(self):
        result = phase_status(1, {"manifest": "verified"})
        self.assertFalse(result["complete"])
        self.assertIn("exact_hash", result["gaps"])

    def test_invalid_phase_rejected(self):
        with self.assertRaises(ValueError):
            phase_status(5, {})

    def test_complete_evidence(self):
        phases = {p: {k: "verified" for k in keys} for p, keys in REQUIRED.items()}
        self.assertTrue(build_certified(phases, "strike", artifact_selected=True))
        self.assertFalse(build_certified(phases, "Trials", artifact_selected=True))
        self.assertFalse(build_certified(phases, "Competitive", artifact_selected=True))
        self.assertTrue(build_certified(phases, "Competitive", artifact_selected=False))

    def test_one_unverified_phase_blocks_build(self):
        phases = {p: {k: "verified" for k in keys} for p, keys in REQUIRED.items()}
        phases[2]["calibration"] = "hypothesis"
        self.assertFalse(build_certified(phases, "raid"))

if __name__ == "__main__":
    unittest.main()
