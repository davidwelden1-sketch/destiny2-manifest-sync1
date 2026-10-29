import unittest

from scripts.audit_frame_plug_reuse import audit_frame_plug_reuse


class TestFramePlugReuse(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"hash": 10, "name": "Alpha", "itemType": 3, "equippable": True,
             "itemSubType": 6, "socketEntries": [
                 {"singleInitialItemHash": 100, "socketTypeHash": 501},
                 {"singleInitialItemHash": 101, "socketTypeHash": 502}]},
            {"hash": 11, "name": "Beta", "itemType": 3, "equippable": True,
             "itemSubType": 7, "socketEntries": [
                 {"singleInitialItemHash": 100, "socketTypeHash": 503}]},
            {"hash": 12, "name": "Armor", "itemType": 2, "equippable": True,
             "socketEntries": [{"singleInitialItemHash": 100}]},
            {"hash": 100, "name": "Ambiguous", "plugCategoryIdentifier": "frames"},
            {"hash": 101, "name": "Magazine", "plugCategoryIdentifier": "magazines"},
        ]
        self.index = [
            {"item_hash": 10, "item_type": 3, "sockets": [
                {"socket_index": 2, "randomized_candidate_plug_hashes": [100, 101]}]},
            {"item_hash": 11, "item_type": 3, "sockets": [
                {"socket_index": 1, "randomized_candidate_plug_hashes": [999]}]},
        ]

    def test_reuse_across_weapon_subtypes_and_same_weapon_randomized(self):
        report = audit_frame_plug_reuse(self.items, self.index, "synthetic")
        self.assertEqual(report["equippable_weapon_definitions"], 2)
        self.assertEqual(report["unique_frames_labelled_initial_plug_hashes"], 1)
        self.assertEqual(report["initial_plug_hashes_reused_across_weapon_hashes"], 1)
        self.assertEqual(report["initial_plug_hashes_spanning_weapon_subtypes"], 1)
        self.assertEqual(report["initial_plug_hashes_also_in_randomized_weapon_sockets"], 1)
        self.assertEqual(report["initial_plug_hashes_randomized_on_same_weapon"], 1)
        self.assertFalse(report["examples"][0]["active_frame_verified"])

    def test_other_weapon_randomized_overlap_is_not_same_weapon(self):
        self.index[0]["sockets"][0]["randomized_candidate_plug_hashes"] = [101]
        self.index[1]["sockets"][0]["randomized_candidate_plug_hashes"] = [100]
        self.index[1]["item_hash"] = 13
        report = audit_frame_plug_reuse(self.items, self.index, "synthetic")
        self.assertEqual(report["initial_plug_hashes_also_in_randomized_weapon_sockets"], 1)
        self.assertEqual(report["initial_plug_hashes_randomized_on_same_weapon"], 0)

    def test_nonframe_and_nonweapon_excluded(self):
        self.items[3]["plugCategoryIdentifier"] = "magazines"
        report = audit_frame_plug_reuse(self.items, self.index, "synthetic")
        self.assertEqual(report["unique_frames_labelled_initial_plug_hashes"], 0)
        self.assertEqual(report["examples"], [])

    def test_boolean_hashes_fail_closed(self):
        self.items[0]["socketEntries"].append({"singleInitialItemHash": True})
        self.index[0]["sockets"][0]["randomized_candidate_plug_hashes"] = [True]
        report = audit_frame_plug_reuse(self.items, self.index, "synthetic")
        self.assertEqual(report["unique_frames_labelled_initial_plug_hashes"], 1)
        self.assertEqual(report["initial_plug_hashes_also_in_randomized_weapon_sockets"], 0)


if __name__ == "__main__":
    unittest.main()
