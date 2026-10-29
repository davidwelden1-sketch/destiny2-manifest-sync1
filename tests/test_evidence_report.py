import unittest
from simulator.evidence_report import evidence_summary

class TestEvidenceSummary(unittest.TestCase):
    def test_counts_all_categories(self):
        result = evidence_summary([
            {"evidence_status": "official"},
            {"evidence_status": "measured"},
            {"evidence_status": "estimated"},
            {"evidence_status": "hypothetical"},
        ])
        self.assertEqual(result["verified_observations"], 2)
        self.assertEqual(result["unverified_observations"], 2)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValueError):
            evidence_summary([{"evidence_status": "unknown"}])
