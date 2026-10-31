"""Synthetic regression tests for official 9.7.0 relative weapon damage deltas."""
import unittest

from simulator.pve_970_weapon_deltas import historical_pve_delta, SOURCE_URL


def evaluate(family, target, activity="pve", version="9.7.0"):
    return historical_pve_delta(family, target, activity=activity,
                                source_patch_version=version)


class Pve970WeaponDeltaTests(unittest.TestCase):
    def test_rocket_pulse_boss_stacks_separate_patch_changes(self):
        result = evaluate("rocket_pulse", "boss")
        self.assertAlmostEqual(result["multiplier"], 0.675)
        self.assertEqual([x["factor"] for x in result["components"]], [0.9, 0.75])
        self.assertEqual(result["status"], "historical_patch_delta_only")

    def test_rocket_pulse_elite_only_generic_change(self):
        self.assertAlmostEqual(evaluate("rocket_pulse", "elite")["multiplier"], 0.9)

    def test_rocket_pulse_champion_not_mislabeled_boss(self):
        self.assertAlmostEqual(evaluate("rocket_pulse", "champion")["multiplier"], 0.9)

    def test_rocket_pulse_base_combatant_generic_change(self):
        self.assertAlmostEqual(evaluate("rocket_pulse", "base_combatant")["multiplier"], 0.9)

    def test_rocket_launcher_boss_bonus(self):
        self.assertAlmostEqual(evaluate("rocket_launcher", "boss")["multiplier"], 1.05)

    def test_rocket_launcher_champion_bonus(self):
        self.assertAlmostEqual(evaluate("rocket_launcher", "champion")["multiplier"], 1.05)

    def test_rocket_launcher_elite_not_boss(self):
        self.assertEqual(evaluate("rocket_launcher", "elite")["multiplier"], 1.0)

    def test_heavy_grenade_launcher_boss_bonus(self):
        self.assertAlmostEqual(evaluate("heavy_grenade_launcher", "boss")["multiplier"], 1.05)

    def test_heavy_grenade_launcher_champion_bonus(self):
        self.assertAlmostEqual(evaluate("heavy_grenade_launcher", "champion")["multiplier"], 1.05)

    def test_heavy_grenade_launcher_base_no_listed_change(self):
        self.assertEqual(evaluate("heavy_grenade_launcher", "base_combatant")["multiplier"], 1.0)

    def test_pvp_does_not_inherit_pve_patch_values(self):
        result = evaluate("rocket_pulse", "boss", activity="pvp")
        self.assertIsNone(result["multiplier"])
        self.assertEqual(result["status"], "pvp_not_applicable")

    def test_mismatched_version_rejects_numeric_output(self):
        result = evaluate("rocket_pulse", "boss", version="9.7.0.6")
        self.assertIsNone(result["multiplier"])
        self.assertEqual(result["status"], "source_patch_version_mismatch")

    def test_unknown_family_fail_closed(self):
        result = evaluate("sniper", "boss")
        self.assertIsNone(result["multiplier"])
        self.assertEqual(result["status"], "unsupported_weapon_family")

    def test_unknown_target_rejected(self):
        with self.assertRaises(ValueError):
            evaluate("rocket_pulse", "guardian")

    def test_invalid_activity_rejected(self):
        with self.assertRaises(ValueError):
            evaluate("rocket_pulse", "boss", activity="strikes")

    def test_blank_version_rejected(self):
        with self.assertRaises(ValueError):
            evaluate("rocket_pulse", "boss", version="")

    def test_source_and_no_measurement_claim(self):
        result = evaluate("rocket_pulse", "boss")
        self.assertEqual(result["source_url"], SOURCE_URL)
        self.assertFalse(result["gameplay_measured"])
        self.assertFalse(result["current_game_verified"])
        self.assertIsNone(result["boss_dps"])
        self.assertIsNone(result["absolute_damage"])


if __name__ == "__main__":
    unittest.main()
