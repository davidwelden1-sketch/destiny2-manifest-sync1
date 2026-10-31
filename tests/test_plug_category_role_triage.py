"""Synthetic role-triage regression tests; never claim live-game legality."""
import copy
import unittest

from scripts.plug_category_role_triage import triage_category_roles


class CategoryRoleTriageTests(unittest.TestCase):
    def setUp(self):
        self.provenance = {"categories": [
            {"categoryHash": 11, "identifier": "barrels", "occurrences": 3,
             "uniqueWeaponDefinitions": 2,
             "sampleNamedDefinitionMemberships": [
                 {"itemHash": 101, "weaponName": "Example", "plugHash": 7, "plugName": "Test"}]},
            {"categoryHash": 12, "identifier": "frames", "occurrences": 2,
             "uniqueWeaponDefinitions": 1, "sampleNamedDefinitionMemberships": []},
        ]}
        self.socket_map = {"categories": [
            {"categoryHash": 11, "identifier": "barrels", "uniqueWeaponDefinitions": 2,
             "socketPositions": [{"socketIndex": 1, "occurrences": 3}]},
            {"categoryHash": 12, "identifier": "frames", "uniqueWeaponDefinitions": 1,
             "socketPositions": [{"socketIndex": 3, "occurrences": 2}]},
        ]}

    def test_component_and_frames_remains_unknown(self):
        report = triage_category_roles(self.provenance, self.socket_map)
        self.assertEqual(report["counts"], {
            "categoryIdentities": 2, "explicitComponentLabelCategories": 1,
            "unclassifiedCategories": 1})
        self.assertEqual(report["categories"][0]["roleScreen"], "explicit_component_label")
        self.assertEqual(report["categories"][1]["roleScreen"],
                         "unclassified_not_trait_certified")
        self.assertEqual(report["categories"][0]["socketPositions"], [1])
        self.assertEqual(len(report["categories"][0]["sampleNamedDefinitionMemberships"]), 1)

    def test_never_certifies_obtainability_enhancement_or_damage(self):
        report = triage_category_roles(self.provenance, self.socket_map)
        self.assertIsNone(report["certifiedPlayableTraitCount"])
        self.assertIsNone(report["certifiedObtainableRollCount"])
        self.assertIsNone(report["certifiedEnhancedPerkCount"])
        self.assertFalse(report["gameplayMeasured"])
        self.assertTrue(all(not x["certifiedWeaponTrait"] for x in report["categories"]))

    def test_category_identity_mismatch_rejected(self):
        self.socket_map["categories"][0]["categoryHash"] = 99
        with self.assertRaises(ValueError):
            triage_category_roles(self.provenance, self.socket_map)

    def test_weapon_membership_mismatch_rejected(self):
        self.socket_map["categories"][0]["uniqueWeaponDefinitions"] = 3
        with self.assertRaises(ValueError):
            triage_category_roles(self.provenance, self.socket_map)

    def test_occurrence_mismatch_rejected(self):
        self.socket_map["categories"][0]["socketPositions"][0]["occurrences"] = 2
        with self.assertRaises(ValueError):
            triage_category_roles(self.provenance, self.socket_map)

    def test_duplicate_category_rejected(self):
        self.provenance["categories"].append(copy.deepcopy(self.provenance["categories"][0]))
        with self.assertRaises(ValueError):
            triage_category_roles(self.provenance, self.socket_map)

    def test_unknown_component_name_not_guessed(self):
        self.provenance["categories"][0]["identifier"] = "barrels_v2"
        self.socket_map["categories"][0]["identifier"] = "barrels_v2"
        report = triage_category_roles(self.provenance, self.socket_map)
        self.assertEqual(report["counts"]["explicitComponentLabelCategories"], 0)

    def test_missing_and_invalid_category_rejected(self):
        for bad in (None, "", 3):
            self.provenance["categories"][0]["identifier"] = bad
            with self.assertRaises(ValueError):
                triage_category_roles(self.provenance, self.socket_map)

    def test_sample_cap(self):
        self.provenance["categories"][0]["sampleNamedDefinitionMemberships"] = [
            {"itemHash": i} for i in range(20)]
        report = triage_category_roles(self.provenance, self.socket_map)
        self.assertEqual(len(report["categories"][0]["sampleNamedDefinitionMemberships"]), 4)


if __name__ == "__main__":
    unittest.main()
