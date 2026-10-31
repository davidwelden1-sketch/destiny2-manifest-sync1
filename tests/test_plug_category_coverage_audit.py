"""Synthetic plug-category coverage tests, not live weapon-roll evidence."""
import unittest

from scripts.plug_category_coverage_audit import audit_weapon_plug_categories


class PlugCategoryCoverageTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"itemHash": 1, "resolvedPlugSets": [
            {"kind": "randomized", "definitionFound": True, "isFakePlugSet": False,
             "plugs": [
                 {"plugItemHash": 100, "plugCategoryHash": 12,
                  "plugCategoryIdentifier": "weapon.perks", "plugRedacted": False},
                 {"plugItemHash": 101, "plugCategoryHash": None,
                  "plugCategoryIdentifier": None, "plugRedacted": None}]},
            {"kind": "reusable", "definitionFound": True,
             "plugs": [{"plugItemHash": 100, "plugCategoryHash": 12,
                        "plugCategoryIdentifier": "weapon.perks"}]},
            {"kind": "randomized", "definitionFound": False, "plugs": None}
        ]}]

    def test_separates_randomized_and_reusable_occurrences(self):
        counts = audit_weapon_plug_categories(self.rows)["counts"]
        self.assertEqual(counts["randomizedOccurrences"], 2)
        self.assertEqual(counts["reusableOccurrences"], 1)
        self.assertEqual(counts["randomizedUnresolvedPlugSets"], 1)

    def test_unknown_category_not_inferred(self):
        counts = audit_weapon_plug_categories(self.rows)["counts"]
        self.assertEqual(counts["randomizedKnownCategoryOccurrences"], 1)
        self.assertEqual(counts["randomizedUnknownCategoryOccurrences"], 1)
        self.assertEqual(counts["uniqueRandomizedPlugHashesWithCategory"], 1)

    def test_distinct_hashes_not_occurrences(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"].append(
            dict(self.rows[0]["resolvedPlugSets"][0]["plugs"][0]))
        result = audit_weapon_plug_categories(self.rows)
        self.assertEqual(result["counts"]["randomizedOccurrences"], 3)
        self.assertEqual(result["counts"]["uniqueRandomizedPlugHashes"], 2)
        self.assertEqual(result["randomizedCategoryIdentifiersByOccurrence"][0]["occurrences"], 2)

    def test_redacted_and_fake_sets_not_certified(self):
        entry = self.rows[0]["resolvedPlugSets"][0]
        entry["isFakePlugSet"] = True
        entry["plugs"][0]["plugRedacted"] = True
        result = audit_weapon_plug_categories(self.rows)
        self.assertEqual(result["counts"]["randomizedFakeSetOccurrences"], 2)
        self.assertEqual(result["counts"]["randomizedRedactedPlugOccurrences"], 1)
        self.assertIsNone(result["certifiedTraitCount"])
        self.assertIsNone(result["certifiedEnhancedPerkCount"])

    def test_missing_category_identifier_is_unknown(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryIdentifier"] = ""
        result = audit_weapon_plug_categories(self.rows)
        self.assertEqual(result["counts"]["randomizedUnknownCategoryOccurrences"], 2)

    def test_duplicate_weapon_hash_rejected(self):
        with self.assertRaises(ValueError):
            audit_weapon_plug_categories(self.rows + self.rows)

    def test_invalid_category_hash_rejected(self):
        for bad in (True, -1, "12", 2 ** 32):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryHash"] = bad
                audit_weapon_plug_categories(self.rows)

    def test_no_roll_or_performance_certification(self):
        result = audit_weapon_plug_categories(self.rows)
        self.assertIsNone(result["certifiedObtainableRollCount"])
        self.assertFalse(result["certifiedPvEOrPvPPerformance"])
        self.assertTrue(result["manifestDefinitionOnly"])


if __name__ == "__main__":
    unittest.main()
