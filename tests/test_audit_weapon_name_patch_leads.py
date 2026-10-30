import unittest

from scripts.audit_weapon_name_patch_leads import audit_name_level_patch_leads


class NameLevelPatchLeadTests(unittest.TestCase):
    def setUp(self):
        self.variants = [
            {"item_hash": 3003492238, "weapon_name": "Zephyr",
             "source_url": "https://www.light.gg/db/items/3003492238/zephyr/",
             "source_reviewed_on": "2026-10-30"},
            {"item_hash": 1911078836, "weapon_name": "Zephyr",
             "source_url": "https://www.light.gg/db/items/1911078836/zephyr/",
             "source_reviewed_on": "2026-10-30"},
            {"item_hash": 100, "weapon_name": "Unrelated Sword",
             "source_url": "https://example.org/sword",
             "source_reviewed_on": "2026-10-29"},
        ]
        self.patches = [
            {"patch_id": "bungie-9701-zephyr", "weapon_name": "Zephyr",
             "effective_date": "2026-06-16",
             "source_url": "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_1",
             "correction_type": "perk_column_orientation"}
        ]

    def audit(self, variants=None, patches=None, checked_on="2026-10-30"):
        return audit_name_level_patch_leads(
            self.variants if variants is None else variants,
            self.patches if patches is None else patches, checked_on)

    def test_name_level_matches_all_variants_but_not_exact_hash_scope(self):
        r = self.audit()
        self.assertEqual(r["variants_reviewed"], 3)
        self.assertEqual(r["potential_name_matches"], 2)
        for row in r["per_item_hash"]:
            if row["weapon_name"] == "Zephyr":
                self.assertEqual(row["exact_hash_affected"], "unknown")
                self.assertEqual(row["potential_name_level_patch_ids"],
                                 ["bungie-9701-zephyr"])
                self.assertEqual(row["roll_legality"], "unverified")
                self.assertEqual(row["enhanced_perk_legality"], "unverified")
                self.assertEqual(row["current_acquisition"], "unverified")
            else:
                self.assertEqual(row["exact_hash_affected"], "no_name_match")

    def test_casefold_name_only_and_distinct_hashes(self):
        variants = [dict(self.variants[0], weapon_name="zEpHyR")]
        r = self.audit(variants=variants)
        self.assertEqual(r["potential_name_matches"], 1)
        self.assertEqual(r["per_item_hash"][0]["item_hash"], 3003492238)

    def test_empty_patches_never_certify_rolls(self):
        r = self.audit(patches=[])
        self.assertEqual(r["potential_name_matches"], 0)
        self.assertTrue(all(x["roll_legality"] == "unverified"
                            for x in r["per_item_hash"]))

    def test_duplicate_or_bool_hash_rejected(self):
        for variants in ([self.variants[0], self.variants[0]],
                         [dict(self.variants[0], item_hash=True)],
                         [dict(self.variants[0], item_hash=0)]):
            with self.subTest(variants=variants), self.assertRaises(ValueError):
                self.audit(variants=variants)

    def test_untrusted_patch_url_rejected(self):
        for url in ("http://www.bungie.net/patch",
                    "https://fake-bungie.net/patch",
                    "https://www.bungie.net.evil.com/patch"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.audit(patches=[dict(self.patches[0], source_url=url)])

    def test_future_patch_and_catalog_review_rejected(self):
        with self.assertRaisesRegex(ValueError, "Future patch"):
            self.audit(patches=[dict(self.patches[0],
                                    effective_date="2026-11-01")])
        with self.assertRaisesRegex(ValueError, "Future catalog"):
            self.audit(variants=[dict(self.variants[0],
                                      source_reviewed_on="2026-11-01")])

    def test_duplicate_patch_id_and_invalid_type_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate patch_id"):
            self.audit(patches=self.patches * 2)
        with self.assertRaisesRegex(ValueError, "Unsupported correction"):
            self.audit(patches=[dict(self.patches[0],
                                    correction_type="damage_buff")])

    def test_bad_date_and_source_url_rejected(self):
        with self.assertRaises(ValueError):
            self.audit(checked_on="tomorrow")
        with self.assertRaises(ValueError):
            self.audit(variants=[dict(self.variants[0],
                                      source_url="http://example.org")])

    def test_empty_inputs_are_valid(self):
        r = self.audit(variants=[], patches=[])
        self.assertEqual(r["variants_reviewed"], 0)
        self.assertEqual(r["per_item_hash"], [])


if __name__ == "__main__":
    unittest.main()
