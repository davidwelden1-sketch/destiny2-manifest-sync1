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


if __name__ == "__main__":
    unittest.main()
