import unittest
from simulator.source_freshness import source_suitability

class SourceFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.source = {"independent_measurement": True, "independently_reviewed": True,
                       "game_version": "9.7.0.5", "measured_on": "2026-10-20"}

    def test_explicit_warning_overrides_recent_commit(self):
        self.assertEqual(source_suitability({**self.source, "explicitly_outdated": True,
            "repository_updated_on": "2026-10-29"}, "2026-10-29")["reason"],
            "explicit_outdated_warning")

    def test_unreviewed_source_rejected(self):
        result = source_suitability({**self.source, "independently_reviewed": False}, "2026-10-29")
        self.assertFalse(result["usable_for_current_calibration"])

    def test_future_date_rejected(self):
        result = source_suitability({**self.source, "measured_on": "2026-11-01"}, "2026-10-29")
        self.assertFalse(result["usable_for_current_calibration"])

    def test_metadata_only_not_gameplay_certification(self):
        self.assertEqual(source_suitability(self.source, "2026-10-29")["reason"],
                         "metadata_screen_only_not_gameplay_proof")

if __name__ == "__main__":
    unittest.main()
