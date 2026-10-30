"""Synthetic source-rule tests; these are not gameplay measurements."""
import unittest
from simulator.jade_rabbit_stack_rules import project_jade_rabbit_events as project


class JadeRabbitStackRuleTests(unittest.TestCase):
    def test_precision_final_blows_add_stacks(self):
        r = project(["precision_final_blow"] * 3)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (3, 3))

    def test_precision_stack_cap_is_fifteen(self):
        r = project(["precision_final_blow"] * 20)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (15, 15))

    def test_body_shot_subtracts_one_and_never_negative(self):
        r = project(["direct_body_hit"] * 3, initial_stacks=2)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (0, 0))

    def test_firefly_splash_does_not_remove_stack(self):
        r = project(["firefly_splash_damage"] * 5, initial_stacks=7)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (7, 7))

    def test_normal_reload_retention_is_not_invented(self):
        r = project(["normal_reload"], initial_stacks=9)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (0, 9))

    def test_reload_uncertainty_propagates_through_precision_and_body(self):
        r = project(["normal_reload", "precision_final_blow",
                     "direct_body_hit"], initial_stacks=5)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (0, 5))

    def test_positive_special_reload_consumes_stacks_and_one_round(self):
        r = project(["special_reload"], initial_stacks=10)
        self.assertEqual((r["stacks_min"], r["stacks_max"]), (0, 0))
        self.assertEqual(r["events"][0]["micro_missile"],
                         "one_round_official_rule_damage_unmeasured")

    def test_uncertain_stack_special_reload_keeps_missile_uncertain(self):
        r = project(["normal_reload", "special_reload"], initial_stacks=8)
        self.assertEqual(r["events"][-1]["micro_missile"],
                         "one_round_possible_stack_uncertain")

    def test_zero_stack_special_reload_not_assumed_to_activate(self):
        r = project(["special_reload"])
        self.assertEqual(r["events"][0]["micro_missile"],
                         "zero_stack_activation_unverified")

    def test_reject_invalid_events_and_non_sequences(self):
        for bad in (None, "precision_final_blow", ["grenade_kill"], [True]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                project(bad)

    def test_reject_invalid_initial_stacks(self):
        for bad in (-1, 16, True, 3.5, "5"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                project([], initial_stacks=bad)

    def test_no_damage_or_ttk_fabricated(self):
        r = project(["precision_final_blow", "special_reload"])
        self.assertIsNone(r["micro_missile_damage"])
        self.assertIsNone(r["pve_dps"])
        self.assertIsNone(r["pvp_ttk"])
        self.assertEqual(r["current_artifact_selection"], "unverified")


if __name__ == "__main__":
    unittest.main()
