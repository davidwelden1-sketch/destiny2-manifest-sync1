import unittest
from scripts.audit_weapon_frame_candidates import audit_initial_frame_candidates


class TestInitialFrameEvidence(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"hash": 101, "name": "Test sword", "itemType": 3,
             "itemSubType": 18, "equippable": True,
             "socketEntries": [
                 {"singleInitialItemHash": 501, "socketTypeHash": 601,
                  "defaultVisible": True},
                 {"singleInitialItemHash": 502, "defaultVisible": False},
                 {"singleInitialItemHash": 503},
                 {"singleInitialItemHash": 999},
             ]},
            {"hash": 102, "name": "Other weapon", "itemType": 3,
             "equippable": True, "socketEntries": [
                 {"singleInitialItemHash": 501},
             ]},
            {"hash": 103, "name": "Not equippable", "itemType": 3,
             "equippable": False, "socketEntries": [
                 {"singleInitialItemHash": 501},
             ]},
            {"hash": 501, "name": "Vortex Frame", "plugCategoryIdentifier": "frames"},
            {"hash": 502, "name": "Element", "plugCategoryIdentifier": "v300.weapon.damage_type.energy"},
            {"hash": 503, "name": "Unknown", "plugCategoryIdentifier": None},
        ]

    def test_exact_hash_and_category_only(self):
        report = audit_initial_frame_candidates(self.items, "synthetic")
        self.assertEqual(report["equippable_weapon_definitions"], 2)
        self.assertEqual(report["frames_labelled_initial_plug_occurrences"], 2)
        self.assertEqual(report["weapons_with_frames_labelled_initial_plug"], 2)
        self.assertEqual([row["item_hash"] for row in report["frame_candidates"]],
                         [101, 102])

    def test_no_automatic_champion_or_active_frame_certification(self):
        for row in audit_initial_frame_candidates(self.items, "synthetic")["frame_candidates"]:
            self.assertFalse(row["active_frame_verified"])
            self.assertFalse(row["champion_effect_verified"])
            self.assertEqual(row["runtime_socket_state"], "unverified")

    def test_other_component_labels_excluded(self):
        report = audit_initial_frame_candidates(self.items, "synthetic")
        self.assertEqual(report["initial_plug_category_occurrences"][
            "v300.weapon.damage_type.energy"], 1)
        self.assertEqual(report["initial_plug_category_occurrences"]["<missing>"], 1)

    def test_missing_reference_reported_without_fabricating_frame(self):
        report = audit_initial_frame_candidates(self.items, "synthetic")
        self.assertEqual(report["unresolved_initial_plug_references"], 1)
        self.assertEqual(report["unresolved_initial_plug_examples"][0]["initial_plug_hash"], 999)

    def test_nonpositive_and_boolean_hashes_ignored(self):
        rows = [{"hash": 1, "itemType": 3, "equippable": True,
                 "socketEntries": [{"singleInitialItemHash": True},
                                   {"singleInitialItemHash": 0},
                                   {"singleInitialItemHash": -2}]}]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["unresolved_initial_plug_references"], 0)
        self.assertEqual(report["frames_labelled_initial_plug_occurrences"], 0)

    def test_duplicate_names_do_not_merge_versions(self):
        rows = [
            {"hash": 1, "name": "Same", "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 501}]},
            {"hash": 2, "name": "Same", "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 502}]},
            {"hash": 501, "name": "Frame", "plugCategoryIdentifier": "frames"},
            {"hash": 502, "name": "Magazine", "plugCategoryIdentifier": "magazines"},
        ]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual([x["item_hash"] for x in report["frame_candidates"]], [1])


    def test_multi_frame_labelled_plugs_are_counted_per_exact_hash(self):
        rows = [
            {"hash": 11, "name": "Multi", "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 501},
                               {"singleInitialItemHash": 502}]},
            {"hash": 12, "name": "Single", "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 501}]},
            {"hash": 501, "name": "Vortex Frame", "plugCategoryIdentifier": "frames"},
            {"hash": 502, "name": "Other Frame", "plugCategoryIdentifier": "frames"},
        ]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["weapons_with_multiple_frame_labelled_initial_plugs"], 1)
        self.assertEqual(report["multi_frame_labelled_occurrences"], 2)
        example = report["multi_frame_labelled_examples"][0]
        self.assertEqual(example["item_hash"], 11)
        self.assertEqual(example["socket_indexes"], [0, 1])
        self.assertEqual(example["distinct_initial_plug_hashes"], 2)
        self.assertEqual(example["initial_plug_names"], ["Other Frame", "Vortex Frame"])

    def test_repeated_same_frame_label_is_not_a_distinct_frame(self):
        rows = [
            {"hash": 11, "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 501},
                               {"singleInitialItemHash": 501}]},
            {"hash": 501, "name": "Frame", "plugCategoryIdentifier": "frames"},
        ]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["weapons_with_multiple_frame_labelled_initial_plugs"], 1)
        self.assertEqual(report["multi_frame_labelled_examples"][0][
            "distinct_initial_plug_hashes"], 1)
        self.assertFalse(any(x["active_frame_verified"]
                             for x in report["frame_candidates"]))

    def test_no_multiple_frame_labels_returns_empty_examples(self):
        report = audit_initial_frame_candidates(self.items, "synthetic")
        self.assertEqual(report["weapons_with_multiple_frame_labelled_initial_plugs"], 0)
        self.assertEqual(report["multi_frame_labelled_occurrences"], 0)
        self.assertEqual(report["multi_frame_labelled_examples"], [])


    def test_frame_labelled_socket_type_relationships(self):
        rows = [
            {"hash": 11, "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"singleInitialItemHash": 501, "socketTypeHash": 900},
                 {"singleInitialItemHash": 502, "socketTypeHash": 901}]},
            {"hash": 12, "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"singleInitialItemHash": 501, "socketTypeHash": 900},
                 {"singleInitialItemHash": 501, "socketTypeHash": 900}]},
            {"hash": 13, "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"singleInitialItemHash": 501},
                 {"singleInitialItemHash": 502, "socketTypeHash": 900}]},
            {"hash": 501, "plugCategoryIdentifier": "frames"},
            {"hash": 502, "plugCategoryIdentifier": "frames"},
        ]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["multi_frame_socket_type_relationships"],
                         {"different_socket_types": 1, "same_socket_type": 1,
                          "unknown_socket_type": 1})
        self.assertEqual(report["multi_frame_plug_identity_relationships"],
                         {"different_initial_plugs": 2, "same_initial_plug": 1})
        self.assertEqual(report["multi_frame_socket_index_patterns"], {"0,1": 3})
        self.assertTrue(all(not row["active_frame_verified"] for row
                            in report["multi_frame_relationship_examples"]))

    def test_frame_socket_index_patterns_do_not_merge_hashes(self):
        rows = [
            {"hash": 11, "itemType": 3, "equippable": True,
             "socketEntries": [
                 {}, {"singleInitialItemHash": 501, "socketTypeHash": 901},
                 {}, {"singleInitialItemHash": 502, "socketTypeHash": 902}]},
            {"hash": 12, "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"singleInitialItemHash": 501, "socketTypeHash": 901},
                 {"singleInitialItemHash": 502, "socketTypeHash": 902}]},
            {"hash": 501, "plugCategoryIdentifier": "frames"},
            {"hash": 502, "plugCategoryIdentifier": "frames"},
        ]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["multi_frame_socket_index_patterns"],
                         {"0,1": 1, "1,3": 1})
        self.assertEqual(report["multi_frame_socket_type_relationships"],
                         {"different_socket_types": 2})

    def test_boolean_socket_type_is_unknown(self):
        rows = [
            {"hash": 11, "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"singleInitialItemHash": 501, "socketTypeHash": True},
                 {"singleInitialItemHash": 501, "socketTypeHash": 901}]},
            {"hash": 501, "plugCategoryIdentifier": "frames"},
        ]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["multi_frame_socket_type_relationships"],
                         {"unknown_socket_type": 1})
        self.assertEqual(report["multi_frame_socket_type_pairs_top"], [])


    def test_unique_dominant_pair_surfaces_exact_hash_outlier(self):
        def weapon(hash_value, left, right):
            return {"hash": hash_value, "name": f"Weapon {hash_value}",
                    "itemType": 3, "equippable": True, "socketEntries": [
                        {"singleInitialItemHash": 501, "socketTypeHash": left},
                        {"singleInitialItemHash": 502, "socketTypeHash": right}]}
        rows = [weapon(11, 900, 901), weapon(12, 901, 900),
                weapon(13, 900, 901), weapon(14, 900, 902),
                {"hash": 501, "name": "Intrinsic A", "plugCategoryIdentifier": "frames"},
                {"hash": 502, "name": "Intrinsic B", "plugCategoryIdentifier": "frames"}]
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["multi_frame_dominant_socket_type_pair"], "900,901")
        self.assertEqual(report["multi_frame_exception_count"], 1)
        outlier = report["multi_frame_exception_examples"][0]
        self.assertEqual(outlier["item_hash"], 14)
        self.assertEqual(outlier["socket_type_hashes"], [900, 902])
        self.assertEqual(outlier["initial_plug_names"], ["Intrinsic A", "Intrinsic B"])
        self.assertEqual(outlier["reason"], "non_dominant_socket_type_pair")
        self.assertFalse(outlier["active_frame_verified"])
        self.assertFalse(outlier["current_acquisition_verified"])

    def test_tied_pairs_do_not_invent_dominant_frame_structure(self):
        rows = [
            {"hash": h, "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 501, "socketTypeHash": 900},
                               {"singleInitialItemHash": 502, "socketTypeHash": t}]}
            for h, t in ((11, 901), (12, 902))]
        rows.extend([{"hash": 501, "plugCategoryIdentifier": "frames"},
                     {"hash": 502, "plugCategoryIdentifier": "frames"}])
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertIsNone(report["multi_frame_dominant_socket_type_pair"])
        self.assertEqual(report["multi_frame_exception_count"], 2)
        self.assertEqual({r["reason"] for r in report["multi_frame_exception_examples"]},
                         {"no_unique_dominant_pair"})

    def test_unknown_socket_type_is_explicit_exception(self):
        rows = [
            {"hash": h, "itemType": 3, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 501, "socketTypeHash": 900},
                               {"singleInitialItemHash": 502, "socketTypeHash": t}]}
            for h, t in ((11, 901), (12, 901), (13, True))]
        rows.extend([{"hash": 501, "plugCategoryIdentifier": "frames"},
                     {"hash": 502, "plugCategoryIdentifier": "frames"}])
        report = audit_initial_frame_candidates(rows, "synthetic")
        self.assertEqual(report["multi_frame_dominant_socket_type_pair"], "900,901")
        self.assertEqual(report["multi_frame_exception_count"], 1)
        self.assertEqual(report["multi_frame_exception_examples"][0]["item_hash"], 13)
        self.assertEqual(report["multi_frame_exception_examples"][0]["reason"],
                         "unknown_socket_type")


if __name__ == "__main__":
    unittest.main()
