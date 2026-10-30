"""Synthetic metadata tests, not in-game calibration measurements."""
import unittest
from simulator.source_freshness import source_suitability


class SourceVersionActivityGateTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "independent_measurement": True,
            "independently_reviewed": True,
            "game_version": "9.7.0.6",
            "measured_on": "2026-10-20",
            "activity": "pve",
        }

    def screen(self, record=None, **kwargs):
        return source_suitability(record or self.record, "2026-10-30", **kwargs)

    def test_matching_version_and_pve_activity_is_only_metadata_screen(self):
        result = self.screen(current_game_version="9.7.0.6", activity="pve")
        self.assertTrue(result["usable_for_current_calibration"])
        self.assertEqual(result["reason"], "metadata_screen_only_not_gameplay_proof")

    def test_stale_game_version_rejected(self):
        self.assertEqual(self.screen(current_game_version="9.7.0.7")["reason"],
                         "game_version_mismatch")

    def test_pvp_measurement_cannot_calibrate_pve(self):
        self.assertEqual(self.screen({**self.record, "activity": "pvp"}, activity="pve")["reason"],
                         "activity_mismatch")

    def test_missing_activity_cannot_calibrate_activity_specific_model(self):
        self.assertEqual(self.screen({k: v for k, v in self.record.items() if k != "activity"},
                                     activity="pvp")["reason"], "measurement_activity_missing")

    def test_unrecognized_activity_is_not_silently_mapped(self):
        self.assertEqual(self.screen({**self.record, "activity": "crucible"}, activity="pvp")["reason"],
                         "measurement_activity_missing")

    def test_empty_version_constraint_fails_closed(self):
        with self.assertRaises(ValueError):
            self.screen(current_game_version="")

    def test_unknown_requested_activity_fails_closed(self):
        with self.assertRaises(ValueError):
            self.screen(activity="trials")

    def test_explicit_outdated_warning_still_precedes_matching_version(self):
        result = self.screen({**self.record, "explicitly_outdated": True},
                             current_game_version="9.7.0.6", activity="pve")
        self.assertEqual(result["reason"], "explicit_outdated_warning")

    def test_legacy_call_without_constraints_remains_compatible(self):
        self.assertTrue(source_suitability(self.record, "2026-10-30")["usable_for_current_calibration"])


if __name__ == "__main__":
    unittest.main()
