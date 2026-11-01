"""Synthetic tests for official June 2026 ability cap and PvP start rules."""
import unittest

from simulator.patch_970_ability_cooldown_evidence import (
    audit_match_start_charges, audit_ability_stat_cooldown_caps,
)


class MatchStartChargeTests(unittest.TestCase):
    def check(self, **overrides):
        args = dict(observation_date="2026-06-10", activity="pvp",
                    class_name="hunter", multi_charge_ability=True,
                    match_start=True)
        args.update(overrides)
        return audit_match_start_charges(**args)

    def test_one_initial_charge_for_all_classes_in_pvp(self):
        for cls in ("hunter", "titan", "warlock"):
            with self.subTest(cls=cls):
                r = self.check(class_name=cls)
                self.assertEqual(r["status"], "official_pvp_multi_charge_match_start_rule")
                self.assertEqual(r["starting_charges_official"], 1)
                self.assertIsNone(r["maximum_ability_charges"])
                self.assertIsNone(r["ability_cooldown_seconds"])

    def test_competitive_and_trials_exclude_artifact(self):
        for mode in ("competitive", "trials"):
            with self.subTest(mode=mode):
                r = self.check(activity=mode)
                self.assertEqual(r["starting_charges_official"], 1)
                self.assertIs(r["artifact_enabled"], False)

    def test_pve_cannot_inherit_pvp_start_rule(self):
        r = self.check(activity="pve")
        self.assertEqual(r["status"], "pvp_only_rule_not_applicable_to_pve")
        self.assertIsNone(r["starting_charges_official"])

    def test_single_charge_and_mid_match_not_inferred(self):
        self.assertEqual(self.check(multi_charge_ability=False)["status"],
                         "not_a_multi_charge_ability")
        self.assertEqual(self.check(match_start=False)["status"],
                         "mid_match_charges_not_established")

    def test_freshness_and_invalid_input(self):
        for changes, status in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.1"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(changes=changes):
                r = self.check(**changes)
                self.assertEqual(r["status"], status)
                self.assertIsNone(r["starting_charges_official"])
        for changes in (
            {"multi_charge_ability": 1}, {"match_start": None},
            {"class_name": "bard"}, {"activity": "gambit"},
            {"observation_date": "2026-02-30"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.check(**changes)


class AbilityStatCapTests(unittest.TestCase):
    def check(self, **overrides):
        args = dict(observation_date="2026-06-10", activity="pve",
                    class_name="warlock")
        args.update(overrides)
        return audit_ability_stat_cooldown_caps(**args)

    def test_passive_approximate_and_active_exact_are_distinct(self):
        r = self.check()
        self.assertEqual(r["status"], "official_general_cooldown_stat_cap_changes_only")
        self.assertEqual(r["passive_maximum_bonus_relative_reduction_approx_percent"], 20)
        self.assertEqual(r["previous_active_maximum_bonus_percent"], 190)
        self.assertEqual(r["post_patch_active_maximum_bonus_percent"], 125)
        self.assertIsNone(r["ability_cooldown_seconds"])
        self.assertIsNone(r["ability_regeneration_uptime"])
        self.assertFalse(r["gameplay_measured"])

    def test_general_rule_across_modes_without_transferring_dps_or_ttk(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = self.check(activity=mode)
                self.assertEqual(r["post_patch_active_maximum_bonus_percent"], 125)
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_guardian_ttk"])

    def test_freshness_mismatch_has_no_current_cap(self):
        for changes in (
            {"observation_date": "2026-06-08"},
            {"observation_date": "2026-06-09"},
            {"source_patch_version": "9.7.0.2"},
        ):
            with self.subTest(changes=changes):
                r = self.check(**changes)
                self.assertIsNone(r["post_patch_active_maximum_bonus_percent"])
                self.assertIsNone(r["passive_maximum_bonus_relative_reduction_approx_percent"])

    def test_invalid_input(self):
        for changes in (
            {"class_name": None}, {"activity": "gambit"},
            {"observation_date": "2026-6-10"}, {"observation_date": 20260610},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.check(**changes)


if __name__ == "__main__":
    unittest.main()
