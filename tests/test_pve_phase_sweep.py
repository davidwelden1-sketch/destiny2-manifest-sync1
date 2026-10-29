import unittest
from simulator.pve_phase_sweep import run_pve_sweep

class PvePhaseSweepTests(unittest.TestCase):
    def test_default_grid(self):
        report = run_pve_sweep()
        self.assertEqual(report["scenario_count"], 24)
        self.assertTrue(all(not r["verified_in_game"] for r in report["scenarios"]))

    def test_phase_math(self):
        row = run_pve_sweep(base_dps=(100,), phase_seconds=(10,),
            damage_multiplier=(1.5,), ability_cycle=(20,), ability_duration=10)["scenarios"][0]
        self.assertEqual(row["phase_damage_if_multiplier_always_active"], 1500)
        self.assertEqual(row["phase_damage_if_multiplier_only_during_ability"], 1250)

    def test_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            run_pve_sweep(base_dps=(float("nan"),))
        with self.assertRaises(ValueError):
            run_pve_sweep(ability_duration=0)

if __name__ == "__main__":
    unittest.main()
