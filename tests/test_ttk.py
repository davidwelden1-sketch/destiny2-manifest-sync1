import unittest
from simulator.ttk import WeaponProfile, shots_to_kill, ttk_seconds, optimal_ttk, minimum_precision_hits

class TestTTK(unittest.TestCase):
    def test_first_shot_at_zero(self):
        self.assertEqual(ttk_seconds(140, 1), 0)
        self.assertAlmostEqual(ttk_seconds(140, 3), 120 / 140)
    def test_exact_breakpoint(self):
        self.assertEqual(shots_to_kill(100, 50), 2)
        self.assertEqual(shots_to_kill(100.01, 50), 3)
    def test_precision_split(self):
        p = WeaponProfile(140, 80, 40)
        self.assertEqual(minimum_precision_hits(p, 200, 3), 2)
        self.assertIsNone(minimum_precision_hits(p, 300, 3))
    def test_multiplier(self):
        p = WeaponProfile(140, 80, 40)
        self.assertEqual(optimal_ttk(p, 200, 1.25)["shots"], 2)
        self.assertFalse(optimal_ttk(p, 200)["verified_in_game"])
    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            WeaponProfile(0, 80, 40)
        with self.assertRaises(ValueError):
            shots_to_kill(0, 20)

if __name__ == "__main__":
    unittest.main()
