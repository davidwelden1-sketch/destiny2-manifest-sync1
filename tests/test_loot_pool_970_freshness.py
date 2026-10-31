import unittest

from simulator.loot_pool_970_freshness import (
    SOURCE_DATE, SOURCE_URL, audit_loot_pool_freshness,
)


class LootPool970FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.kw = dict(item_hash=123456, source_kind="raid",
                       pre_edge_of_fate=True, craftable=True,
                       observation_date="2026-06-08", activity="pve")

    def classify(self, **changes):
        return audit_loot_pool_freshness(**{**self.kw, **changes})

    def test_old_craftable_raid_pool_requires_revalidation(self):
        r = self.classify()
        self.assertTrue(r["perk_pool_revalidation_required"])
        self.assertTrue(r["tiered_reward_revalidation_required"])
        self.assertIn("craftable_raid_perk_pool_updated",
                      r["official_source_level_changes"])

    def test_raid_upgrade_not_equivalent_to_enhanced_roll(self):
        r = self.classify()
        self.assertIn("craftable_raid_tier_upgrade_supported",
                      r["official_source_level_changes"])
        self.assertFalse(r["enhanced_perk_legality_verified"])
        self.assertFalse(r["current_exact_perk_pair_verified"])

    def test_post_patch_raid_observation_not_automatically_legal(self):
        r = self.classify(observation_date="2026-06-10")
        self.assertFalse(r["perk_pool_revalidation_required"])
        self.assertFalse(r["current_exact_perk_pair_verified"])

    def test_patch_date_not_before_patch(self):
        r = self.classify(observation_date="2026-06-09")
        self.assertFalse(r["perk_pool_revalidation_required"])

    def test_noncraftable_raid_does_not_inherit_craftable_pool_claim(self):
        r = self.classify(craftable=False)
        self.assertFalse(r["perk_pool_revalidation_required"])
        self.assertTrue(r["tiered_reward_revalidation_required"])
        self.assertNotIn("craftable_raid_perk_pool_updated",
                         r["official_source_level_changes"])

    def test_unknown_craftability_fails_closed(self):
        r = self.classify(craftable=None)
        self.assertFalse(r["perk_pool_revalidation_required"])
        self.assertFalse(r["current_exact_perk_pair_verified"])

    def test_dungeon_origin_traits_need_revalidation(self):
        r = self.classify(source_kind="dungeon", craftable=False)
        self.assertTrue(r["origin_trait_revalidation_required"])
        self.assertFalse(r["perk_pool_revalidation_required"])
        self.assertIn("dungeon_new_origin_traits",
                      r["official_source_level_changes"])

    def test_post_patch_dungeon_origin_observation_not_stale_by_date(self):
        r = self.classify(source_kind="dungeon",
                          observation_date="2026-06-09")
        self.assertFalse(r["origin_trait_revalidation_required"])

    def test_newer_activities_not_automatically_classified(self):
        for kind in ("raid", "dungeon"):
            with self.subTest(kind=kind):
                r = self.classify(source_kind=kind, pre_edge_of_fate=False)
                self.assertEqual(r["official_source_level_changes"], [])
                self.assertFalse(r["tiered_reward_revalidation_required"])

    def test_unknown_age_fails_closed(self):
        r = self.classify(pre_edge_of_fate=None)
        self.assertEqual(r["official_source_level_changes"], [])
        self.assertFalse(r["perk_pool_revalidation_required"])

    def test_destination_does_not_inherit_raid_rules(self):
        r = self.classify(source_kind="destination")
        self.assertEqual(r["official_source_level_changes"], [])
        self.assertFalse(r["tiered_reward_revalidation_required"])

    def test_missing_item_hash_does_not_certify_any_roll(self):
        r = self.classify(item_hash=None)
        self.assertFalse(r["current_exact_perk_pair_verified"])
        self.assertFalse(r["current_acquisition_verified"])

    def test_manifest_mismatch_requires_revalidation(self):
        r = self.classify(observed_manifest_version="old",
                          reference_manifest_version="new")
        self.assertEqual(r["manifest_version_status"],
                         "version_mismatch_revalidate")

    def test_matching_manifest_still_not_roll_certification(self):
        r = self.classify(observed_manifest_version="same",
                          reference_manifest_version="same")
        self.assertEqual(r["manifest_version_status"],
                         "versions_match_not_roll_certification")
        self.assertFalse(r["enhanced_perk_legality_verified"])

    def test_missing_version_comparison_is_explicit(self):
        self.assertEqual(self.classify()["manifest_version_status"],
                         "version_comparison_unavailable")

    def test_activity_specific_artifact_and_no_cross_mode_damage(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                r = self.classify(activity=activity)
                self.assertEqual(r["artifact_enabled"],
                                 False if activity in ("competitive", "trials")
                                 else None)
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_ttk"])
                self.assertFalse(r["gameplay_measured"])

    def test_invalid_inputs_fail_closed(self):
        invalid = (
            {"item_hash": 0}, {"item_hash": True},
            {"source_kind": "unknown"}, {"pre_edge_of_fate": 1},
            {"craftable": "yes"}, {"observation_date": "2026-02-30"},
            {"observation_date": "2026-6-9"},
            {"activity": "unknown"}, {"observed_manifest_version": ""},
            {"reference_manifest_version": 42},
        )
        for change in invalid:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.classify(**change)

    def test_official_source_metadata(self):
        r = self.classify()
        self.assertEqual(SOURCE_DATE, "2026-06-09")
        self.assertIn("destiny_update_9_7_0", SOURCE_URL)
        self.assertEqual(r["evidence_grade"],
                         "official_historical_source_level_patch_only")


if __name__ == "__main__":
    unittest.main()
