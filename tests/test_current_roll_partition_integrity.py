"""Synthetic regression: a manifest roll-state partition must be complete and unique."""
import unittest

from scripts.query_weapon_pairs import current_roll_filter_diagnostic


def snapshot(base, current, retired=(), unknown=()):
    return [{"item_type": 3, "item_hash": 101, "name": "Synthetic",
             "sockets": [{
                 "socket_index": 2,
                 "randomized_candidate_plug_hashes": list(base),
                 "currently_rollable_randomized_candidate_plug_hashes": list(current),
                 "noncurrent_randomized_candidate_plug_hashes": list(retired),
                 "unknown_current_roll_randomized_candidate_plug_hashes": list(unknown),
             }]}]


class RollPartitionIntegrityTests(unittest.TestCase):
    def test_complete_all_current_remains_structural_only(self):
        report = current_roll_filter_diagnostic(snapshot((11, 22), (11, 22)))
        self.assertEqual(report["invalid_membership_rows"], 0)
        self.assertFalse(report["current_obtainability_certified"])

    def test_unclassified_membership_is_invalid_not_current(self):
        report = current_roll_filter_diagnostic(snapshot((11, 22), (11,)))
        self.assertEqual(report["status"], "invalid_membership_rows_require_review")
        self.assertEqual(report["invalid_membership_rows"], 1)
        self.assertFalse(report["current_roll_filter_discriminates_retired_memberships"])

    def test_duplicate_current_hash_is_invalid(self):
        report = current_roll_filter_diagnostic(snapshot((11, 22), (11, 11), (22,)))
        self.assertEqual(report["invalid_membership_rows"], 1)

    def test_duplicate_base_hash_is_invalid(self):
        report = current_roll_filter_diagnostic(snapshot((11, 11), (11,)))
        self.assertEqual(report["invalid_membership_rows"], 1)

    def test_complete_three_way_partition_is_valid_but_not_drop_proof(self):
        report = current_roll_filter_diagnostic(
            snapshot((11, 22, 33), (11,), (22,), (33,)))
        self.assertEqual(report["invalid_membership_rows"], 0)
        self.assertEqual(report["unknown_memberships"], 1)
        self.assertTrue(report["current_roll_filter_discriminates_retired_memberships"])
        self.assertFalse(report["current_obtainability_certified"])
        self.assertFalse(report["enhanced_perk_legality_certified"])


if __name__ == "__main__":
    unittest.main()
