"""Synthetic regression tests for historical Crown of Tempests patch evidence."""
import unittest

from simulator.crown_tempests_970_evidence import audit_crown_tempests


class CrownTempests970Tests(unittest.TestCase):
    def screen(self, **overrides):
        kwargs = dict(observation_date="2026-06-10", activity="pve",
                      class_name="warlock", event="ionic_sentry_deploy",
                      tines_stacks=1)
        kwargs.update(overrides)
        return audit_crown_tempests(**kwargs)

    def test_post_patch_one_stack_is_only_official_condition(self):
        result = self.screen()
        self.assertEqual(result["status"], "official_post_patch_condition_only")
        self.assertTrue(result["official_ionic_sentry_storm_grenade_condition_met"])
        self.assertFalse(result["condition_verified_in_game"])
        self.assertIsNone(result["weapon_perk_trigger_from_grenade"])
        self.assertIsNone(result["grenade_kill_attribution"])
        self.assertIsNone(result["ability_energy_refund"])

    def test_zero_stacks_does_not_satisfy_condition(self):
        result = self.screen(tines_stacks=0)
        self.assertEqual(result["status"], "no_conduction_tines_stack")
        self.assertFalse(result["official_ionic_sentry_storm_grenade_condition_met"])

    def test_pve_duration_not_transferred_to_pvp(self):
        self.assertEqual(self.screen()["pve_conduction_tines_duration_seconds_official_historical"], 10)
        self.assertEqual(self.screen()["pve_previous_duration_seconds_official"], 7)
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = self.screen(activity=mode)
                self.assertIsNone(r["pve_conduction_tines_duration_seconds_official_historical"])
                self.assertIsNone(r["pvp_conduction_tines_duration_seconds"])
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_guardian_ttk"])
                self.assertIs(r["artifact_enabled"], False if mode != "pvp" else None)

    def test_no_other_class_inherits_crown_activation_or_duration(self):
        for cls in ("hunter", "titan"):
            with self.subTest(cls=cls):
                r = self.screen(class_name=cls)
                self.assertEqual(r["status"], "class_not_supported_by_exotic")
                self.assertIsNone(r["pve_conduction_tines_duration_seconds_official_historical"])

    def test_weapon_kills_and_grenade_hits_are_not_auto_attributed(self):
        for event in ("weapon_kill", "grenade_damage"):
            with self.subTest(event=event):
                r = self.screen(event=event)
                self.assertEqual(r["status"], "event_not_supported_by_official_rule")
                self.assertFalse(r["official_ionic_sentry_storm_grenade_condition_met"])

    def test_patch_day_and_pre_patch_are_not_current_certifications(self):
        self.assertEqual(self.screen(observation_date="2026-06-08")["status"],
                         "pre_patch_requires_historical_revalidation")
        self.assertEqual(self.screen(observation_date="2026-06-09")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertIsNone(self.screen(observation_date="2026-06-09")
                          ["pve_conduction_tines_duration_seconds_official_historical"])
        self.assertEqual(self.screen(source_patch_version="9.7.0.1")["status"],
                         "source_patch_mismatch")

    def test_invalid_inputs_fail_closed(self):
        cases = (
            {"observation_date": "2026-6-10"},
            {"observation_date": "2026-02-30"},
            {"observation_date": 20260610},
            {"activity": "gambit"},
            {"class_name": "druid"},
            {"event": "all_kills"},
            {"tines_stacks": True},
            {"tines_stacks": -1},
            {"tines_stacks": 1.0},
            {"source_patch_version": ""},
        )
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    self.screen(**case)


if __name__ == "__main__":
    unittest.main()
