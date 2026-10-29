import unittest

from simulator.collective_action import advance_collective_action as step


class TestCollectiveActionPatchModel(unittest.TestCase):
    def test_void_breach_and_firesprite_grant_eight_seconds(self):
        for event in ("void_breach", "firesprite"):
            self.assertEqual(step(0, 0, event)["remaining_seconds"], 8)

    def test_ionic_stasis_and_tangle_detonation_grant_four(self):
        for event in ("ionic_trace", "stasis_shard", "tangle_detonation"):
            self.assertEqual(step(0, 0, event)["remaining_seconds"], 4)

    def test_cap_and_expiry(self):
        self.assertEqual(step(14, 1, "void_breach")["remaining_seconds"], 16)
        self.assertEqual(step(4, 5, None)["remaining_seconds"], 0)
        self.assertFalse(step(4, 5, None)["active"])

    def test_tangle_throw_requires_existing_active_buff(self):
        self.assertEqual(step(0, 0, "tangle_throw_extension")["remaining_seconds"], 0)
        self.assertEqual(step(3, 1, "tangle_throw_extension")["remaining_seconds"], 6)

    def test_pve_pvp_enhanced_damage_distinct_and_unmeasured(self):
        self.assertEqual(step(0, 0, "void_breach", activity="pve")["damage_multiplier_if_active"], 1.30)
        self.assertEqual(step(0, 0, "void_breach", activity="pve", enhanced=True)["damage_multiplier_if_active"], 1.33)
        self.assertEqual(step(0, 0, "void_breach", activity="pvp")["damage_multiplier_if_active"], 1.10)
        self.assertEqual(step(0, 0, "void_breach", activity="pvp", enhanced=True)["damage_multiplier_if_active"], 1.11)
        self.assertFalse(step(0, 0, "void_breach")["measured_in_game"])

    def test_artifact_orb_duration_and_bad_inputs_fail_closed(self):
        for event in ("artifact_orb", "unknown"):
            with self.assertRaises(ValueError):
                step(0, 0, event)
        for remaining, elapsed in ((float("nan"), 0), (0, float("inf")), (-1, 0), (17, 0), (0, -1)):
            with self.assertRaises(ValueError):
                step(remaining, elapsed, "void_breach")


if __name__ == "__main__":
    unittest.main()
