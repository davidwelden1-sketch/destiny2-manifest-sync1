"""Synthetic boundary tests for Bungie's published Cascade Point hit counts."""
import unittest

from simulator.cascade_point_priming import (
    HITS_BY_SOURCE, screen_cascade_point_priming,
)


class TestCascadePointPriming(unittest.TestCase):
    def test_all_official_source_families_at_boundary(self):
        self.assertEqual(len(HITS_BY_SOURCE), 13)
        for family, minimum in HITS_BY_SOURCE.items():
            with self.subTest(family=family):
                below = screen_cascade_point_priming(family, minimum - 1)
                at = screen_cascade_point_priming(family, minimum)
                self.assertFalse(below["count_threshold_met"])
                self.assertTrue(at["count_threshold_met"])
                self.assertEqual(at["minimum_hits"], minimum)
                self.assertFalse(at["certified_activation"])

    def test_same_weapon_does_not_qualify(self):
        result = screen_cascade_point_priming("Hand Cannon", 100, other_weapon=False)
        self.assertEqual(result["status"], "requires_other_weapon")
        self.assertFalse(result["count_threshold_met"])

    def test_unknown_family_fails_closed(self):
        result = screen_cascade_point_priming("Rocket Pulse", 100)
        self.assertEqual(result["status"], "unknown_source_family")
        self.assertFalse(result["certified_activation"])

    def test_bad_inputs_fail_closed(self):
        for count in (-1, True, 1.5, "6"):
            with self.assertRaises(ValueError):
                screen_cascade_point_priming("Auto Rifle", count)
        with self.assertRaises(TypeError):
            screen_cascade_point_priming(3, 6)
        with self.assertRaises(TypeError):
            screen_cascade_point_priming("Auto Rifle", 6, other_weapon=1)

    def test_normalization_and_no_timing_certification(self):
        result = screen_cascade_point_priming("  GLAIVE   PROJECTILE ", 2)
        self.assertTrue(result["count_threshold_met"])
        self.assertEqual(result["status"], "count_only_not_timing_verified")
        self.assertFalse(result["certified_activation"])


if __name__ == "__main__":
    unittest.main()
