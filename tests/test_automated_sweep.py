import unittest
from simulator.automated_sweep import run_sweep

class AutomatedSweepTests(unittest.TestCase):
    def test_default_sweep(self):
        r = run_sweep()
        self.assertEqual(r["scenario_count"], 18)
        self.assertTrue(all(not s["certified_current"] for s in r["scenarios"]))

    def test_zero_frost_equal_hypotheses(self):
        r = run_sweep(incoming_hits=(100, 200), frost_dr=(0,))
        self.assertTrue(all(s["health_damage_difference"] == 0 for s in r["scenarios"]))

    def test_positive_difference_when_frost_helps_shield(self):
        r = run_sweep(incoming_hits=(200,), frost_dr=(.35,))
        self.assertGreater(r["scenarios"][0]["health_damage_difference"], 0)

if __name__ == "__main__":
    unittest.main()
