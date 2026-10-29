import unittest
from simulator.measurement_aggregation import summarize_measurements

class MeasurementAggregationTests(unittest.TestCase):
    def setUp(self):
        self.records = [{"metric": "precision_damage", "game_version": "test",
                         "activity": "private_match", "scenario": "unbuffed",
                         "unit": "damage", "value": v,
                         "source_url": "https://example.org/test"}
                        for v in (70, 71, 72)]

    def test_summary_and_uncertainty(self):
        result = summarize_measurements(self.records)
        self.assertEqual(result["mean"], 71)
        self.assertEqual(result["sample_stdev"], 1)
        self.assertEqual(result["count"], 3)
        self.assertFalse(result["verified_in_game"])

    def test_mixed_versions_rejected(self):
        records = [dict(r) for r in self.records]
        records[1]["game_version"] = "different"
        with self.assertRaises(ValueError):
            summarize_measurements(records)

    def test_nonfinite_rejected(self):
        records = [dict(r) for r in self.records]
        records[0]["value"] = float("nan")
        with self.assertRaises(ValueError):
            summarize_measurements(records)

    def test_insufficient_samples(self):
        with self.assertRaises(ValueError):
            summarize_measurements(self.records[:2])

    def test_missing_source(self):
        records = [dict(r) for r in self.records]
        del records[0]["source_url"]
        with self.assertRaises(ValueError):
            summarize_measurements(records)

if __name__ == "__main__":
    unittest.main()
