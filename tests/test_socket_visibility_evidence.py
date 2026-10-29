"""Conservative checks for Bungie socket default visibility and plug sources.

These tests are synthetic; defaultVisible is not a runtime roll guarantee.
"""
import unittest

from scripts.build_socket_candidates import build_index
from scripts.query_weapon_pairs import find_pair_candidates, summarize


class TestSocketVisibilityEvidence(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"hash": 100, "name": "Visible pair", "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"randomizedPlugSetHash": 10, "defaultVisible": True, "plugSources": 2,
                  "preventInitializationOnVendorPurchase": False},
                 {"randomizedPlugSetHash": 11, "defaultVisible": True, "plugSources": 4}]},
            {"hash": 101, "name": "Legacy hidden", "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"randomizedPlugSetHash": 10, "defaultVisible": False},
                 {"randomizedPlugSetHash": 11, "defaultVisible": True}]},
            {"hash": 102, "name": "Unknown visibility", "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"randomizedPlugSetHash": 10},
                 {"randomizedPlugSetHash": 11, "defaultVisible": True}]},
            {"hash": 103, "name": "Invalid metadata", "itemType": 3, "equippable": True,
             "socketEntries": [
                 {"randomizedPlugSetHash": 10, "defaultVisible": 1,
                  "plugSources": True, "preventInitializationOnVendorPurchase": "false"},
                 {"randomizedPlugSetHash": 11, "defaultVisible": True}]},
        ]
        self.index = build_index(self.items, {"10": [20], "11": [30]})

    def test_preserves_explicit_source_and_vendor_evidence(self):
        socket = self.index[0]["sockets"][0]
        self.assertIs(socket["default_visible"], True)
        self.assertEqual(socket["plug_sources"], 2)
        self.assertIs(socket["vendor_purchase_initialization_blocked"], False)

    def test_hidden_and_unknown_are_excluded_only_in_strict_mode(self):
        self.assertEqual(len(find_pair_candidates(self.index, 20, 30)), 4)
        strict = find_pair_candidates(self.index, 20, 30, default_visible_only=True)
        self.assertEqual([r["item_hash"] for r in strict], [100])
        self.assertEqual(strict[0]["runtime_socket_state"], "unverified")
        self.assertIs(strict[0]["socket_pairs"][0]["a_default_visible"], True)

    def test_invalid_metadata_fails_closed(self):
        s = self.index[3]["sockets"][0]
        self.assertIsNone(s["default_visible"])
        self.assertIsNone(s["plug_sources"])
        self.assertIsNone(s["vendor_purchase_initialization_blocked"])

    def test_visibility_summary_counts_socket_memberships_not_drops(self):
        v = summarize(self.index, "test")["randomized_socket_default_visibility"]
        self.assertEqual(v, {"true": 5, "false": 1, "unknown": 2})

    def test_non_boolean_strict_filter_rejected(self):
        with self.assertRaises(ValueError):
            find_pair_candidates(self.index, 20, 30, default_visible_only=1)


if __name__ == "__main__":
    unittest.main()
