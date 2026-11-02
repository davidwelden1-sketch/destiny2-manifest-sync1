"""Synthetic source-integrity tests for Bungie 9.7.0 rocket-pulse and Adagio changes."""
import unittest
from simulator.patch_970_weapon_family_damage import rocket_pulse_patch, adagio_patch

class Patch970WeaponFamilyTests(unittest.TestCase):
    def test_rocket_pulse_boss_combines_two_nerfs_multiplicatively(self):
        r=rocket_pulse_patch(activity="pve",target="boss",observation_date="2026-11-02")
        self.assertEqual(r["historical_relative_damage_multiplier"],"0.675")
        self.assertTrue(r["combined_boss_adjustment_is_arithmetic"])
        self.assertIsNone(r["measured_boss_dps"])
    def test_rocket_pulse_base_elite_champion_not_assumed_boss(self):
        for target in ("base","elite","champion"):
            with self.subTest(target=target):
                r=rocket_pulse_patch(activity="pve",target=target,observation_date="2026-11-02")
                self.assertEqual(r["historical_relative_damage_multiplier"],"0.90")
        self.assertFalse(rocket_pulse_patch(activity="pve",target="elite",observation_date="2026-11-02")["historical_general_special_elite_bonus_applies"])
    def test_no_pve_multiplier_transferred_to_pvp(self):
        for activity in ("pvp","competitive","trials"):
            with self.subTest(activity=activity):
                r=rocket_pulse_patch(activity=activity,target="guardian",observation_date="2026-11-02")
                self.assertIsNone(r["historical_relative_damage_multiplier"])
                self.assertIsNone(r["measured_guardian_ttk"])
    def test_adagio_family_specific_bonus(self):
        for family,bonus in (("hand_cannon",27),("shotgun",30),("bow",30),("other",None)):
            for activity in ("pve","pvp"):
                with self.subTest(family=family,activity=activity):
                    r=adagio_patch(activity=activity,weapon_family=family,observation_date="2026-11-02")
                    self.assertEqual(r["published_damage_bonus_percent"],bonus)
                    self.assertIsNone(r["measured_guardian_ttk"])
                    self.assertFalse(r["current_weapon_perk_pool_verified"])
    def test_patch_day_and_before_are_unknown(self):
        for day in ("2026-06-08","2026-06-09"):
            self.assertIsNone(rocket_pulse_patch(activity="pve",target="boss",observation_date=day)["historical_relative_damage_multiplier"])
            self.assertIsNone(adagio_patch(activity="pvp",weapon_family="hand_cannon",observation_date=day)["published_damage_bonus_percent"])
    def test_rejects_invalid_activity_date_target_family(self):
        for bad in (dict(activity="gambit"),dict(target="unknown"),dict(observation_date="2026-6-9")):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                rocket_pulse_patch(**{**dict(activity="pve",target="boss",observation_date="2026-11-02"),**bad})
        for bad in (dict(activity="crucible"),dict(weapon_family="fusion"),dict(observation_date="invalid")):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                adagio_patch(**{**dict(activity="pvp",weapon_family="bow",observation_date="2026-11-02"),**bad})
    def test_fail_closed_on_non_string_flags(self):
        for bad in (dict(activity=1),dict(target=None),dict(observation_date=None)):
            with self.assertRaises(ValueError):
                rocket_pulse_patch(**{**dict(activity="pve",target="boss",observation_date="2026-11-02"),**bad})
        with self.assertRaises(ValueError):
            adagio_patch(activity="pvp",weapon_family=None,observation_date="2026-11-02")
    def test_artifact_trials_and_uncertainty(self):
        r=adagio_patch(activity="trials",weapon_family="hand_cannon",observation_date="2026-11-02")
        self.assertFalse(r["artifact_effects_enabled"])
        self.assertFalse(r["certified_for_app_build_recommendation"])
        self.assertFalse(r["rpm_change_verified"])
        self.assertFalse(rocket_pulse_patch(activity="pve",target="boss",observation_date="2026-11-02")["runtime_damage_verified"])

if __name__ == "__main__":
    unittest.main()
