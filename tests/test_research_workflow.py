import unittest
from pathlib import Path
from simulator.patch_import import load_patch_notes
from simulator.calibration import calibration_report
from simulator.discovery_review import review_queue

ROOT = Path(__file__).resolve().parents[1]

class ResearchWorkflowTests(unittest.TestCase):
    def test_official_patch_import(self):
        data = load_patch_notes(ROOT / "data" / "official_sandbox_2026_06.json")
        self.assertEqual(data["game_version"], "9.7.0")
        self.assertEqual(len(data["observations"]), 3)
        self.assertEqual(data["observations"][0]["new_value"], 27.1)

    def test_calibration_errors(self):
        report = calibration_report([10, 20, 30], [11, 19, 30])
        self.assertAlmostEqual(report["mean_absolute_error"], 2 / 3)
        self.assertFalse(report["validated_in_game"])

    def test_mismatched_calibration_rejected(self):
        with self.assertRaises(ValueError):
            calibration_report([10, 20], [10])

    def test_review_queue_not_certified(self):
        ranked = [{"id": "titan", "class": "titan", "score": .9,
                   "certified_build": False}]
        result = review_queue(ranked)
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]["certified_build"])

    def test_review_rejects_unverified_certification_flag(self):
        self.assertEqual(review_queue([{"score": 1, "certified_build": True}]), [])

if __name__ == "__main__":
    unittest.main()
