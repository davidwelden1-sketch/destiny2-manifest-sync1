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
    def fake_report(pairs):
        counts = Counter(h for h, _, _ in pairs)
        return {
            "structural_pair_matches": [
                {"item_hash": h, "perk_a_hash": a, "perk_b_hash": b}
                for h, a, b in pairs
            ],
            "structural_match_count": len(pairs),
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
            with self.assertRaisesRegex(ValueError, "Combined filter contains pairs"):
                audit_named_pair_filters([], [], "Explosive Payload", "Firefly")

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
