import unittest
from simulator.candidate_comparison import compare_candidates

class CandidateComparisonTests(unittest.TestCase):
    def setUp(self):
        self.weights = {"damage": 2, "survivability": 1, "uptime": 1}
        self.good = {"id": "A", "class": "titan", "legal": True,
                     "artifact_checked": True,
                     "metrics": {"damage": 0.8, "survivability": 0.5, "uptime": 0.5}}

    def test_ranked_but_never_certified(self):
        result = compare_candidates([self.good], self.weights)
        self.assertEqual(result[0]["score"], 0.65)
        self.assertFalse(result[0]["certified_build"])

    def test_missing_metric_excluded(self):
        bad = {**self.good, "metrics": {"damage": 1, "survivability": 1}}
        self.assertEqual(compare_candidates([bad], self.weights), [])

    def test_unchecked_artifact_excluded(self):
        bad = {**self.good, "artifact_checked": False}
        self.assertEqual(compare_candidates([bad], self.weights), [])

    def test_nan_excluded(self):
        bad = {**self.good, "metrics": {**self.good["metrics"], "damage": float("nan")}}
        self.assertEqual(compare_candidates([bad], self.weights), [])

    def test_invalid_weights_rejected(self):
        with self.assertRaises(ValueError):
            compare_candidates([self.good], {"damage": 1})

if __name__ == "__main__":
    unittest.main()
