"""Synthetic tests: named memberships do not certify obtainable rolls."""
import unittest
from scripts.category_role_digest import build_category_role_digest


class CategoryRoleDigestTests(unittest.TestCase):
    def setUp(self):
        self.data = {"categories": [
            {"categoryHash": 10, "identifier": "frames",
             "roleScreen": "unclassified_not_trait_certified", "occurrences": 2,
             "uniqueWeaponDefinitions": 1, "sampleNamedDefinitionMemberships": [
                 {"itemHash": 7, "weaponName": "Example Weapon",
                  "plugHash": 8, "plugName": "Example Plug"}]},
            {"categoryHash": 9, "identifier": "barrels",
             "roleScreen": "explicit_component_label", "occurrences": 3,
             "uniqueWeaponDefinitions": 2, "sampleNamedDefinitionMemberships": []},
        ]}

    def test_sorted_and_preserves_identity(self):
        rows = build_category_role_digest(self.data)["categories"]
        self.assertEqual([r["identifier"] for r in rows], ["barrels", "frames"])
        self.assertEqual(rows[1]["categoryHash"], 10)

    def test_exact_membership_example(self):
        example = build_category_role_digest(self.data)["categories"][1]["exampleSameManifestMembership"]
        self.assertEqual(example, {"itemHash": 7, "weaponName": "Example Weapon",
                                   "plugHash": 8, "plugName": "Example Plug"})

    def test_empty_samples_remain_null(self):
        self.assertIsNone(build_category_role_digest(self.data)["categories"][0]["exampleSameManifestMembership"])

    def test_no_roll_certification(self):
        report = build_category_role_digest(self.data)
        self.assertEqual(report["evidenceGrade"], "same_manifest_definition_only")
        self.assertTrue(all(not r["certifiedPlayableTrait"] and
                            not r["certifiedObtainableRoll"] and
                            not r["certifiedEnhancedPerk"] for r in report["categories"]))

    def test_duplicate_category_rejected(self):
        self.data["categories"].append(dict(self.data["categories"][0]))
        with self.assertRaises(ValueError):
            build_category_role_digest(self.data)

    def test_bad_hash_rejected(self):
        for h in (-1, True, 2**32):
            with self.subTest(h=h):
                self.data["categories"][0]["categoryHash"] = h
                with self.assertRaises(ValueError):
                    build_category_role_digest(self.data)

    def test_bad_sample_is_not_guessed(self):
        self.data["categories"][0]["sampleNamedDefinitionMemberships"] = [
            {"itemHash": 7, "weaponName": "", "plugHash": 8, "plugName": "Plug"}]
        self.assertIsNone(build_category_role_digest(self.data)["categories"][1]["exampleSameManifestMembership"])

    def test_frames_with_trait_like_name_stays_uncertified(self):
        # Live October 2026 manifest sample includes 'Adagio' under 'frames'.
        # A category label must never be used to discard or certify a perk.
        self.data["categories"][0]["sampleNamedDefinitionMemberships"][0]["plugName"] = "Adagio"
        rows = build_category_role_digest(self.data)["categories"]
        frames = next(r for r in rows if r["identifier"] == "frames")
        self.assertEqual(frames["exampleSameManifestMembership"]["plugName"], "Adagio")
        self.assertFalse(frames["certifiedPlayableTrait"])
        self.assertFalse(frames["certifiedObtainableRoll"])
        self.assertFalse(frames["certifiedEnhancedPerk"])

    def test_bad_structure_rejected(self):
        for bad in (None, {}, {"categories": "wrong"}):
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                build_category_role_digest(bad)


if __name__ == "__main__":
    unittest.main()
