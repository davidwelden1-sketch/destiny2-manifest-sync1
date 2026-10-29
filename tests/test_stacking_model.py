import unittest
from simulator.stacking_model import calculate_damage

class StackingModelTests(unittest.TestCase):
    def test_exclusive_group(self):
        mods = [{"group":"empower", "multiplier":1.2, "rule":"exclusive_max"},
                {"group":"empower", "multiplier":1.3, "rule":"exclusive_max"}]
        result = calculate_damage(100, mods)
        self.assertAlmostEqual(result["damage"], 130)
        self.assertTrue(result["model_only"])

    def test_independent_groups(self):
        mods = [{"group":"a", "multiplier":1.2, "rule":"exclusive_max"},
                {"group":"b", "multiplier":1.5, "rule":"exclusive_max"}]
        self.assertAlmostEqual(calculate_damage(100, mods)["damage"], 180)

    def test_unknown_rule_rejected(self):
        with self.assertRaises(ValueError):
            calculate_damage(100, [{"group":"a","multiplier":2,"rule":"additive"}])

if __name__ == "__main__":
    unittest.main()
