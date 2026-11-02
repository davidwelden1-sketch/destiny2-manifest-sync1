import unittest
from simulator.patch_970_ability_conditions import (
    ARC_SOUL_MAX_ACQUISITION_M, ARC_SOUL_PREVIOUS_MAX_ACQUISITION_M,
    offensive_bulwark_energy_trigger, arc_soul_acquisition_zone,
)


class Patch970AbilityConditionsTest(unittest.TestCase):
    def test_final_blow_with_overshield_triggers_both(self):
        self.assertEqual(offensive_bulwark_energy_trigger(True, True), ("grenade", "melee"))

    def test_overshield_without_final_blow_does_not_trigger(self):
        self.assertEqual(offensive_bulwark_energy_trigger(True, False), ())

    def test_final_blow_without_overshield_does_not_trigger(self):
        self.assertEqual(offensive_bulwark_energy_trigger(False, True), ())

    def test_neither_condition_does_not_trigger(self):
        self.assertEqual(offensive_bulwark_energy_trigger(False, False), ())

    def test_non_boolean_conditions_rejected(self):
        with self.assertRaises(TypeError):
            offensive_bulwark_energy_trigger(1, True)

    def test_arc_soul_inside_published_range(self):
        self.assertEqual(arc_soul_acquisition_zone("23.99"), "within_published_max")

    def test_arc_soul_exact_boundary_remains_unverified(self):
        self.assertEqual(arc_soul_acquisition_zone(24), "boundary_unverified")

    def test_arc_soul_outside_published_range(self):
        self.assertEqual(arc_soul_acquisition_zone(24.01), "beyond_published_max")

    def test_old_range_is_not_current_range(self):
        self.assertEqual(ARC_SOUL_PREVIOUS_MAX_ACQUISITION_M - ARC_SOUL_MAX_ACQUISITION_M, 6)
        self.assertEqual(arc_soul_acquisition_zone(27), "beyond_published_max")

    def test_invalid_distances_fail_closed(self):
        for bad in (-1, "nan", "Infinity", "unknown", True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                arc_soul_acquisition_zone(bad)


if __name__ == "__main__":
    unittest.main()
