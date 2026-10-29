import unittest
from simulator.measurement_aggregation import summarize_measurements
from simulator.measurement_comparison import compare_measurement_summaries

class MeasurementComparisonTests(unittest.TestCase):
    def samples(self, values, scenario="unbuffed"):
        return summarize_measurements([
            {"metric": "damage", "game_version": "test", "activity": "raid",
             "scenario": scenario, "unit": "damage", "value": v,
             "source_url": "https://example.org/test"} for v in values
        ])

    def test_difference(self):
        result = compare_measurement_summaries(
            self.samples([100, 101, 102]), self.samples([90, 91, 92]))
        self.assertEqual(result["difference"], 10)
        self.assertFalse(result["statistical_significance_claim"])

    def test_incompatible_scenario(self):
        with self.assertRaises(ValueError):
            compare_measurement_summaries(
                self.samples([100, 101, 102]), self.samples([90, 91, 92], "buffed"))

if __name__ == "__main__":
    unittest.main()
