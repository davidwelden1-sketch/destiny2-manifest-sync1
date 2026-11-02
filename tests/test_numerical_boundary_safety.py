"""Regression gates for numerical PvP TTK and PvE DR boundary safety.

The values are synthetic examples, NOT measured Destiny damage, health or DR.
"""
import unittest
from math import inf, nan

from simulator.ttk import (
    WeaponProfile, minimum_precision_hits, optimal_ttk, shots_to_kill, ttk_seconds,
)
from simulator.forge_damage_resistance import (
    combined_dr, damage_taken, gifted_conviction_reported,
)


class PvpExactBoundaryTests(unittest.TestCase):
    def test_near_two_tap_false_positive_is_rejected(self):
        # Previous epsilon arithmetic incorrectly returned 2.
        self.assertEqual(shots_to_kill(230, 114.9999999997), 3)
        self.assertEqual(shots_to_kill(230, 115), 2)

    def test_near_three_tap_false_positive_is_rejected(self):
        self.assertEqual(shots_to_kill(240, 79.9999999998), 4)
        self.assertEqual(shots_to_kill(240, 80), 3)

    def test_two_tap_precision_split_never_uses_epsilon(self):
        p = WeaponProfile(140, 114.9999999997, 50)
        self.assertIsNone(minimum_precision_hits(p, 230, 2))
        self.assertEqual(minimum_precision_hits(WeaponProfile(140, 115, 50), 230, 2), 2)

    def test_multiplier_comparison_uses_exact_decimal_factors(self):
        p = WeaponProfile(140, 80, 40)
        self.assertEqual(optimal_ttk(p, 230, 1.4375)["shots"], 2)
        self.assertEqual(optimal_ttk(p, 230, 1.43749999999)["shots"], 3)
        self.assertFalse(optimal_ttk(p, 230, 1.4375)["verified_in_game"])

    def test_exact_precision_body_split(self):
        p = WeaponProfile(120, 80, 40)
        self.assertEqual(minimum_precision_hits(p, 200, 3), 2)
        self.assertIsNone(minimum_precision_hits(p, 240.0000000001, 3))

    def test_ttk_rpm_is_explicit_not_weapon_certification(self):
        for rpm in (120, 140, 180):
            with self.subTest(rpm=rpm):
                r = optimal_ttk(WeaponProfile(rpm, 115, 60), 230)
                self.assertEqual(r["shots"], 2)
                self.assertAlmostEqual(r["ttk_seconds"], 60 / rpm)
                self.assertFalse(r["verified_in_game"])

    def test_boolean_numeric_inputs_rejected(self):
        for f in (
            lambda: shots_to_kill(True, 100),
            lambda: shots_to_kill(100, False),
            lambda: WeaponProfile(True, 80, 40),
            lambda: WeaponProfile(140, 80, 40, True),
            lambda: ttk_seconds(140, True),
            lambda: ttk_seconds(140, 2, True),
            lambda: optimal_ttk(WeaponProfile(140, 80, 40), 230, True),
            lambda: minimum_precision_hits(WeaponProfile(140, 80, 40), 230, True),
        ):
            with self.subTest(function=f), self.assertRaises(ValueError):
                f()

    def test_nonfinite_and_invalid_inputs_rejected(self):
        for bad in (nan, inf, -inf):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    shots_to_kill(230, bad)
                with self.assertRaises(ValueError):
                    minimum_precision_hits(WeaponProfile(140, 80, 40), bad, 3)
                with self.assertRaises(ValueError):
                    ttk_seconds(bad, 2)
        with self.assertRaises(ValueError):
            ttk_seconds(140, 2.5)
        with self.assertRaises(ValueError):
            minimum_precision_hits(WeaponProfile(140, 80, 40), 230, 0)


class PveDamageResistanceInputTests(unittest.TestCase):
    def test_multiplicative_is_model_only(self):
        self.assertAlmostEqual(combined_dr(.4, .3), .58)
        self.assertAlmostEqual(damage_taken(100, .4, .3), 42)

    def test_invalid_resistance_is_rejected(self):
        for bad in (True, False, nan, inf, -inf, -0.01, 1.0, "0.5"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                combined_dr(bad)

    def test_invalid_raw_damage_is_rejected(self):
        for bad in (True, False, nan, inf, -inf, -1, "100"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                damage_taken(bad, .4)
        with self.assertRaises(ValueError):
            damage_taken(100)

    def test_zero_damage_valid_with_finite_dr(self):
        self.assertEqual(damage_taken(0, 0), 0)
        self.assertEqual(combined_dr(0), 0)

    def test_gifted_conviction_stacks_do_not_accept_bool(self):
        for bad in (True, False, 1.0, "1"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                gifted_conviction_reported(bad)
        self.assertEqual(gifted_conviction_reported(3, "pve"), .5)
        self.assertEqual(gifted_conviction_reported(3, "pvp"), .1)


if __name__ == "__main__":
    unittest.main()
