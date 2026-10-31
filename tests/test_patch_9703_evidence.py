"""Synthetic regression tests for official 2026-07-07 patch scope."""
import unittest

from simulator.patch_9703_evidence import (
    CHANGES, PATCH_DATE, PATCH_VERSION, SOURCE_URL, audit_patch_9703,
)


class Patch9703EvidenceTests(unittest.TestCase):
    def screen(self, key="pantheon_insurrection_prime_divinity_cage",
               when="2026-07-06", **kwargs):
        kwargs.setdefault("activity", "pve")
        return audit_patch_9703(key, when, **kwargs)

    def test_divinity_cage_invalidates_old_insurrection_prime_boss_dps(self):
        r = self.screen(encounter="pantheon_insurrection_prime")
        self.assertEqual(r["status"], "pre_fix_observation_requires_revalidation")
        self.assertIn("no longer damage Insurrection Prime", r["official_fact"])
        self.assertIsNone(r["pve_boss_dps"])
        self.assertIsNone(r["damage_ownership"])

    def test_divinity_cage_does_not_globalize_to_other_bosses(self):
        for encounter in (None, "other_boss", "pantheon_consecrated_mind"):
            with self.subTest(encounter=encounter):
                r = self.screen(encounter=encounter)
                self.assertEqual(r["status"], "encounter_scope_not_established")
                self.assertFalse(r["revalidation_required"])

    def test_divinity_cage_cannot_be_used_as_pvp_damage_evidence(self):
        r = self.screen(activity="pvp", encounter="pantheon_insurrection_prime")
        self.assertEqual(r["status"], "not_supported_for_activity")
        self.assertIsNone(r["pvp_guardian_ttk"])

    def test_consecrated_mind_remote_tether_is_encounter_specific(self):
        r = self.screen("pantheon_consecrated_mind_remote_tether",
                        encounter="pantheon_consecrated_mind")
        self.assertTrue(r["revalidation_required"])
        self.assertEqual(self.screen("pantheon_consecrated_mind_remote_tether",
                         encounter="pantheon_insurrection_prime")["status"],
                         "encounter_scope_not_established")

    def test_hunter_phantom_surge_requires_hunter_scope(self):
        for activity in ("pve", "pvp"):
            r = self.screen("hunter_phantom_surge_stylish_executioner",
                            activity=activity, class_name="hunter")
            self.assertTrue(r["revalidation_required"])
            self.assertIsNone(r["damage_ownership"])
        self.assertEqual(self.screen("hunter_phantom_surge_stylish_executioner",
                         class_name="warlock")["status"],
                         "class_scope_not_established")

    def test_ward_of_dawn_pvp_scope_not_pve_or_other_classes(self):
        key = "titan_ward_of_dawn_projectile_block"
        self.assertEqual(self.screen(key, class_name="titan")["status"],
                         "not_supported_for_activity")
        self.assertEqual(self.screen(key, activity="pvp", class_name="warlock")["status"],
                         "class_scope_not_established")
        r = self.screen(key, activity="pvp", class_name="titan")
        self.assertTrue(r["revalidation_required"])
        self.assertIsNone(r["pve_damage_resistance"])

    def test_artifact_pack_tactics_disabled_in_competitive_and_trials(self):
        for activity in ("competitive", "trials"):
            r = self.screen("pack_tactics_performance", activity=activity)
            self.assertEqual(r["status"], "artifact_disabled_in_activity")
            self.assertIs(r["artifact_enabled"], False)
            self.assertFalse(r["current_artifact_selection_verified"])

    def test_pack_tactics_performance_does_not_imply_damage_or_uptime(self):
        r = self.screen("pack_tactics_performance", when="2026-07-08")
        self.assertEqual(r["status"], "post_fix_not_gameplay_certification")
        self.assertIsNone(r["pve_boss_dps"])
        self.assertFalse(r["gameplay_measured"])

    def test_backfang_focusing_is_not_a_legal_roll_certification(self):
        r = self.screen("backfang_drifter_focusing", when="2026-07-08")
        self.assertEqual(r["scope"], "weapon_acquisition_focusing")
        self.assertFalse(r["current_weapon_hash_verified"])
        self.assertFalse(r["current_roll_or_enhancement_verified"])

    def test_patch_day_and_version_mismatch_fail_closed(self):
        self.assertEqual(self.screen(encounter="pantheon_insurrection_prime",
                         when=PATCH_DATE)["status"], "patch_day_deployment_time_unknown")
        self.assertEqual(self.screen(encounter="pantheon_insurrection_prime",
                         when="2026-07-08")["status"], "post_fix_not_gameplay_certification")
        self.assertEqual(self.screen(encounter="pantheon_insurrection_prime",
                         source_patch_version="9.7.0.2")["status"],
                         "source_patch_version_mismatch")

    def test_invalid_inputs_fail_closed(self):
        cases = (
            ("missing", "2026-07-06", {}),
            ("backfang_drifter_focusing", "2026-7-6", {}),
            ("backfang_drifter_focusing", "2026-02-30", {}),
            ("backfang_drifter_focusing", 20260706, {}),
            ("backfang_drifter_focusing", "2026-07-06", {"activity": "gambit"}),
            ("backfang_drifter_focusing", "2026-07-06", {"class_name": "druid"}),
            ("backfang_drifter_focusing", "2026-07-06", {"encounter": ""}),
            ("backfang_drifter_focusing", "2026-07-06", {"source_patch_version": ""}),
        )
        for key, when, kwargs in cases:
            with self.subTest(key=key, when=when, kwargs=kwargs):
                with self.assertRaises(ValueError):
                    self.screen(key, when=when, **kwargs)

    def test_all_changes_are_historical_and_source_scoped(self):
        self.assertEqual(len(CHANGES), 6)
        self.assertEqual(PATCH_VERSION, "9.7.0.3")
        self.assertEqual(PATCH_DATE, "2026-07-07")
        self.assertIn("bungie.net", SOURCE_URL)
        for key in CHANGES:
            with self.subTest(key=key):
                c = CHANGES[key]
                kwargs = {"activity": c["modes"][0]}
                if c["class"]:
                    kwargs["class_name"] = c["class"]
                if c["encounter"]:
                    kwargs["encounter"] = c["encounter"]
                r = self.screen(key, **kwargs)
                self.assertEqual(r["evidence_grade"], "official_historical_patch_note_only")
                self.assertFalse(r["gameplay_measured"])
                self.assertFalse(r["current_roll_or_enhancement_verified"])


if __name__ == "__main__":
    unittest.main()
