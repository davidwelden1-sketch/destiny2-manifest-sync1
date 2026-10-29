import unittest
from simulator.sensitivity_search import robust_rank

WEIGHTS = {"damage": 1, "survivability": 1, "uptime": 1}
class SensitivitySearchTests(unittest.TestCase):
    def test_worst_case_ranking(self):
        candidates = [
            {"id": "a", "class": "hunter", "artifact_perks": ["synthetic_a"],
             "metric_ranges": {"damage": (.4, .9), "survivability": (.4, .9), "uptime": (.4, .9)}},
            {"id": "b", "class": "titan", "artifact_perks": ["synthetic_b"],
             "metric_ranges": {"damage": (.6, .7), "survivability": (.6, .7), "uptime": (.6, .7)}},
        ]
        result = robust_rank(candidates, WEIGHTS)
        self.assertEqual(result[0]["id"], "b")
        self.assertFalse(result[0]["certified_build"])

    def test_invalid_range_excluded(self):
        result = robust_rank([{"id": "x", "class": "warlock", "artifact_perks": ["test"],
             "metric_ranges": {"damage": (.9, .1), "survivability": (.2, .3),
                               "uptime": (.2, .3)}}], WEIGHTS)
        self.assertEqual(result, [])

    def test_missing_artifact_excluded(self):
        result = robust_rank([{"id": "x", "class": "warlock", "artifact_perks": [],
             "metric_ranges": {"damage": (.2, .3), "survivability": (.2, .3),
                               "uptime": (.2, .3)}}], WEIGHTS)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
