import unittest
from scripts.index_ability_candidates import classify_candidates

class TestAbilityCandidates(unittest.TestCase):
    def test_keyword_classification_is_unverified(self):
        items = [
            {"hash": 10, "name": "Example Grenade", "classType": 0},
            {"hash": 11, "name": "Example Weapon", "classType": 3},
        ]
        rows = classify_candidates(items)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["hash"], 10)
        self.assertEqual(rows[0]["ability_legality"], "unverified")

    def test_missing_name_skipped(self):
        self.assertEqual(classify_candidates([{"hash": 1, "name": ""}]), [])
