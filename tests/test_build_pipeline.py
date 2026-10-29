import unittest
from simulator.build_pipeline import evaluate_candidates
from simulator.loadout_completeness import REQUIRED_LOADOUT

class BuildPipelineTests(unittest.TestCase):
    def setUp(self):
        self.weights = {"damage": 1, "survivability": 1, "uptime": 1}
        self.build = {key: "placeholder" for key in REQUIRED_LOADOUT}
        self.build.update({"id": "test", "class": "titan", "activity": "raid",
                           "artifact_id": "active", "artifact_perks": ["A"],
                           "weapon_legality_checked": True,
                           "metrics": {"damage": .5, "survivability": .8, "uptime": .9}})
        self.catalog = {"active": ["A"]}

    def test_complete_preliminary_candidate(self):
        result = evaluate_candidates([self.build], self.catalog, self.weights)
        self.assertEqual(len(result["ranked"]), 1)
        self.assertEqual(result["certified_builds"], 0)

    def test_cross_artifact_rejected(self):
        bad = {**self.build, "artifact_perks": ["B"]}
        result = evaluate_candidates([bad], self.catalog, self.weights)
        self.assertEqual(result["ranked"], [])

    def test_weapon_legality_gate(self):
        bad = {**self.build, "weapon_legality_checked": False}
        result = evaluate_candidates([bad], self.catalog, self.weights)
        self.assertEqual(result["ranked"], [])

    def test_incomplete_loadout(self):
        bad = {**self.build, "fragments": []}
        result = evaluate_candidates([bad], self.catalog, self.weights)
        self.assertEqual(result["ranked"], [])

if __name__ == "__main__":
    unittest.main()
