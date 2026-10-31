"""Synthetic category/socket audit tests; not gameplay evidence."""
import unittest
from scripts.plug_category_socket_map import audit_category_socket_map


def plug(h, category_hash=77, category="weapon.perks", roll=True):
    return {"plugItemHash": h, "plugCategoryHash": category_hash,
            "plugCategoryIdentifier": category, "currentlyCanRoll": roll, "plugRedacted": False}


def entry(pos, plugs):
    return {"kind": "randomized", "socketIndex": pos, "definitionFound": True,
            "isFakePlugSet": False, "redacted": False, "plugs": plugs}


class CategorySocketMapTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"itemHash": 1, "resolvedPlugSets": [entry(2, [plug(10), plug(11)]), entry(3, [plug(10)])]},
            {"itemHash": 2, "resolvedPlugSets": [entry(4, [plug(10)]),
                {"kind": "reusable", "socketIndex": 1, "definitionFound": True, "plugs": [plug(90)]}]},
        ]

    def test_counts_are_not_unique_plugs(self):
        result = audit_category_socket_map(self.rows)
        self.assertEqual(result["counts"]["randomizedOccurrences"], 4)
        self.assertEqual(result["categories"][0]["uniqueWeaponDefinitions"], 2)
        self.assertEqual(result["categories"][0]["socketPositions"][0]["uniquePlugHashes"], 2)

    def test_weapon_relative_positions_preserved(self):
        result = audit_category_socket_map(self.rows)
        self.assertEqual([r["socketIndex"] for r in result["categories"][0]["socketPositions"]], [2, 3, 4])
        self.assertEqual(result["counts"]["categoriesSpanningMultipleSocketIndexes"], 1)
        self.assertEqual(result["categories"][0]["weaponsWithMultipleSocketPositions"], 1)

    def test_reusable_ignored(self):
        self.assertEqual(sum(x["occurrences"] for x in audit_category_socket_map(self.rows)["categories"][0]["socketPositions"]), 4)

    def test_unknown_category_remains_unknown(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryIdentifier"] = None
        self.assertEqual(audit_category_socket_map(self.rows)["counts"]["unknownCategoryOccurrences"], 1)

    def test_unresolved_set_does_not_infer_category(self):
        self.rows[0]["resolvedPlugSets"].append({"kind": "randomized", "socketIndex": 5, "definitionFound": False, "plugs": None})
        self.assertEqual(audit_category_socket_map(self.rows)["counts"]["unresolvedRandomizedSets"], 1)

    def test_false_roll_not_certified(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["currentlyCanRoll"] = False
        r = audit_category_socket_map(self.rows)
        self.assertEqual(r["counts"]["explicitlyExcludedOccurrences"], 1)
        self.assertIsNone(r["certifiedObtainableRollCount"])
        self.assertIsNone(r["certifiedEnhancedPerkCount"])
        self.assertIsNone(r["certifiedCrossSocketPairCount"])

    def test_unknown_set_flag_not_clean(self):
        self.rows[0]["resolvedPlugSets"][0]["isFakePlugSet"] = None
        self.assertEqual(audit_category_socket_map(self.rows)["counts"]["unknownProvenanceOccurrences"], 2)

    def test_category_identifier_hash_mismatch_reported(self):
        self.rows[1]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryHash"] = 88
        self.assertEqual(audit_category_socket_map(self.rows)["counts"]["categoryIdentifiersWithMultipleHashes"], 1)

    def test_category_hash_identifier_mismatch_reported(self):
        self.rows[1]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryIdentifier"] = "weapon.other"
        self.assertEqual(audit_category_socket_map(self.rows)["counts"]["categoryHashesWithMultipleIdentifiers"], 1)

    def test_reject_duplicate_weapon_hash(self):
        with self.assertRaises(ValueError):
            audit_category_socket_map(self.rows + [self.rows[0]])

    def test_reject_invalid_position(self):
        self.rows[0]["resolvedPlugSets"][0]["socketIndex"] = -1
        with self.assertRaises(ValueError):
            audit_category_socket_map(self.rows)

    def test_reject_boolean_hash(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugItemHash"] = True
        with self.assertRaises(ValueError):
            audit_category_socket_map(self.rows)

    def test_reject_bad_roll_flag(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["currentlyCanRoll"] = 1
        with self.assertRaises(ValueError):
            audit_category_socket_map(self.rows)

    def test_not_measured(self):
        self.assertFalse(audit_category_socket_map(self.rows)["gameplayMeasured"])


if __name__ == "__main__":
    unittest.main()
