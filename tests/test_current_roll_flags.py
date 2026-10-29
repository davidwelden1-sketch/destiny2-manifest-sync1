"""Synthetic regression tests for official per-plug currentlyCanRoll semantics."""
import unittest

from scripts.build_socket_candidates import build_index, classify_roll_flags
from scripts.query_weapon_pairs import find_pair_candidates, summarize


class TestCurrentRollFlags(unittest.TestCase):
    def setUp(self):
        self.items = [{"hash": 101, "name": "Versioned weapon", "itemType": 3,
                       "equippable": True, "socketEntries": [
                           {"randomizedPlugSetHash": 10},
                           {"randomizedPlugSetHash": 11}]}]
        self.plugsets = {"10": [20, 21, 22, 23], "11": [30, 31]}
        self.flags = {
            "10": [{"plugItemHash": 20, "currentlyCanRoll": True},
                   {"plugItemHash": 21, "currentlyCanRoll": False},
                   {"plugItemHash": 22, "currentlyCanRoll": None},
                   {"plugItemHash": 23, "currentlyCanRoll": True},
                   {"plugItemHash": 23, "currentlyCanRoll": False}],
            "11": [{"plugItemHash": 30, "currentlyCanRoll": True},
                   {"plugItemHash": 31, "currentlyCanRoll": False}]}
        self.index = build_index(self.items, self.plugsets, self.flags)

    def test_three_way_classification_and_conflict(self):
        socket = self.index[0]["sockets"][0]
        self.assertEqual(socket["randomized_candidate_plug_hashes"], [20, 21, 22, 23])
        self.assertEqual(socket["currently_rollable_randomized_candidate_plug_hashes"], [20])
        self.assertEqual(socket["noncurrent_randomized_candidate_plug_hashes"], [21])
        self.assertEqual(socket["unknown_current_roll_randomized_candidate_plug_hashes"], [22, 23])

    def test_current_only_requires_both_explicit_true(self):
        self.assertEqual(len(find_pair_candidates(self.index, 20, 30, True)), 1)
        self.assertEqual(find_pair_candidates(self.index, 21, 30, True), [])
        self.assertEqual(find_pair_candidates(self.index, 22, 30, True), [])
        self.assertEqual(find_pair_candidates(self.index, 23, 30, True), [])
        self.assertEqual(find_pair_candidates(self.index, 20, 31, True), [])
        self.assertEqual(len(find_pair_candidates(self.index, 21, 30)), 1)
        self.assertEqual(find_pair_candidates(self.index, 20, 21, True), [])

    def test_absent_flag_file_is_unknown_not_current(self):
        index = build_index(self.items, self.plugsets)
        s = index[0]["sockets"][0]
        self.assertEqual(s["currently_rollable_randomized_candidate_plug_hashes"], [])
        self.assertEqual(s["unknown_current_roll_randomized_candidate_plug_hashes"],
                         [20, 21, 22, 23])
        self.assertEqual(find_pair_candidates(index, 20, 30, True), [])

    def test_summary_counts_memberships_not_unique_perks(self):
        report = summarize(self.index, "test")
        self.assertEqual(report["currently_rollable_randomized_plug_memberships"], 2)
        self.assertEqual(report["noncurrent_randomized_plug_memberships"], 2)
        self.assertEqual(report["unknown_current_roll_plug_memberships"], 2)

    def test_boolean_hashes_fail_closed(self):
        for a, b in [(True, 30), (20, False)]:
            with self.assertRaises(ValueError):
                find_pair_candidates(self.index, a, b)

    def test_missing_and_conflicting_flags_unknown(self):
        a, b, c = classify_roll_flags({1, 2, 3},
            [{"plugItemHash": 1, "currentlyCanRoll": True},
             {"plugItemHash": 1, "currentlyCanRoll": False},
             {"plugItemHash": 2, "currentlyCanRoll": False}])
        self.assertEqual(a, set())
        self.assertEqual(b, {2})
        self.assertEqual(c, {1, 3})


    def test_all_true_manifest_is_explicitly_non_discriminating(self):
        all_true = {"10": [{"plugItemHash": h, "currentlyCanRoll": True}
                           for h in self.plugsets["10"]],
                    "11": [{"plugItemHash": h, "currentlyCanRoll": True}
                           for h in self.plugsets["11"]]}
        index = build_index(self.items, self.plugsets, all_true)
        report = summarize(index, "test")
        self.assertEqual(report["currently_rollable_randomized_plug_memberships"], 6)
        self.assertEqual(report["noncurrent_randomized_plug_memberships"], 0)
        self.assertFalse(report["explicit_noncurrent_roll_evidence_found"])
        self.assertIn("cannot distinguish retired rolls", report["roll_flag_caveat"])


if __name__ == "__main__":
    unittest.main()
