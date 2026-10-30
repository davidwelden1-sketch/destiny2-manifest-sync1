import unittest

from scripts.build_socket_candidates import build_index
from scripts.query_named_weapon_perks import query_named_pairs, resolve_names


class NamedPerkQueryTests(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"hash": 100, "name": "Weapon", "itemType": 3, "equippable": True,
             "socketEntries": [{"randomizedPlugSetHash": 10, "defaultVisible": True},
                               {"randomizedPlugSetHash": 11, "defaultVisible": True}]},
            {"hash": 101, "name": "Weapon", "itemType": 3, "equippable": True,
             "socketEntries": [{"randomizedPlugSetHash": 12},
                               {"randomizedPlugSetHash": 13}]},
            {"hash": 200, "name": "Explosive Payload"},
            {"hash": 201, "name": "Firefly"},
            {"hash": 202, "name": "explosive payload"},
            {"hash": 203, "name": "Firefly"},
            {"hash": 204, "name": "Reusable Only"},
        ]
        self.index = build_index(self.items[:2], {
            "10": [200], "11": [201], "12": [202], "13": [203]})

    def test_resolves_distinct_same_name_hashes(self):
        found = resolve_names(self.index, self.items, [" explosive payload ", "FIREFLY"])
        self.assertEqual(found["explosive payload"], [200, 202])
        self.assertEqual(found["firefly"], [201, 203])

    def test_never_merges_same_name_weapon_variants(self):
        rows = query_named_pairs(self.index, self.items, "Explosive Payload", "Firefly")
        self.assertEqual([(r["item_hash"], r["perk_a_hash"], r["perk_b_hash"])
                          for r in rows["structural_pair_matches"]],
                         [(100, 200, 201), (101, 202, 203)])
        self.assertEqual(rows["enhanced_perk_legality"], "unverified")

    def test_same_socket_cannot_form_pair(self):
        index = build_index([{"hash": 10, "name": "A", "itemType": 3,
                              "equippable": True,
                              "socketEntries": [{"randomizedPlugSetHash": 20}]}],
                            {"20": [200, 201]})
        self.assertEqual(query_named_pairs(index, self.items, "Explosive Payload", "Firefly")
                         ["structural_pair_matches"], [])

    def test_unresolved_name_and_reusable_only_do_not_match(self):
        rows = query_named_pairs(self.index, self.items, "Explosive Payload", "Reusable Only")
        self.assertEqual(rows["unresolved_names"], ["Reusable Only"])
        self.assertEqual(rows["structural_pair_matches"], [])

    def test_explicit_roll_flags_required_when_requested(self):
        flags = {"10": [{"plugItemHash": 200, "currentlyCanRoll": True}],
                 "11": [{"plugItemHash": 201, "currentlyCanRoll": False}],
                 "12": [{"plugItemHash": 202, "currentlyCanRoll": True}],
                 "13": [{"plugItemHash": 203, "currentlyCanRoll": True}]}
        index = build_index(self.items[:2], {"10": [200], "11": [201],
                                             "12": [202], "13": [203]}, flags)
        rows = query_named_pairs(index, self.items, "Explosive Payload", "Firefly",
                                 current_roll_only=True)
        self.assertEqual([r["item_hash"] for r in rows["structural_pair_matches"]], [101])

    def test_default_visibility_filter_is_not_live_socket_proof(self):
        rows = query_named_pairs(self.index, self.items, "Explosive Payload", "Firefly",
                                 default_visible_only=True)
        self.assertEqual([r["item_hash"] for r in rows["structural_pair_matches"]], [100])
        self.assertIn("runtime states may differ", rows["interpretation"])

    def test_report_distinguishes_matches_from_unique_weapon_definitions(self):
        report = query_named_pairs(self.index, self.items, "Explosive Payload", "Firefly")
        self.assertEqual(report["structural_match_count"], 2)
        self.assertEqual(report["unique_weapon_definition_count"], 2)
        self.assertEqual(report["category_role_screen_counts"]["unknown_missing_category"], 2)
        self.assertEqual(report["roll_legality"], "unverified")

    def test_explicit_component_category_is_flagged_not_certified(self):
        self.items[4]["plugCategoryIdentifier"] = "barrels"
        self.items[5]["plugCategoryIdentifier"] = "v300.weapon.trait"
        report = query_named_pairs(self.index, self.items, "Explosive Payload", "Firefly")
        flagged = [r for r in report["structural_pair_matches"]
                   if r["perk_a_hash"] == 202]
        self.assertEqual(flagged[0]["category_role_screen"],
                         "explicit_component_label_present")
        self.assertEqual(report["category_role_screen_counts"]
                         ["explicit_component_label_present"], 1)
        self.assertEqual(report["enhanced_perk_legality"], "unverified")

    def test_unclassified_categories_do_not_certify_trait_role(self):
        for item in self.items:
            if item.get("hash") in (200, 201, 202, 203):
                item["plugCategoryIdentifier"] = "frames"
        report = query_named_pairs(self.index, self.items, "Explosive Payload", "Firefly")
        self.assertEqual(report["category_role_screen_counts"]
                         ["unclassified_not_trait_certified"], 2)
        self.assertIn("does NOT certify a weapon trait", report["interpretation"])

    def test_invalid_names_and_filters_fail_closed(self):
        for names in (("", "Firefly"), ("Firefly", "firefly"), (None, "Firefly")):
            with self.assertRaises(ValueError):
                query_named_pairs(self.index, self.items, *names)
        with self.assertRaises(ValueError):
            query_named_pairs(self.index, self.items, "Firefly", "Explosive Payload",
                              current_roll_only=1)


if __name__ == "__main__":
    unittest.main()
