import unittest
from simulator.forge_damage_resistance import combined_dr, damage_taken, gifted_conviction_reported

class DamageResistanceTests(unittest.TestCase):
    def test_reported_gifted_pve(self):
        self.assertEqual([gifted_conviction_reported(n) for n in range(4)], [0, .25, .40, .50])
    def test_reported_gifted_pvp(self):
        self.assertEqual([gifted_conviction_reported(n, "pvp") for n in range(4)], [0, .05, .075, .10])
    def test_multiplicative_independent(self):
        self.assertAlmostEqual(combined_dr(.5, .3), .65)
        self.assertAlmostEqual(combined_dr(.4, .3), .58)
        self.assertAlmostEqual(combined_dr(.25, .3), .475)
    def test_effective_damage(self):
        self.assertAlmostEqual(damage_taken(100, .5, .3), 35)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            combined_dr(1.1)
        with self.assertRaises(ValueError):
            gifted_conviction_reported(4)
if __name__ == "__main__":
    unittest.main()
