import unittest
from simulator.shield_damage_model import damage_through_layers, stacking_hypotheses

class ShieldDamageModelTests(unittest.TestCase):
    def test_frost_on_shield_absorbs_more_raw_damage(self):
        result = stacking_hypotheses(200)
        self.assertAlmostEqual(result["frost_on_shield"]["health_damage"], 0)
        self.assertAlmostEqual(result["frost_not_on_shield"]["health_damage"], 32.5)
        self.assertTrue(result["stacking_not_verified"])

    def test_without_shield(self):
        r = damage_through_layers(100, frost_dr=.35, overshield_hp=0,
                                  frost_affects_shield=False)
        self.assertAlmostEqual(r["health_damage"], 65)

    def test_shield_breakover(self):
        r = damage_through_layers(300, frost_dr=.35, frost_affects_shield=False)
        self.assertAlmostEqual(r["health_damage"], 97.5)
        self.assertAlmostEqual(r["shield_hp_lost"], 45)

    def test_requires_explicit_hypothesis(self):
        with self.assertRaises(ValueError):
            damage_through_layers(100, frost_dr=.35)

    def test_invalid_resistance(self):
        with self.assertRaises(ValueError):
            damage_through_layers(100, frost_dr=1, frost_affects_shield=True)

if __name__ == "__main__":
    unittest.main()
