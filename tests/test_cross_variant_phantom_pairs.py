import unittest

from scripts.audit_cross_variant_phantom_pairs import (
    audit_cross_variant_phantoms, distinct_socket_pairs, socket_pools,
)


def weapon(h, name, sockets):
    return {"item_hash": h, "name": name, "item_type": 3, "sockets": [
        {"socket_index": index, "randomized_candidate_plug_hashes": plugs}
        for index, plugs in sockets.items()
    ]}


class TestCrossVariantPhantomPairs(unittest.TestCase):
    def test_merging_variants_invents_pair_not_on_any_hash(self):
        rows = [
            weapon(101, "Lotus", {3: [10], 4: [20]}),
            weapon(102, " LOTUS ", {3: [30], 4: [40]}),
        ]
        report = audit_cross_variant_phantoms(rows, "test")
        self.assertEqual(report["same_name_variant_groups_checked"], 1)
        self.assertEqual(report["groups_with_phantom_pairs"], 1)
        self.assertEqual(report["phantom_pair_occurrences_across_groups"], 2)
        self.assertEqual(report["groups"][0]["example_phantom_plug_pairs"], [[10, 40], [20, 30]])

    def test_same_variant_pair_never_counted_as_phantom(self):
        rows = [weapon(1, "A", {3: [10, 30], 4: [20]}),
                weapon(2, "A", {3: [10], 4: [20]})]
        report = audit_cross_variant_phantoms(rows, "test")
        self.assertEqual(report["groups_with_phantom_pairs"], 0)

    def test_same_socket_is_not_a_pair(self):
        rows = [weapon(1, "A", {3: [10]}), weapon(2, "A", {3: [20]})]
        self.assertEqual(audit_cross_variant_phantoms(rows, "test")["groups_with_phantom_pairs"], 0)
        self.assertEqual(distinct_socket_pairs(socket_pools(rows[0])), set())

    def test_no_cross_name_or_armor_merging(self):
        rows = [weapon(1, "A", {3: [10]}), weapon(2, "B", {4: [20]}),
                {"item_hash": 3, "name": "A", "item_type": 2,
                 "sockets": [{"socket_index": 4, "randomized_candidate_plug_hashes": [20]}]}]
        report = audit_cross_variant_phantoms(rows, "test")
        self.assertEqual(report["same_name_variant_groups_checked"], 0)


    def test_missing_socket_list_is_not_an_empty_pool(self):
        row = {"item_hash": 1, "name": "A", "item_type": 3}
        with self.assertRaisesRegex(ValueError, "Missing weapon socket"):
            audit_cross_variant_phantoms([row], "test")

    def test_missing_membership_is_not_explicitly_nonrandomized(self):
        row = {"item_hash": 1, "name": "A", "item_type": 3,
               "sockets": [{"socket_index": 3}]}
        with self.assertRaisesRegex(ValueError, "Missing randomized"):
            audit_cross_variant_phantoms([row], "test")

    def test_duplicate_socket_index_cannot_merge_two_perk_pools(self):
        row = {"item_hash": 1, "name": "A", "item_type": 3,
               "sockets": [
                   {"socket_index": 3, "randomized_candidate_plug_hashes": [10]},
                   {"socket_index": 3, "randomized_candidate_plug_hashes": [20]}]}
        with self.assertRaisesRegex(ValueError, "duplicate socket"):
            audit_cross_variant_phantoms([row], "test")

    def test_corrupt_singleton_fails_before_name_merging(self):
        row = {"item_hash": 1, "name": "Unique", "item_type": 3,
               "sockets": [None]}
        with self.assertRaisesRegex(ValueError, "Malformed weapon socket"):
            audit_cross_variant_phantoms([row], "test")

    def test_boolean_socket_index_and_scalar_plugs_fail(self):
        row = weapon(1, "A", {3: [10]})
        row["sockets"][0]["socket_index"] = True
        with self.assertRaises(ValueError):
            audit_cross_variant_phantoms([row], "test")
        row["sockets"][0]["socket_index"] = 3
        row["sockets"][0]["randomized_candidate_plug_hashes"] = 10
        with self.assertRaises(ValueError):
            audit_cross_variant_phantoms([row], "test")

    def test_explicit_empty_sockets_remain_distinct_from_missing(self):
        row = weapon(1, "A", {})
        self.assertEqual(audit_cross_variant_phantoms([row], "test")["weapon_definitions_checked"], 1)

    def test_malformed_index_and_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "sequence"):
            audit_cross_variant_phantoms(None, "test")
        with self.assertRaisesRegex(ValueError, "Malformed weapon row"):
            audit_cross_variant_phantoms([None], "test")

    def test_invalid_hashes_and_socket_data_fail_closed(self):
        with self.assertRaises(ValueError):
            audit_cross_variant_phantoms([weapon(1, "A", {}), weapon(1, "B", {})], "test")
        with self.assertRaises(ValueError):
            audit_cross_variant_phantoms([weapon(1, "A", {3: [True]})], "test")
        with self.assertRaises(ValueError):
            audit_cross_variant_phantoms([weapon(1, "A", {-1: [10]})], "test")
        with self.assertRaises(ValueError):
            audit_cross_variant_phantoms([], "test", sample_limit=-1)


if __name__ == "__main__":
    unittest.main()
