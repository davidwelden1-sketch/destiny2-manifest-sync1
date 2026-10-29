import unittest
from scripts.compare_weapon_variants import compare_named_variants


class TestVariantComparison(unittest.TestCase):
    def setUp(self):
        self.index = [
            {"item_hash": 10, "name": "Example", "item_type": 3,
             "sockets": [{"socket_index": 3, "socket_type_hash": 33,
                          "randomized_candidate_plug_hashes": [101, 102]},
                         {"socket_index": 4, "socket_type_hash": 44,
                          "randomized_candidate_plug_hashes": [201]}]},
            {"item_hash": 11, "name": "Example", "item_type": 3,
             "sockets": [{"socket_index": 3, "socket_type_hash": 33,
                          "randomized_candidate_plug_hashes": [101, 103]},
                         {"socket_index": 4, "socket_type_hash": 44,
                          "randomized_candidate_plug_hashes": [201]}]},
            {"item_hash": 12, "name": "Example", "item_type": 2,
             "sockets": [{"socket_index": 3, "randomized_candidate_plug_hashes": [999]}]},
        ]

    def test_same_name_distinct_weapon_hashes_and_per_socket_delta(self):
        report = compare_named_variants(self.index, " example ", {102: "Old", 103: "New"})
        self.assertEqual(report["variant_hashes"], [10, 11])
        changes = report["comparisons"][0]["changed_sockets"]
        self.assertEqual([x["socket_index"] for x in changes], [3])
        self.assertEqual(changes[0]["left_only"], [{"plug_hash": 102, "name": "Old"}])
        self.assertEqual(changes[0]["right_only"], [{"plug_hash": 103, "name": "New"}])

    def test_identical_randomized_socket_evidence_is_not_roll_legality(self):
        self.index[1]["sockets"] = self.index[0]["sockets"]
        report = compare_named_variants(self.index, "Example")
        self.assertTrue(report["comparisons"][0]["identical_randomized_socket_evidence"])
        self.assertIn("do not certify", report["interpretation"])

    def test_socket_type_change_is_visible_even_when_plugs_match(self):
        self.index[1]["sockets"] = [dict(self.index[0]["sockets"][0], socket_type_hash=99)]
        changes = compare_named_variants(self.index, "Example")["comparisons"][0]["changed_sockets"]
        self.assertEqual([x["socket_index"] for x in changes], [3, 4])
        self.assertEqual(changes[0]["right_socket_type_hash"], 99)

    def test_non_weapon_and_empty_name_excluded(self):
        self.assertEqual(compare_named_variants(self.index, "Missing")["variant_hashes"], [])
        with self.assertRaises(ValueError):
            compare_named_variants(self.index, " ")

    def test_duplicate_hash_fails_closed(self):
        with self.assertRaises(ValueError):
            compare_named_variants(self.index + [self.index[0]], "Example")
