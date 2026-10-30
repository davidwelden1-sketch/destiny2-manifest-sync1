"""Synthetic schema fixtures, not live Bungie manifest verification."""
import unittest
from scripts.weapon_socket_refs import build_weapon_socket_reference_index


class TestWeaponSocketReferences(unittest.TestCase):
    def test_preserves_item_hash_and_socket_positions(self):
        data = {"42": {"itemType": 3, "displayProperties": {"name": "Test Rifle"},
                       "itemSubType": 6, "sockets": {"socketEntries": [
                           {"socketTypeHash": 11, "randomizedPlugSetHash": 77,
                            "reusablePlugItems": [{"plugItemHash": 88}]},
                           {"reusablePlugSetHash": 99, "singleInitialItemHash": 100}]}}}
        row = build_weapon_socket_reference_index(data)[0]
        self.assertEqual(row["hash"], 42)
        self.assertEqual(row["sockets"][0]["socketIndex"], 0)
        self.assertEqual(row["sockets"][1]["socketIndex"], 1)
        self.assertEqual(row["sockets"][0]["randomizedPlugSetHash"], 77)
        self.assertEqual(row["sockets"][0]["reusablePlugItemHashes"], [88])
        self.assertEqual(row["sockets"][1]["reusablePlugSetHash"], 99)
        self.assertFalse(row["certifiedObtainableRoll"])
        self.assertFalse(row["certifiedEnhancedPerks"])

    def test_does_not_merge_same_named_weapon_versions(self):
        fixture = {"50": {"itemType": 3, "displayProperties": {"name": "Same"}},
                   "49": {"itemType": 3, "displayProperties": {"name": "Same"}}}
        self.assertEqual([x["hash"] for x in build_weapon_socket_reference_index(fixture)], [49, 50])

    def test_ignores_non_weapons_without_rejecting_missing_sockets(self):
        fixture = {"1": {"itemType": 2}, "2": {"itemType": 3}}
        rows = build_weapon_socket_reference_index(fixture)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sockets"], [])

    def test_malformed_socket_rejected(self):
        for entries in ("not a list", [None], [{"reusablePlugItems": [None]}]):
            with self.subTest(entries=entries):
                with self.assertRaises(ValueError):
                    build_weapon_socket_reference_index({"7": {"itemType": 3, "sockets": {"socketEntries": entries}}})

    def test_bad_hashes_fail_closed(self):
        for value in (True, -1, 2**32, "77"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    build_weapon_socket_reference_index({"7": {"itemType": 3, "sockets": {"socketEntries": [{"randomizedPlugSetHash": value}]}}})


if __name__ == "__main__":
    unittest.main()
