"""Synthetic, source-gated regression tests; not gameplay measurements."""
import unittest

from simulator.patch_970_ammo_evidence import (
    audit_pit_brick, audit_precision_lfr_brick,
)


class PitBrickEvidenceTests(unittest.TestCase):
    def audit(self, **changes):
        params = dict(observation_date="2026-06-10", activity="pve",
                      enemy_floating_above_pit=True,
                      meter_threshold_reached=True)
        params.update(changes)
        return audit_pit_brick(**params)

    def test_above_pit_filled_meter_defers_not_drops(self):
        result = self.audit()
        self.assertEqual(result["status"], "brick_deferred_until_eligible_kill")
        self.assertIs(result["pit_kill_drops_brick"], False)
        self.assertIsNone(result["number_of_bricks_spawned"])
        self.assertFalse(result["gameplay_measured"])

    def test_above_pit_without_filled_meter_preserves_progress_rule(self):
        result = self.audit(meter_threshold_reached=False)
        self.assertEqual(result["status"], "ammo_meter_progress_not_lost")
        self.assertIs(result["pit_kill_drops_brick"], False)

    def test_next_eligible_kill_can_pay_owed_brick(self):
        result = self.audit(enemy_floating_above_pit=False,
                            meter_threshold_reached=False, owed_brick_before=True)
        self.assertEqual(result["status"], "owed_brick_spawns_on_eligible_kill")
        self.assertTrue(result["owed_brick_spawn_rule_applies"])
        self.assertIsNone(result["number_of_bricks_spawned"])

    def test_simultaneous_owed_and_new_threshold_does_not_invent_two_bricks(self):
        result = self.audit(enemy_floating_above_pit=False, owed_brick_before=True)
        self.assertEqual(result["status"], "simultaneous_owed_and_new_threshold_payout_unresolved")
        self.assertIsNone(result["number_of_bricks_spawned"])

    def test_normal_ground_drop_not_guaranteed_by_pit_rule(self):
        result = self.audit(enemy_floating_above_pit=False)
        self.assertEqual(result["status"], "ordinary_brick_drop_not_certified_by_this_note")

    def test_pvp_and_competitive_not_misrepresented_as_measured(self):
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                result = self.audit(activity=mode)
                self.assertFalse(result["pvp_guardian_drop_behavior_measured"])
                self.assertIsNone(result["pvp_guardian_ttk"])
                self.assertIs(result["artifact_enabled"],
                              False if mode != "pvp" else None)

    def test_patch_freshness_gates(self):
        for changes, expected in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.1"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(changes=changes):
                result = self.audit(**changes)
                self.assertEqual(result["status"], expected)
                self.assertIsNone(result["pit_kill_drops_brick"])

    def test_invalid_input_fails_closed(self):
        for changes in (
            {"enemy_floating_above_pit": 1}, {"meter_threshold_reached": 0},
            {"owed_brick_before": None}, {"observation_date": "2026-02-30"},
            {"observation_date": "2026-6-10"}, {"activity": "gambit"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.audit(**changes)


class PrecisionLfrEvidenceTests(unittest.TestCase):
    def audit(self, **changes):
        params = dict(observation_date="2026-06-10", activity="pve",
                      ammo_class="heavy", brick_type="base")
        params.update(changes)
        return audit_precision_lfr_brick(**params)

    def test_all_four_official_pve_ammo_amount_changes(self):
        expected = {
            ("heavy", "base"): (3, 5),
            ("heavy", "enhanced"): (4, 6),
            ("special", "base"): (3, 5),
            ("special", "enhanced"): (6, 10),
        }
        for (ammo_class, brick_type), (old, new) in expected.items():
            with self.subTest(ammo_class=ammo_class, brick_type=brick_type):
                result = self.audit(ammo_class=ammo_class, brick_type=brick_type)
                self.assertEqual(result["status"], "official_pve_precision_lfr_ammo_per_brick_only")
                self.assertEqual(result["previous_pve_ammo_per_brick"], old)
                self.assertEqual(result["post_patch_pve_ammo_per_brick"], new)
                self.assertFalse(result["exact_weapon_hash_eligibility_verified"])
                self.assertFalse(result["enhanced_perk_eligibility_verified"])

    def test_pvp_does_not_inherit_pve_amounts(self):
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                result = self.audit(activity=mode)
                self.assertEqual(result["status"], "pvp_ammo_amount_not_established")
                self.assertIsNone(result["post_patch_pve_ammo_per_brick"])
                self.assertIsNone(result["previous_pve_ammo_per_brick"])

    def test_pre_patch_and_patch_day_not_certified(self):
        for changes, expected in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.2"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(changes=changes):
                result = self.audit(**changes)
                self.assertEqual(result["status"], expected)
                self.assertIsNone(result["post_patch_pve_ammo_per_brick"])

    def test_invalid_lfr_inputs(self):
        for changes in (
            {"ammo_class": "rocket"}, {"brick_type": "scavenger"},
            {"observation_date": 20260610}, {"activity": "gambit"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.audit(**changes)


if __name__ == "__main__":
    unittest.main()
