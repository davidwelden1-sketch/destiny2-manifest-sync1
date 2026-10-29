import unittest
from simulator.calibration_eligibility import calibration_eligibility

class CalibrationEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.summary = {"status": "reported_measurements_not_independently_verified",
                        "context": {"game_version": "9.7.0.5"}, "count": 3,
                        "source_urls": ["https://example.org/test"]}
        self.review = {"source_urls": ["https://example.org/test"],
                       "reuse_permission_confirmed": True,
                       "independent_measurement": True,
                       "independently_reviewed": True,
                       "game_version": "9.7.0.5",
                       "measured_on": "2026-10-20"}
    def check(self, summary=None, review=None):
        return calibration_eligibility(
            self.summary if summary is None else summary,
            self.review if review is None else review,
            current_game_version="9.7.0.5", as_of="2026-10-29")

    def test_reviewed_metadata_only(self):
        result = self.check()
        self.assertTrue(result["eligible"])
        self.assertFalse(result["independently_reproduced"])

    def test_outdated_warning_blocks(self):
        self.assertEqual(self.check(review={**self.review, "explicitly_outdated": True})["reason"],
                         "explicit_outdated_warning")

    def test_unconfirmed_permission_blocks(self):
        self.assertEqual(self.check(review={**self.review, "reuse_permission_confirmed": False})["reason"],
                         "reuse_permission_unconfirmed")

    def test_wrong_sandbox_blocks(self):
        self.assertEqual(self.check(summary={**self.summary,
            "context": {"game_version": "old"}})["reason"], "sandbox_version_mismatch")

    def test_unreviewed_source_blocks(self):
        self.assertEqual(self.check(review={**self.review,
            "independently_reviewed": False})["reason"], "independent_review_pending")

    def test_wrong_source_blocks(self):
        self.assertEqual(self.check(review={**self.review,
            "source_urls": ["https://other.example.org"]})["reason"], "source_review_mismatch")

if __name__ == "__main__":
    unittest.main()
