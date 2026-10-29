import unittest
from simulator.ability_timing import cooldown_seconds, uptime_fraction

class AbilityTimingTests(unittest.TestCase):
    def test_regeneration(self):
        self.assertEqual(cooldown_seconds(60, 2)["seconds"], 30)
        self.assertFalse(cooldown_seconds(60, 2)["measured_in_game"])

    def test_uptime_capped(self):
        self.assertEqual(uptime_fraction(15, 10)["fraction"], 1.0)

    def test_invalid_rate(self):
        with self.assertRaises(ValueError):
            cooldown_seconds(60, 0)

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            uptime_fraction(float("nan"), 20)

if __name__ == "__main__":
    unittest.main()
