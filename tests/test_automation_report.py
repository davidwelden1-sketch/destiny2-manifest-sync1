import unittest
from pathlib import Path
from simulator.automation_report import generate_report

class AutomationReportTests(unittest.TestCase):
    def test_inventory_is_conservative(self):
        root = Path(__file__).resolve().parents[1]
        result = generate_report(root)
        self.assertGreater(result["source_count"], 0)
        self.assertEqual(result["certified_builds"], 0)
        self.assertEqual(result["current_verified_measurements"], 0)
        self.assertEqual(result["automated_candidate_search"],
                         "not_run_no_verified_current_inputs")

    def test_explicit_outdated_sources_quarantined(self):
        root = Path(__file__).resolve().parents[1]
        result = generate_report(root)
        self.assertIn("clarity_stats", result["quarantined_sources"])
        self.assertIn("pvp_damage", result["quarantined_sources"])

if __name__ == "__main__":
    unittest.main()
