"""Synthetic numerical boundary regressions, not measured Destiny 2 damage."""
import unittest

from simulator.survivability import effective_health, effective_resistance
from simulator.ttk import WeaponProfile, optimal_ttk


class PrecisionAndEHPSafetyTests(unittest.TestCase):
    def test_reject_boolean_resistance(self):
        for bad in (True, False):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                effective_resistance([bad])

    def test_reject_boolean_health(self):
        with self.assertRaises(ValueError):
            effective_health(True)

    def test_reject_boolean_shields(self):
        with self.assertRaises(ValueError):
            effective_health(100, shields=True)

    def test_reject_numerical_total_resistance(self):
        # 200 valid 50% factors lose the surviving fraction at float precision.
        with self.assertRaises(ValueError):
            effective_health(100, resistances=[0.5] * 200)

    def test_reject_nonfinite_effective_health(self):
        with self.assertRaises(ValueError):
            effective_health(1e308, shields=1e308)

    def test_normal_synthetic_ehp_remains_supported(self):
        self.assertAlmostEqual(effective_health(100, 25, [0.2]), 156.25)

    def test_pvp_exact_display_does_not_round_false_two_tap(self):
        result = optimal_ttk(WeaponProfile(140, 114.9999999997, 70), 230, 2)
        self.assertEqual(result["precision_damage_after_multiplier_exact"], "229.9999999994")
        self.assertEqual(result["shots"], 2)
        self.assertTrue(result["shot_breakpoint_uses_exact_decimal_fractions"])
        self.assertFalse(result["verified_in_game"])

    def test_pvp_subthreshold_two_hits_still_need_three(self):
        result = optimal_ttk(WeaponProfile(140, 114.9999999997, 70), 230)
        self.assertEqual(result["shots"], 3)
        self.assertEqual(result["precision_damage_after_multiplier_exact"], "114.9999999997")

    def test_exact_decimal_multiplier(self):
        result = optimal_ttk(WeaponProfile(180, 80.01, 40), 230, 1.25)
        self.assertEqual(result["precision_damage_after_multiplier_exact"], "100.0125")
        self.assertIsNone(result.get("measured_pvp_ttk"))


if __name__ == "__main__":
    unittest.main()
