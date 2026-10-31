"""Synthetic tests for Bungie's 2026-06-23 9.7.0.2 corrections."""
import unittest

from simulator.patch_9702_evidence import (
    CHANGES, PATCH_DATE, PATCH_VERSION, SOURCE_URL, audit_patch_9702,
)


class Patch9702EvidenceTests(unittest.TestCase):
    def screen(self, change_key="europa_moon_rocket_lead_from_gold",
               observation_date="2026-06-22", activity="pve", **kwargs):
        return audit_patch_9702(
            change_key, observation_date, activity=activity, **kwargs
        )

    def test_kinetic_brick_bug_cannot_calibrate_current_damage_element(self):
        r = self.screen("kinetic_brick_element_conversion")
        self.assertEqual(r["scope"], "weapon_damage_type_and_ammo")
        self.assertIn("non-Kinetic weapon damage", r["official_fact"])
        self.assertTrue(r["revalidation_required"])
        self.assertFalse(r["gameplay_measured"])
        self.assertIsNone(r["damage_ownership"])

    def test_catalyst_progression_fix_does_not_certify_catalyst(self):
        r = self.screen("exotic_catalyst_progression", "2026-06-24")
        self.assertIn("Fafnir", r["official_fact"])
        self.assertEqual(r["status"], "post_fix_observation_not_gameplay_certification")
        self.assertFalse(r["current_roll_or_enhancement_verified"])

    def test_historical_europa_moon_rocket_roll_invalidated(self):
        r = self.screen()
        self.assertEqual(r["status"], "pre_fix_observation_requires_revalidation")
        self.assertIn("Impromptu Ammunition", r["official_fact"])
        self.assertTrue(r["revalidation_required"])
        self.assertFalse(r["current_roll_or_enhancement_verified"])

    def test_raid_adept_inventory_trait_rewrite(self):
        r = self.screen("raid_adept_perk_sync")
        self.assertIn("inventory traits were updated", r["official_fact"])
        self.assertTrue(r["revalidation_required"])

    def test_cynosure_tier_does_not_certify_specific_roll(self):
        r = self.screen("cynosure_higher_tier_extra_traits", "2026-07-01")
        self.assertEqual(r["status"], "post_fix_observation_not_gameplay_certification")
        self.assertFalse(r["current_weapon_hash_verified"])

    def test_ergo_sum_vortex_ammo_historical_only(self):
        r = self.screen("ergo_sum_vortex_heavy_ammo")
        self.assertIn("6 to 4", r["official_fact"])
        self.assertIsNone(r["pve_boss_dps"])

    def test_frostees_only_pvp_scope(self):
        self.assertEqual(self.screen("frostees_frost_armor_pvp")["status"],
                         "not_supported_for_this_activity_by_source")
        r = self.screen("frostees_frost_armor_pvp", activity="pvp")
        self.assertTrue(r["revalidation_required"])
        self.assertIsNone(r["pve_damage_resistance"])

    def test_lethal_current_pvp_one_shot_no_ttk_claim(self):
        r = self.screen("hunter_lethal_current_multi_proc", activity="pvp")
        self.assertIn("one-shots", r["official_fact"])
        self.assertIsNone(r["pvp_guardian_ttk"])

    def test_pit_of_heresy_scorch_no_damage_multiplier(self):
        r = self.screen("pit_of_heresy_four_piece")
        self.assertIn("20+10", r["official_fact"])
        self.assertIsNone(r["damage_ownership"])

    def test_artifact_cooldown_and_prismatic_activation_not_certified(self):
        for key in ("vile_weave_tangle_cooldown", "unto_the_breach_prismatic",
                    "artifact_duplicate_restriction"):
            with self.subTest(key=key):
                r = self.screen(key)
                self.assertFalse(r["current_artifact_selection_verified"])
                self.assertFalse(r["gameplay_measured"])

    def test_competitive_and_trials_artifact_off(self):
        for activity in ("competitive", "trials"):
            with self.subTest(activity=activity):
                r = self.screen("unto_the_breach_prismatic", activity=activity)
                self.assertIs(r["artifact_enabled"], False)
                self.assertFalse(r["current_artifact_selection_verified"])

    def test_patch_day_uncertain_and_post_patch_not_certified(self):
        self.assertEqual(self.screen(observation_date=PATCH_DATE)["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(self.screen(observation_date="2026-06-24")["status"],
                         "post_fix_observation_not_gameplay_certification")

    def test_source_version_mismatch_fails_closed(self):
        r = self.screen(source_patch_version="9.7.0.6")
        self.assertEqual(r["status"], "source_patch_version_mismatch")
        self.assertFalse(r["revalidation_required"])

    def test_invalid_inputs_fail_closed(self):
        cases = (
            ("not_real", "2026-06-22", "pve", {}),
            ("europa_moon_rocket_lead_from_gold", "2026-6-22", "pve", {}),
            ("europa_moon_rocket_lead_from_gold", "2026-02-30", "pve", {}),
            ("europa_moon_rocket_lead_from_gold", 20260622, "pve", {}),
            ("europa_moon_rocket_lead_from_gold", "2026-06-22", "gambit", {}),
            ("europa_moon_rocket_lead_from_gold", "2026-06-22", "pve",
             {"source_patch_version": ""}),
        )
        for key, when, mode, kwargs in cases:
            with self.subTest(key=key, when=when, mode=mode):
                with self.assertRaises(ValueError):
                    self.screen(key, when, mode, **kwargs)

    def test_all_known_changes_have_official_provenance(self):
        self.assertEqual(len(CHANGES), 12)
        self.assertEqual(PATCH_VERSION, "9.7.0.2")
        self.assertEqual(PATCH_DATE, "2026-06-23")
        self.assertIn("bungie.net", SOURCE_URL)
        for key in CHANGES:
            with self.subTest(key=key):
                r = self.screen(key)
                self.assertEqual(r["evidence_grade"], "official_historical_patch_note_only")
                self.assertFalse(r["current_roll_or_enhancement_verified"])
                self.assertIsNone(r["pvp_guardian_ttk"])


if __name__ == "__main__":
    unittest.main()
