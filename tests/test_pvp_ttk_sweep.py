import unittest
from simulator.pvp_ttk_sweep import run_pvp_sweep

class PvpTtkSweepTests(unittest.TestCase):
    def test_patch_provenance(self):
        report = run_pvp_sweep(health_values=(200,))
        self.assertEqual(report["game_version"], "9.7.0")
        self.assertGreater(report["result_count"], 0)
        self.assertTrue(all(not row["certified_current"] for row in report["results"]))

    def test_invalid_health(self):
        with self.assertRaises(ValueError):
            run_pvp_sweep(health_values=(0,))

    def test_nonfinite_inputs_rejected(self):
        for value in (float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                run_pvp_sweep(health_values=(value,))
            with self.assertRaises(ValueError):
                run_pvp_sweep(rpm=value)

    def test_ttk_consistent_with_shot_count(self):
        report = run_pvp_sweep(health_values=(220,))
        for row in report["results"]:
            self.assertAlmostEqual(row["ttk_seconds"], (row["shots"] - 1) / 10)

if __name__ == "__main__":
    unittest.main()
