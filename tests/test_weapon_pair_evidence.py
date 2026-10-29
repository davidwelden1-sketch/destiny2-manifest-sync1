import unittest

from scripts.build_socket_candidates import build_index
from scripts.query_weapon_pairs import find_pair_candidates, summarize


class TestWeaponPairEvidence(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"hash": 100, "name": "Test weapon", "equippable": True, "itemType": 3,
             "socketEntries": [
                 {"socketTypeHash": 91, "randomizedPlugSetHash": 10, "reusablePlugSetHash": 11},
                 {"socketTypeHash": 92, "randomizedPlugSetHash": 12},
                 {"socketTypeHash": 93, "singleInitialItemHash": 99}]},
            {"hash": 101, "name": "Same socket only", "equippable": True, "itemType": 3,
             "socketEntries": [{"randomizedPlugSetHash": 13}]},
            {"hash": 102, "name": "Armor decoy", "equippable": True, "itemType": 2,
             "socketEntries": [{"randomizedPlugSetHash": 10},
                               {"randomizedPlugSetHash": 12}]},
        ]
        self.index = build_index(self.items, {
            "10": [20, 30], "11": [30, 40], "12": [50],
            "13": [20, 50]})

    def test_source_separation_prevents_reusable_only_false_positive(self):
        socket = self.index[0]["sockets"][0]
        self.assertEqual(socket["candidate_plug_hashes"], [20, 30, 40])
        self.assertEqual(socket["randomized_candidate_plug_hashes"], [20, 30])
        self.assertEqual(socket["reusable_candidate_plug_hashes"], [30, 40])
        self.assertEqual(find_pair_candidates(self.index, 40, 50), [])

    def test_two_distinct_randomized_sockets_have_auditable_source(self):
        rows = find_pair_candidates(self.index, 20, 50)
        self.assertEqual([x["item_hash"] for x in rows], [100])
        self.assertEqual(rows[0]["socket_pairs"][0]["a_socket_index"], 0)
        self.assertEqual(rows[0]["socket_pairs"][0]["b_socket_index"], 1)
        self.assertEqual(rows[0]["socket_pairs"][0]["a_randomized_set_hashes"], [10])
        self.assertEqual(rows[0]["socket_pairs"][0]["b_randomized_set_hashes"], [12])
        self.assertEqual(rows[0]["enhanced_perk_legality"], "unverified")

    def test_initial_only_is_not_randomized(self):
        self.assertEqual(find_pair_candidates(self.index, 20, 99), [])

    def test_same_socket_cannot_pair(self):
        self.assertEqual(find_pair_candidates(self.index, 20, 30), [])

    def test_hash_validation(self):
        for a, b in [(0, 20), (20, 20), (-1, 30)]:
            with self.assertRaises(ValueError):
                find_pair_candidates(self.index, a, b)

    def test_summary_does_not_claim_unique_playable_weapons(self):
        report = summarize(self.index, "test-manifest")
        self.assertEqual(report["indexed_weapon_definitions"], 2)
        self.assertEqual(report["weapon_definitions_with_two_or_more_randomized_sockets"], 1)
        self.assertEqual(report["randomized_socket_entries"], 3)
        self.assertIn("not unique playable weapons", report["interpretation"])
