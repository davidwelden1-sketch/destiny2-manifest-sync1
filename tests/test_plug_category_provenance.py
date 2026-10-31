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


    def test_missing_names_do_not_invent_examples(self):
        result = audit_category_provenance(self.rows)
        self.assertEqual(result["counts"]["categoriesWithNamedExplicitPlugExamples"], 0)
        self.assertEqual(result["categories"][0]["sampleNamedDefinitionPlugs"], [])

    def test_named_explicit_definition_example(self):
        self.rows[0]["name"] = "Sample Weapon"
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugName"] = "Test Trait"
        result = audit_category_provenance(self.rows)
        category = result["categories"][0]
        self.assertEqual(category["uniqueNamedExplicitPlugHashes"], 1)
        self.assertEqual(category["sampleNamedDefinitionPlugs"], [{"plugHash": 8, "name": "Test Trait"}])
        self.assertEqual(category["sampleWeaponDefinitions"], [{"itemHash": 101, "name": "Sample Weapon"}])
        self.assertEqual(result["counts"]["categoriesWithNamedExplicitPlugExamples"], 1)

    def test_excluded_definition_cannot_supply_example(self):
        self.rows[1]["resolvedPlugSets"][0]["plugs"][0]["plugName"] = "Excluded"
        result = audit_category_provenance(self.rows)
        self.assertEqual(result["categories"][0]["sampleNamedDefinitionPlugs"], [])

    def test_unknown_roll_flag_cannot_supply_example(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][1]["plugName"] = "Unknown"
        self.assertEqual(audit_category_provenance(self.rows)["categories"][0]["sampleNamedDefinitionPlugs"], [])

    def test_conflicting_names_for_same_explicit_hash_rejected(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugName"] = "First"
        self.rows[1]["resolvedPlugSets"][0]["isFakePlugSet"] = False
        self.rows[1]["resolvedPlugSets"][0]["plugs"][0]["plugName"] = "Different"
        with self.assertRaises(ValueError):
            audit_category_provenance(self.rows)

    def test_invalid_plug_name_rejected(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugName"] = 123
        with self.assertRaises(ValueError):
            audit_category_provenance(self.rows)

    def test_example_cap_and_stable_sort(self):
        plugs = self.rows[0]["resolvedPlugSets"][0]["plugs"]
        plugs[:] = [
            {"plugItemHash": h, "plugCategoryHash": 55,
             "plugCategoryIdentifier": "weapon.perks", "plugName": "Name %02d" % (20-h),
             "currentlyCanRoll": True, "plugRedacted": False}
            for h in range(1, 13)
        ]
        result = audit_category_provenance(self.rows)
        category = result["categories"][0]
        self.assertEqual(category["uniqueNamedExplicitPlugHashes"], 12)
        self.assertEqual(len(category["sampleNamedDefinitionPlugs"]), 8)
        self.assertEqual(category["sampleNamedDefinitionPlugs"][0]["name"], "Name 08")

    def test_named_examples_do_not_certify_gameplay(self):
        self.rows[0]["resolvedPlugSets"][0]["plugs"][0]["plugName"] = "Test Trait"
        result = audit_category_provenance(self.rows)
        self.assertIsNone(result["certifiedObtainableRollCount"])
        self.assertIsNone(result["certifiedEnhancedPerkCount"])
        self.assertFalse(result["certifiedPvEOrPvPPerformance"])



if __name__ == "__main__":
    unittest.main()
