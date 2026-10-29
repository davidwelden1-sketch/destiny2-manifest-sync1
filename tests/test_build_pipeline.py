import unittest
from simulator.build_pipeline import evaluate_candidates
from simulator.loadout_completeness import REQUIRED_LOADOUT

class BuildPipelineTests(unittest.TestCase):
    def setUp(self):
        self.weights = {"damage": 1, "survivability": 1, "uptime": 1}
        self.inventory = {123: {"sockets": {3: [301], 4: [401]}}}
        self.check = {"item_hash": 123, "left_index": 3, "left_plug": 301,
                      "right_index": 4, "right_plug": 401}
        self.build = {key: "placeholder" for key in REQUIRED_LOADOUT}
        self.build.update({"id": "test", "class": "titan", "activity": "raid",
                           "artifact_id": "active", "artifact_perks": ["A"],
                           "weapon_checks": [self.check],
                           "metrics": {"damage": .5, "survivability": .8, "uptime": .9}})
        self.catalog = {"active": ["A"]}

    def run_pipeline(self, build, inventory=None):
        return evaluate_candidates([build], self.catalog, self.weights,
                                   self.inventory if inventory is None else inventory)

    def test_manifest_membership_candidate_not_certified(self):
        result = self.run_pipeline(self.build)
        self.assertEqual(len(result["ranked"]), 1)
        self.assertEqual(result["certified_builds"], 0)
        self.assertEqual(result["weapon_verification"], "manifest_socket_membership_only")

    def test_cross_artifact_rejected(self):
        self.assertEqual(self.run_pipeline({**self.build, "artifact_perks": ["B"]})["ranked"], [])

    def test_self_reported_legality_not_accepted(self):
        bad = {**self.build, "weapon_checks": [], "weapon_legality_checked": True}
        self.assertEqual(self.run_pipeline(bad)["ranked"], [])

    def test_wrong_hash_rejected(self):
        bad = {**self.build, "weapon_checks": [{**self.check, "item_hash": 999}]}
        self.assertEqual(self.run_pipeline(bad)["ranked"], [])

    def test_wrong_socket_rejected(self):
        bad = {**self.build, "weapon_checks": [{**self.check, "right_index": 3}]}
        self.assertEqual(self.run_pipeline(bad)["ranked"], [])

    def test_incomplete_loadout(self):
        self.assertEqual(self.run_pipeline({**self.build, "fragments": []})["ranked"], [])

    def test_missing_inventory(self):
        result = evaluate_candidates([self.build], self.catalog, self.weights)
        self.assertEqual(result["ranked"], [])

if __name__ == "__main__":
    unittest.main()
