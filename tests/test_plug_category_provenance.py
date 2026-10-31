"""Synthetic category provenance tests; no gameplay or roll certification."""
import unittest
from scripts.plug_category_provenance import audit_category_provenance


class CategoryProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"itemHash": 101, "resolvedPlugSets": [
                {"kind": "randomized", "definitionFound": True,
                 "isFakePlugSet": False, "redacted": False, "plugs": [
                     {"plugItemHash": 8, "plugCategoryHash": 55,
                      "plugCategoryIdentifier": "weapon.perks",
                      "currentlyCanRoll": True, "plugRedacted": False},
                     {"plugItemHash": 9, "plugCategoryHash": 55,
                      "plugCategoryIdentifier": "weapon.perks",
                      "currentlyCanRoll": None, "plugRedacted": False},
                 ]},
                {"kind": "reusable", "definitionFound": True, "plugs": [
                    {"plugItemHash": 7, "plugCategoryHash": 1,
                     "plugCategoryIdentifier": "barrels"}]},
            ]},
            {"itemHash": 102, "resolvedPlugSets": [
                {"kind": "randomized", "definitionFound": True,
                 "isFakePlugSet": True, "redacted": False, "plugs": [
                     {"plugItemHash": 8, "plugCategoryHash": 55,
                      "plugCategoryIdentifier": "weapon.perks",
                      "currentlyCanRoll": True, "plugRedacted": False},
                ]},
                {"kind": "randomized", "definitionFound": False, "plugs": None},
            ]},
        ]

    def test_unique_hashes_and_weapons_not_occurrences(self):
        result = audit_category_provenance(self.rows)
        category = result["categories"][0]
        self.assertEqual(category["occurrences"], 3)
        self.assertEqual(category["uniquePlugHashes"], 2)
        self.assertEqual(category["uniqueWeaponDefinitions"], 2)
        self.assertEqual(result["counts"]["unresolvedRandomizedSets"], 1)

    def test_provenance_states_separated(self):
        category = audit_category_provenance(self.rows)["categories"][0]
        self.assertEqual(category["fullyExplicitDefinitionFlagOccurrences"], 1)
        self.assertEqual(category["explicitlyExcludedOccurrences"], 1)
        self.assertEqual(category["unknownProvenanceOccurrences"], 1)

    def test_unknown_category_is_not_inferred(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryIdentifier"] = None
        result = audit_category_provenance(self.rows)
        self.assertEqual(result["counts"]["unknownCategoryOccurrences"], 1)

    def test_same_plug_hash_conflicting_identity_flagged(self):
        self.rows[1]["resolvedPlugSets"][0]["plugs"][0]["plugCategoryHash"] = 99
        result = audit_category_provenance(self.rows)
        self.assertEqual(result["counts"]["plugHashesWithConflictingCategoryIdentity"], 1)
        self.assertEqual(result["conflictingCategoryIdentityExamples"][0]["plugHash"], 8)

    def test_reusable_does_not_inflate_randomized(self):
        result = audit_category_provenance(self.rows)
        self.assertEqual(result["counts"]["randomizedOccurrences"], 3)
        self.assertEqual(result["counts"]["uniqueCategoryIdentities"], 1)

    def test_false_roll_flag_excluded_not_clear(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["currentlyCanRoll"] = False
        category = audit_category_provenance(self.rows)["categories"][0]
        self.assertEqual(category["explicitlyExcludedOccurrences"], 2)
        self.assertEqual(category["fullyExplicitDefinitionFlagOccurrences"], 0)

    def test_unknown_set_flags_do_not_become_clear(self):
        self.rows[0]["resolvedPlugSets"][0]["isFakePlugSet"] = None
        category = audit_category_provenance(self.rows)["categories"][0]
        self.assertEqual(category["fullyExplicitDefinitionFlagOccurrences"], 0)
        self.assertEqual(category["unknownProvenanceOccurrences"], 2)

    def test_bad_flags_rejected(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["currentlyCanRoll"] = 1
        with self.assertRaises(ValueError):
            audit_category_provenance(self.rows)

    def test_duplicate_weapon_rejected(self):
        with self.assertRaises(ValueError):
            audit_category_provenance(self.rows + self.rows)

    def test_no_certification(self):
        result = audit_category_provenance(self.rows)
        self.assertIsNone(result["certifiedObtainableRollCount"])
        self.assertIsNone(result["certifiedEnhancedPerkCount"])
        self.assertFalse(result["certifiedPvEOrPvPPerformance"])


if __name__ == "__main__":
    unittest.main()
