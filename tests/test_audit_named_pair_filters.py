import unittest
from collections import Counter
from unittest.mock import patch

from scripts.build_socket_candidates import build_index
from scripts.audit_named_pair_filters import audit_named_pair_filters


class NamedPairFilterAuditTests(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"hash": 100, "name": "Same Weapon", "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"randomizedPlugSetHash": 10, "defaultVisible": True},
                 {"randomizedPlugSetHash": 11, "defaultVisible": True}]},
            {"hash": 101, "name": "Same Weapon", "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"randomizedPlugSetHash": 12},
                 {"randomizedPlugSetHash": 13}]},
            {"hash": 200, "name": "Explosive Payload"},
            {"hash": 201, "name": "Firefly"},
            {"hash": 202, "name": "Explosive Payload"},
            {"hash": 203, "name": "Firefly"},
        ]
        self.plugsets = {"10": [200], "11": [201], "12": [202], "13": [203]}

    def test_four_filters_are_not_interchangeable(self):
        flags = {
            "10": [{"plugItemHash": 200, "currentlyCanRoll": True}],
            "11": [{"plugItemHash": 201, "currentlyCanRoll": False}],
            "12": [{"plugItemHash": 202, "currentlyCanRoll": True}],
            "13": [{"plugItemHash": 203, "currentlyCanRoll": True}],
        }
        index = build_index(self.items[:2], self.plugsets, flags)
        result = audit_named_pair_filters(index, self.items,
                                          "Explosive Payload", "Firefly")
        counts = result["filter_counts"]
        self.assertEqual([counts[k]["structural_pair_rows"] for k in (
            "structural", "explicit_current_flag", "default_visible", "both_filters"
        )], [2, 1, 1, 0])
        self.assertEqual([r["item_hash"] for r in result["per_exact_weapon_hash"]],
                         [100, 101])
        self.assertEqual([r["explicit_current_flag_pair_count"]
                          for r in result["per_exact_weapon_hash"]], [0, 1])
        self.assertEqual([r["default_visible_pair_count"]
                          for r in result["per_exact_weapon_hash"]], [1, 0])
        self.assertTrue(result["explicit_current_flag_filter_reduced_rows"])
        self.assertTrue(result["default_visibility_filter_reduced_rows"])
        self.assertTrue(all(r["roll_legality"] == "unverified"
                            for r in result["per_exact_weapon_hash"]))

    def test_exact_socket_path_export_keeps_variant_and_filter_identity(self):
        flags = {
            "10": [{"plugItemHash": 200, "currentlyCanRoll": True}],
            "11": [{"plugItemHash": 201, "currentlyCanRoll": False}],
            "12": [{"plugItemHash": 202, "currentlyCanRoll": True}],
            "13": [{"plugItemHash": 203, "currentlyCanRoll": True}],
        }
        index = build_index(self.items[:2], self.plugsets, flags)
        report = audit_named_pair_filters(index, self.items,
                                          "Explosive Payload", "Firefly")
        paths = report["per_exact_socket_path"]
        self.assertEqual(len(paths), 2)
        self.assertEqual([(p["item_hash"], p["perk_a_hash"], p["perk_b_hash"],
                           p["a_socket_index"], p["b_socket_index"]) for p in paths],
                         [(100, 200, 201, 0, 1), (101, 202, 203, 0, 1)])
        self.assertEqual([(p["explicit_current_flag"], p["default_visible"],
                           p["both_filters"]) for p in paths],
                         [(False, True, False), (True, False, False)])
        self.assertTrue(all(p["roll_legality"] == "unverified"
                            and p["enhanced_perk_legality"] == "unverified"
                            and p["current_acquisition"] == "unverified"
                            for p in paths))

    def test_exact_socket_path_export_disjoint_filters_never_certifies(self):
        pair = (100, 200, 201)
        reports = [
            self.fake_report([pair], {pair: [(0, 1), (2, 3)]}),
            self.fake_report([pair], {pair: [(0, 1)]}),
            self.fake_report([pair], {pair: [(2, 3)]}),
            self.fake_report([]),
        ]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            report = audit_named_pair_filters([], [], "Explosive Payload", "Firefly")
        paths = report["per_exact_socket_path"]
        self.assertEqual(len(paths), 2)
        self.assertEqual([p["both_filters"] for p in paths], [False, False])
        self.assertEqual(sum(p["explicit_current_flag"] for p in paths), 1)
        self.assertEqual(sum(p["default_visible"] for p in paths), 1)

    def test_missing_flags_do_not_become_current_roll_proof(self):
        index = build_index(self.items[:2], self.plugsets)
        result = audit_named_pair_filters(index, self.items,
                                          "Explosive Payload", "Firefly")
        self.assertEqual(result["filter_counts"]["structural"]["structural_pair_rows"], 2)
        self.assertEqual(result["filter_counts"]["explicit_current_flag"]
                         ["structural_pair_rows"], 0)
        self.assertEqual(result["filter_counts"]["default_visible"]
                         ["structural_pair_rows"], 1)
        self.assertIn("not proof", result["interpretation"])

    def test_unresolved_perk_name_produces_no_false_matches(self):
        index = build_index(self.items[:2], self.plugsets)
        result = audit_named_pair_filters(index, self.items,
                                          "Explosive Payload", "Not a perk")
        self.assertEqual(result["unresolved_names"], ["Not a perk"])
        self.assertEqual(result["per_exact_weapon_hash"], [])
        self.assertEqual(result["filter_counts"]["both_filters"]
                         ["unique_weapon_hashes"], 0)


    @staticmethod
    def fake_report(pairs, paths=None):
        counts = Counter(h for h, _, _ in pairs)
        paths = paths or {}
        return {
            "structural_pair_matches": [
                {"item_hash": h, "perk_a_hash": a, "perk_b_hash": b,
                 "socket_pairs": [
                     {"a_socket_index": x, "b_socket_index": y}
                     for x, y in paths.get((h, a, b), [(0, 1)])
                 ]}
                for h, a, b in pairs
            ],
            "structural_match_count": len(pairs),
            "unique_weapon_definition_count": len(counts),
            "unique_weapon_definitions": [
                {"item_hash": h, "weapon_name": "Weapon",
                 "structural_pair_count": count, "category_role_screens": []}
                for h, count in sorted(counts.items())
            ],
            "resolved_plug_hashes": {"a": [200, 202], "b": [201, 203]},
            "unresolved_names": [],
        }

    def test_filter_cannot_substitute_another_plug_pair_on_same_weapon(self):
        first, swapped = (100, 200, 201), (100, 202, 203)
        reports = [self.fake_report(pairs) for pairs in (
            [first], [swapped], [first], []
        )]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            with self.assertRaisesRegex(ValueError, "plug pairs exceed"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")

    def test_combined_filter_must_preserve_pair_level_intersection(self):
        first, second = (100, 200, 201), (100, 202, 203)
        reports = [self.fake_report(pairs) for pairs in (
            [first, second], [first], [second], [first]
        )]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            with self.assertRaisesRegex(ValueError, "Combined filter must equal"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")

    def test_combined_filter_cannot_silently_drop_an_intersecting_pair(self):
        # An accidental implementation that returns only a proper subset
        # of the two individually passing filters must be rejected.
        first, second = (100, 200, 201), (100, 202, 203)
        reports = [self.fake_report(pairs) for pairs in (
            [first, second], [first, second], [first], []
        )]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            with self.assertRaisesRegex(ValueError, "Combined filter must equal"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")

    def test_combined_filter_exact_pair_intersection_is_accepted(self):
        first, second = (100, 200, 201), (100, 202, 203)
        reports = [self.fake_report(pairs) for pairs in (
            [first, second], [first, second], [first], [first]
        )]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            result = audit_named_pair_filters([], [], "Explosive Payload", "Firefly")
        self.assertEqual(result["filter_counts"]["both_filters"]
                         ["structural_pair_rows"], 1)

    def test_disjoint_socket_paths_do_not_create_false_combined_match(self):
        # Same weapon+plug pair is present in each individual filter, but
        # different socket paths satisfy each. Combined filter correctly empty.
        pair = (100, 200, 201)
        reports = [
            self.fake_report([pair], {pair: [(0, 1), (2, 3)]}),
            self.fake_report([pair], {pair: [(0, 1)]}),
            self.fake_report([pair], {pair: [(2, 3)]}),
            self.fake_report([]),
        ]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            result = audit_named_pair_filters([], [], "Explosive Payload", "Firefly")
        self.assertEqual(result["filter_counts"]["both_filters"]["distinct_socket_paths"], 0)
        self.assertTrue(result["socket_path_filter_intersection_verified"])

    def test_combined_filter_cannot_omit_common_socket_path(self):
        pair = (100, 200, 201)
        reports = [
            self.fake_report([pair], {pair: [(0, 1), (2, 3)]}),
            self.fake_report([pair], {pair: [(0, 1), (2, 3)]}),
            self.fake_report([pair], {pair: [(0, 1)]}),
            self.fake_report([]),
        ]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            with self.assertRaisesRegex(ValueError, "socket-path intersection"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")

    def test_malformed_socket_path_fails_closed(self):
        pair = (100, 200, 201)
        reports = [self.fake_report([pair], {pair: [(0, 0)]})] * 4
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            with self.assertRaisesRegex(ValueError, "Invalid distinct socket indices"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")

    def test_socket_orientation_counts_are_exact_and_do_not_infer_rolls(self):
        pair = (100, 200, 201)
        reports = [self.fake_report([pair], {pair: [(3, 4), (4, 3)]})] * 4
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            result = audit_named_pair_filters([], [], "Explosive Payload", "Firefly")
        self.assertEqual(result["socket_order_counts"],
                         {"perk_a_before_perk_b": 1, "perk_b_before_perk_a": 1})
        self.assertEqual(result["socket_order_by_exact_weapon_hash"][0]["item_hash"], 100)
        self.assertEqual(result["socket_order_by_exact_weapon_hash"][0]
                         ["perk_b_before_perk_a"], 1)
        self.assertTrue(all(p["roll_legality"] == "unverified"
                            for p in result["per_exact_socket_path"]))

    def test_socket_orientation_preserves_same_named_variant_hashes(self):
        first, second = (100, 200, 201), (101, 202, 203)
        paths = {first: [(3, 4)], second: [(4, 3)]}
        reports = [self.fake_report([first, second], paths)] * 4
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            result = audit_named_pair_filters([], [], "Explosive Payload", "Firefly")
        self.assertEqual(result["socket_order_counts"],
                         {"perk_a_before_perk_b": 1, "perk_b_before_perk_a": 1})
        self.assertEqual(
            [(r["item_hash"], r["perk_a_before_perk_b"], r["perk_b_before_perk_a"])
             for r in result["socket_order_by_exact_weapon_hash"]],
            [(100, 1, 0), (101, 0, 1)])

    def test_duplicate_pair_rows_are_rejected(self):
        first = (100, 200, 201)
        reports = [self.fake_report(pairs) for pairs in (
            [first, first], [first], [first], [first]
        )]
        with patch("scripts.audit_named_pair_filters.query_named_pairs",
                   side_effect=reports):
            with self.assertRaisesRegex(ValueError, "Duplicate exact"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")


if __name__ == "__main__":
    unittest.main()
