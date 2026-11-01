"""Regression tests: structural pairs must not survive contradictory roll-state data.

Synthetic hashes and memberships only; no claim about live Bungie drops.
"""
import unittest

from scripts.query_weapon_pairs import find_pair_candidates


def weapon(left=(11,), right=(22,)):
    def socket(index, base):
        return {
            "socket_index": index,
            "randomized_candidate_plug_hashes": list(base),
            "currently_rollable_randomized_candidate_plug_hashes": list(base),
            "noncurrent_randomized_candidate_plug_hashes": [],
            "unknown_current_roll_randomized_candidate_plug_hashes": [],
            "plugset_references": [],
            "default_visible": True,
        }
    return [{
        "item_type": 3, "item_hash": 500, "name": "Synthetic",
        "sockets": [socket(2, left), socket(3, right)],
    }]


class PairPartitionFailClosedTests(unittest.TestCase):
    def assert_rejected(self, rows):
        self.assertEqual(find_pair_candidates(rows, 11, 22), [])
        self.assertEqual(find_pair_candidates(rows, 11, 22, current_roll_only=True), [])

    def test_complete_partition_allows_structural_only_pair(self):
        rows = weapon()
        result = find_pair_candidates(rows, 11, 22, current_roll_only=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["roll_legality"], "unverified")
        self.assertEqual(result[0]["enhanced_perk_legality"], "unverified")

    def test_duplicate_base_membership_rejected(self):
        rows = weapon()
        rows[0]["sockets"][0]["randomized_candidate_plug_hashes"] = [11, 11]
        self.assert_rejected(rows)

    def test_duplicate_current_membership_rejected(self):
        rows = weapon()
        rows[0]["sockets"][0]["currently_rollable_randomized_candidate_plug_hashes"] = [11, 11]
        self.assert_rejected(rows)

    def test_current_and_retired_overlap_rejected(self):
        rows = weapon()
        rows[0]["sockets"][0]["noncurrent_randomized_candidate_plug_hashes"] = [11]
        self.assert_rejected(rows)

    def test_missing_partition_classification_rejected(self):
        rows = weapon()
        rows[0]["sockets"][0]["currently_rollable_randomized_candidate_plug_hashes"] = []
        self.assert_rejected(rows)

    def test_half_present_partition_rejected(self):
        rows = weapon()
        del rows[0]["sockets"][0]["unknown_current_roll_randomized_candidate_plug_hashes"]
        self.assert_rejected(rows)

    def test_corrupt_unrelated_socket_rejects_entire_weapon(self):
        rows = weapon()
        rows[0]["sockets"].append({
            "socket_index": 4,
            "randomized_candidate_plug_hashes": [33],
            "currently_rollable_randomized_candidate_plug_hashes": [33],
            "noncurrent_randomized_candidate_plug_hashes": [33],
            "unknown_current_roll_randomized_candidate_plug_hashes": [],
            "plugset_references": [],
        })
        self.assert_rejected(rows)

    def test_explicit_unknown_is_valid_structural_not_current(self):
        rows = weapon()
        left = rows[0]["sockets"][0]
        left["currently_rollable_randomized_candidate_plug_hashes"] = []
        left["unknown_current_roll_randomized_candidate_plug_hashes"] = [11]
        self.assertEqual(len(find_pair_candidates(rows, 11, 22)), 1)
        self.assertEqual(find_pair_candidates(rows, 11, 22, current_roll_only=True), [])


if __name__ == "__main__":
    unittest.main()
