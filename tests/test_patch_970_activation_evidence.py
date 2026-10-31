"""Synthetic scope tests for official 9.7.0 weapon activation fixes."""
import unittest

from simulator.patch_970_activation_evidence import (
    CORRECTIONS, PATCH_DATE, PATCH_VERSION, SOURCE_URL, audit_weapon_activation,
)


class WeaponActivation970Tests(unittest.TestCase):
    def screen(self, key="paracausal_fluid_sword_activation",
               when="2026-06-08", **kwargs):
        kwargs.setdefault("activity", "pve")
        kwargs.setdefault("event", CORRECTIONS[key]["event"] if key in CORRECTIONS else "x")
        return audit_weapon_activation(key, when, **kwargs)

    def test_all_seven_official_fixes_are_distinct_and_sourced(self):
        self.assertEqual(len(CORRECTIONS), 7)
        self.assertEqual(PATCH_DATE, "2026-06-09")
        self.assertEqual(PATCH_VERSION, "9.7.0")
        self.assertIn("bungie.net", SOURCE_URL)
        for key, rule in CORRECTIONS.items():
            with self.subTest(key=key):
                r = self.screen(key, class_name=rule["class"],
                                weapon_name=rule["weapon"])
                self.assertTrue(r["revalidation_required"])
                self.assertFalse(r["activation_measured"])
                self.assertFalse(r["current_roll_or_enhancement_verified"])
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_guardian_ttk"])

    def test_paracausal_sword_and_high_health_are_separate_conditions(self):
        a = self.screen("paracausal_fluid_sword_activation")
        b = self.screen("paracausal_fluid_high_health_activation")
        self.assertNotEqual(a["event"], b["event"])
        self.assertEqual(self.screen(
            "paracausal_fluid_sword_activation",
            event="high_health_target_activation")["status"],
            "event_scope_not_established")

    def test_hud_x2_does_not_prove_second_damage_stack(self):
        r = self.screen("paracausal_fluid_hud_stack")
        self.assertEqual(r["scope"], "hud_not_damage_stacking")
        self.assertIn("no extra benefit", r["official_fact"])
        self.assertFalse(r["buff_stacks_verified"])
        self.assertIsNone(r["damage_ownership"])

    def test_hunter_tether_not_transferred_to_titan_or_warlock(self):
        key = "aggregate_charge_hunter_tether"
        self.assertTrue(self.screen(key, class_name="hunter")["revalidation_required"])
        for cls in (None, "titan", "warlock"):
            self.assertEqual(self.screen(key, class_name=cls)["status"],
                             "class_scope_not_established")

    def test_cusp_fix_does_not_generalize_to_other_withering_gaze_weapons(self):
        key = "cusp_sempiternal_withering_gaze"
        self.assertTrue(self.screen(key, weapon_name="Cusp Sempiternal")
                        ["revalidation_required"])
        self.assertEqual(self.screen(key, weapon_name="Other weapon")["status"],
                         "weapon_identity_not_established")
        self.assertEqual(self.screen(key)["status"], "weapon_identity_not_established")

    def test_merciless_banner_shield_is_weapon_specific(self):
        key = "merciless_banner_shield"
        self.assertTrue(self.screen(key, weapon_name="Merciless")["revalidation_required"])
        self.assertEqual(self.screen(key, weapon_name="Borealis")["status"],
                         "weapon_identity_not_established")

    def test_monte_carlo_ammo_meter_is_not_measured_ammo_brick_count(self):
        r = self.screen("monte_carlo_bayonet", weapon_name="Monte Carlo")
        self.assertEqual(r["scope"], "kill_attribution_ammo_meter")
        self.assertFalse(r["activation_measured"])
        self.assertIsNone(r["damage_ownership"])

    def test_pve_and_pvp_do_not_share_measured_numbers(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            r = self.screen("paracausal_fluid_sword_activation",
                            when="2026-06-10", activity=activity)
            self.assertEqual(r["status"], "post_fix_not_gameplay_certification")
            self.assertIsNone(r["pve_boss_dps"])
            self.assertIsNone(r["pvp_guardian_ttk"])
            if activity in ("competitive", "trials"):
                self.assertIs(r["artifact_enabled"], False)
            else:
                self.assertIsNone(r["artifact_enabled"])

    def test_patch_day_and_source_mismatch_are_uncertainty(self):
        self.assertEqual(self.screen(when=PATCH_DATE)["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(self.screen(source_patch_version="9.7.0.3")["status"],
                         "source_patch_version_mismatch")
        self.assertFalse(self.screen(when="2026-06-10")["revalidation_required"])

    def test_invalid_inputs_fail_closed(self):
        cases = (
            ("missing", "2026-06-08", {}),
            ("paracausal_fluid_sword_activation", "2026-6-8", {}),
            ("paracausal_fluid_sword_activation", "2026-02-30", {}),
            ("paracausal_fluid_sword_activation", 20260608, {}),
            ("paracausal_fluid_sword_activation", "2026-06-08", {"activity": "gambit"}),
            ("paracausal_fluid_sword_activation", "2026-06-08", {"class_name": "druid"}),
            ("paracausal_fluid_sword_activation", "2026-06-08", {"event": ""}),
            ("paracausal_fluid_sword_activation", "2026-06-08", {"weapon_name": ""}),
            ("paracausal_fluid_sword_activation", "2026-06-08",
             {"source_patch_version": ""}),
        )
        for key, when, kw in cases:
            with self.subTest(key=key, when=when, kw=kw):
                with self.assertRaises(ValueError):
                    self.screen(key, when, **kw)


if __name__ == "__main__":
    unittest.main()
