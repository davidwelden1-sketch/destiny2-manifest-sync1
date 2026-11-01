"""Synthetic tests for source-gated 9.7.0 Rocket Pulse PvE/PvP boundaries."""
import unittest

from simulator.rocket_pulse_970_evidence import review_rocket_pulse


def review(activity="pve", target="boss", class_name="warlock",
           observation_date="2026-11-01", source_patch_version="9.7.0"):
    return review_rocket_pulse(activity=activity, target=target,
                               class_name=class_name,
                               observation_date=observation_date,
                               source_patch_version=source_patch_version)


class RocketPulse970Tests(unittest.TestCase):
    def test_boss_has_separate_pve_and_boss_changes(self):
        result = review()
        self.assertEqual(result["general_pve_damage_change_percent"], -10)
        self.assertEqual(result["additional_boss_damage_change_percent"], -25)
        self.assertIsNone(result["combined_boss_damage_multiplier_measured"])
        self.assertIsNone(result["measured_pve_dps"])

    def test_elite_does_not_inherit_generic_special_bonus(self):
        result = review(target="elite")
        self.assertEqual(result["general_pve_damage_change_percent"], -10)
        self.assertIsNone(result["additional_boss_damage_change_percent"])
        self.assertIs(result["generic_special_elite_20_percent_bonus_applies"], False)

    def test_champion_is_not_automatically_boss(self):
        result = review(target="champion")
        self.assertEqual(result["general_pve_damage_change_percent"], -10)
        self.assertIsNone(result["additional_boss_damage_change_percent"])

    def test_guardian_damage_not_inferred_from_pve(self):
        result = review(activity="pvp", target="guardian")
        self.assertIsNone(result["general_pve_damage_change_percent"])
        self.assertIsNone(result["additional_boss_damage_change_percent"])
        self.assertIsNone(result["measured_pvp_ttk"])

    def test_artifact_off_in_competitive_and_trials(self):
        for mode in ("competitive", "trials"):
            with self.subTest(mode=mode):
                result = review(activity=mode, target="guardian")
                self.assertIs(result["artifact_effects_enabled"], False)

    def test_normal_pvp_artifact_not_assumed_active(self):
        self.assertIsNone(review(activity="pvp", target="guardian")["artifact_effects_enabled"])

    def test_all_classes_same_weapon_patch_without_build_certification(self):
        for class_name in ("hunter", "titan", "warlock"):
            with self.subTest(class_name=class_name):
                result = review(class_name=class_name)
                self.assertEqual(result["general_pve_damage_change_percent"], -10)
                self.assertFalse(result["current_artifact_allocation_verified"])
                self.assertFalse(result["enhanced_roll_verified"])

    def test_prepatch_and_patch_day_not_current_evidence(self):
        for day in ("2026-06-08", "2026-06-09"):
            with self.subTest(day=day):
                result = review(observation_date=day)
                self.assertIsNone(result["general_pve_damage_change_percent"])
                self.assertIsNone(result["additional_boss_damage_change_percent"])

    def test_version_mismatch_blocks_values(self):
        result = review(source_patch_version="9.6.0")
        self.assertEqual(result["status"], "patch_version_mismatch")
        self.assertIsNone(result["general_pve_damage_change_percent"])

    def test_activity_target_mismatch_rejected(self):
        result = review(activity="pve", target="guardian")
        self.assertEqual(result["status"], "activity_target_mismatch")
        self.assertIsNone(result["general_pve_damage_change_percent"])

    def test_bad_inputs_fail_closed(self):
        overrides = [
            {"activity": "gambit"}, {"target": "unknown"},
            {"class_name": "guardian"}, {"observation_date": "2026-02-30"},
            {"observation_date": "Nov 1 2026"}, {"observation_date": None},
            {"source_patch_version": ""}, {"activity": True},
        ]
        for kwargs in overrides:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                review(**kwargs)


if __name__ == "__main__":
    unittest.main()
