"""Synthetic tests for Bungie's 2026-06-23 named weapon corrections."""
import unittest
from simulator.patch_9702_black_armory_discord import review_patch_interaction as review


class Patch9702NamedWeaponTests(unittest.TestCase):
    def test_forge_kin_non_enhanced_multi_weapon_historical_only(self):
        r = review(event="forge_kin_black_armory_non_enhanced", activity="pve",
                   observation_date="2026-07-01", weapon_version="non_enhanced",
                   black_armory_count=2)
        self.assertEqual(r["status"], "historical_patch_candidate_only")
        self.assertFalse(r["certified_for_app_build_recommendation"])
        self.assertIsNone(r["pve_boss_dps_measured"])

    def test_enhanced_version_not_claimed(self):
        r = review(event="forge_kin_black_armory_non_enhanced", activity="pvp",
                   observation_date="2026-07-01", weapon_version="enhanced",
                   black_armory_count=3)
        self.assertEqual(r["status"], "enhanced_variant_not_addressed_by_patch")
        self.assertFalse(r["enhanced_perk_legality_verified"])

    def test_missing_equipment_and_variant_fail_closed(self):
        k = dict(event="forge_kin_black_armory_non_enhanced", activity="pve",
                 observation_date="2026-07-01")
        self.assertEqual(review(**k)["status"], "weapon_variant_unresolved")
        self.assertEqual(review(**k, weapon_version="non_enhanced",
                                black_armory_count=1)["status"],
                         "multiple_black_armory_equipment_not_established")

    def test_discord_named_patch_not_obtainable_roll_proof(self):
        r = review(event="lingering_dread_discord", activity="pve",
                   observation_date="2026-07-01")
        self.assertIn("Discord", r["official_fact"])
        self.assertFalse(r["perk_pool_verified"])
        self.assertFalse(r["current_obtainability_verified"])
        self.assertFalse(r["damage_ownership_verified"])

    def test_pve_pvp_separate_unmeasured(self):
        for activity in ("pve", "pvp"):
            r = review(event="lingering_dread_discord", activity=activity,
                       observation_date="2026-07-01")
            self.assertIsNone(r["pve_boss_dps_measured"])
            self.assertIsNone(r["pvp_guardian_ttk_measured"])

    def test_competitive_trials_artifact_disabled(self):
        for activity in ("competitive", "trials"):
            r = review(event="lingering_dread_discord", activity=activity,
                       observation_date="2026-07-01", artifact_name="Example",
                       artifact_perks=["Example perk"])
            self.assertIs(r["artifact_effects_enabled"], False)
            self.assertFalse(r["artifact_allocation_verified"])

    def test_historical_boundaries(self):
        k = dict(event="lingering_dread_discord", activity="pvp")
        self.assertEqual(review(**k, observation_date="2026-06-22")["status"],
                         "pre_fix_observation_invalid_for_post_fix_calibration")
        self.assertEqual(review(**k, observation_date="2026-06-23")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(review(**k, observation_date="2026-06-24",
                                source_patch_version="9.7.0.6")["status"],
                         "source_patch_mismatch")

    def test_invalid_inputs(self):
        base = dict(event="lingering_dread_discord", activity="pve",
                    observation_date="2026-07-01")
        cases = (dict(event="fake"), dict(activity="gambit"),
                 dict(observation_date="2026-7-1"),
                 dict(observation_date="2026-02-30"),
                 dict(weapon_version="enhanced"), dict(black_armory_count=2),
                 dict(artifact_perks=["X"]), dict(artifact_name=""),
                 dict(artifact_name="X", artifact_perks=["a", "a"]),
                 dict(artifact_name="X", artifact_perks=["a"] * 8),
                 dict(manifest_version=""), dict(source_patch_version=""))
        for change in cases:
            with self.subTest(change=change), self.assertRaises(ValueError):
                review(**dict(base, **change))

    def test_bool_equipment_count_rejected(self):
        with self.assertRaises(ValueError):
            review(event="forge_kin_black_armory_non_enhanced", activity="pve",
                   observation_date="2026-07-01", black_armory_count=True)


if __name__ == "__main__":
    unittest.main()
