"""Synthetic regression tests: structural current-roll flags are not drop proof."""
import unittest

from scripts.query_weapon_pairs import current_roll_filter_diagnostic


def index(*, base=(11, 22), current=(11, 22), retired=(), unknown=()):
    return [{
        "item_type": 3, "item_hash": 100, "name": "Synthetic",
        "sockets": [{
            "socket_index": 2,
            "randomized_candidate_plug_hashes": list(base),
            "currently_rollable_randomized_candidate_plug_hashes": list(current),
            "noncurrent_randomized_candidate_plug_hashes": list(retired),
            "unknown_current_roll_randomized_candidate_plug_hashes": list(unknown),
        }],
    }]


class CurrentRollDiscriminationTests(unittest.TestCase):
    def test_all_current_is_not_a_retired_roll_discriminator(self):
        result = current_roll_filter_diagnostic(index())
        self.assertEqual(result["status"], "no_explicit_noncurrent_memberships_in_snapshot")
        self.assertEqual(result["randomized_memberships"], 2)
        self.assertEqual(result["current_memberships"], 2)
        self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])
        self.assertFalse(result["current_obtainability_certified"])

    def test_explicit_noncurrent_is_discriminating_but_not_drop_proof(self):
        result = current_roll_filter_diagnostic(index(current=(11,), retired=(22,)))
        self.assertEqual(result["status"], "explicit_noncurrent_memberships_present")
        self.assertEqual(result["explicit_noncurrent_memberships"], 1)
        self.assertTrue(result["current_roll_filter_discriminates_retired_memberships"])
        self.assertFalse(result["enhanced_perk_legality_certified"])
        self.assertFalse(result["current_obtainability_certified"])

    def test_unknown_membership_never_becomes_explicit_retired(self):
        result = current_roll_filter_diagnostic(index(current=(11,), unknown=(22,)))
        self.assertEqual(result["unknown_memberships"], 1)
        self.assertEqual(result["explicit_noncurrent_memberships"], 0)
        self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])

    def test_contradictory_current_and_retired_fails_closed(self):
        result = current_roll_filter_diagnostic(index(current=(11, 22), retired=(22,)))
        self.assertEqual(result["status"], "invalid_membership_rows_require_review")
        self.assertEqual(result["invalid_membership_rows"], 1)
        self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])

    def test_unrelated_invalid_socket_fails_report(self):
        rows = index(current=(11,), retired=(22,))
        rows[0]["sockets"].append({"randomized_candidate_plug_hashes": [True]})
        result = current_roll_filter_diagnostic(rows)
        self.assertEqual(result["invalid_membership_rows"], 1)
        self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])

    def test_nonweapon_items_do_not_affect_counts(self):
        rows = index()
        rows.append({"item_type": 2, "sockets": [{"randomized_candidate_plug_hashes": [99]}]})
        result = current_roll_filter_diagnostic(rows)
        self.assertEqual(result["randomized_memberships"], 2)

    def test_no_randomized_memberships_is_unknown(self):
        result = current_roll_filter_diagnostic(index(base=(), current=()))
        self.assertEqual(result["status"], "no_randomized_membership_evidence")
        self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])

    def test_bad_index_container_rejected(self):
        for value in (None, {}, "not an index", 12):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                current_roll_filter_diagnostic(value)


    def test_duplicate_item_hash_invalidates_membership_evidence(self):
        rows = index(current=(11,), retired=(22,))
        rows.append(index(current=(22,), retired=(11,))[0])
        result = current_roll_filter_diagnostic(rows)
        self.assertEqual(result["status"], "invalid_membership_rows_require_review")
        self.assertEqual(result["invalid_membership_rows"], 2)
        self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])

    def test_invalid_weapon_identity_cannot_be_counted(self):
        for bad in (None, True, -1, 0, "100", 100.0):
            with self.subTest(identity=repr(bad)):
                rows = index(current=(11,), retired=(22,))
                rows[0]["item_hash"] = bad
                result = current_roll_filter_diagnostic(rows)
                self.assertEqual(result["invalid_membership_rows"], 1)
                self.assertFalse(result["current_roll_filter_discriminates_retired_memberships"])


if __name__ == "__main__":
    unittest.main()
