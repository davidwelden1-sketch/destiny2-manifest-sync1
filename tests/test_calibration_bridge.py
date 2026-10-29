import unittest
from simulator.calibration_bridge import compare_predictions_to_summaries
from simulator.measurement_aggregation import summarize_measurements

class CalibrationBridgeTests(unittest.TestCase):
    def setUp(self):
        self.measurement = summarize_measurements([
            {"metric": "damage", "game_version": "test", "activity": "pvp",
             "scenario": "unbuffed", "unit": "damage", "value": v,
             "source_url": "https://example.org/test"} for v in (70, 71, 72)])
        self.pair = {"context": self.measurement["context"],
                     "measurement": self.measurement, "prediction": 72}

    def test_calibration_residual(self):
        result = compare_predictions_to_summaries([self.pair])
        self.assertEqual(result["mean_absolute_error"], 1)
        self.assertFalse(result["ready_for_certification"])

    def test_context_mismatch_rejected(self):
        bad = {**self.pair, "context": {**self.pair["context"], "activity": "pve"}}
        with self.assertRaises(ValueError):
            compare_predictions_to_summaries([bad])

    def test_unsourced_measurement_rejected(self):
        bad = {**self.measurement, "source_urls": []}
        with self.assertRaises(ValueError):
            compare_predictions_to_summaries([{**self.pair, "measurement": bad}])

if __name__ == "__main__":
    unittest.main()
