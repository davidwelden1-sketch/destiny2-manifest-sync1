import unittest

from simulator.frost_armor_evidence import frost_armor_endpoint, shatter_champion_stun


class FrostArmorEvidenceTests(unittest.TestCase):
    def test_five_stack_pve_endpoint_is_approximate(self):
        row = frost_armor_endpoint(stacks=5, whisper_of_rime=False, mode="pve")
        self.assertEqual(row["approximate_dr"], 0.35)
        self.assertEqual(row["evidence_grade"], "official_patch_approximate_endpoint")

    def test_rime_seven_stack_cap_and_endpoint(self):
        row = frost_armor_endpoint(stacks=7, whisper_of_rime=True, mode="pve")
        self.assertEqual((row["max_stacks"], row["approximate_dr"]), (7, 0.50))

    def test_intermediate_stack_does_not_invent_curve(self):
        row = frost_armor_endpoint(stacks=4, whisper_of_rime=True, mode="pve")
        self.assertIsNone(row["approximate_dr"])
        self.assertEqual(row["decay_model"], "one_stack_at_a_time")

    def test_pvp_numbers_remain_unmeasured(self):
        row = frost_armor_endpoint(stacks=5, whisper_of_rime=False, mode="pvp")
        self.assertIsNone(row["approximate_dr"])
        self.assertEqual(row["evidence_grade"], "unmeasured")

    def test_stacks_over_cap_fail(self):
        for rime, count in ((False, 6), (True, 8)):
            with self.subTest(rime=rime), self.assertRaises(ValueError):
                frost_armor_endpoint(stacks=count, whisper_of_rime=rime, mode="pve")

    def test_shatter_stuns_unstoppable_not_overload(self):
        row = shatter_champion_stun()
        self.assertEqual(row["stuns"], "unstoppable")
        self.assertEqual(row["not_stunned_by_shatter"], "overload")


if __name__ == "__main__":
    unittest.main()
