import unittest
from simulator.stronghold import stronghold_infinite_guard_eligibility


class TestStrongholdInfiniteGuard(unittest.TestCase):
    def test_heavy_sword_eligible_not_measured(self):
        row = stronghold_infinite_guard_eligibility(True, 3)
        self.assertTrue(row["eligible"])
        self.assertEqual(row["damage_resistance"], "unverified")
        self.assertEqual(row["active_guard"], "unverified")

    def test_special_sword_not_eligible(self):
        row = stronghold_infinite_guard_eligibility(True, 2)
        self.assertFalse(row["eligible"])
        self.assertEqual(row["reason"], "not_heavy_ammo_sword")

    def test_non_sword_heavy_not_eligible(self):
        self.assertFalse(stronghold_infinite_guard_eligibility(False, 3)["eligible"])

    def test_unknown_ammo_is_not_false_certainty(self):
        self.assertIsNone(stronghold_infinite_guard_eligibility(True, 4)["eligible"])

    def test_invalid_boolean_ammo_rejected(self):
        with self.assertRaises(ValueError):
            stronghold_infinite_guard_eligibility(True, True)

    def test_invalid_sword_flag_rejected(self):
        with self.assertRaises(ValueError):
            stronghold_infinite_guard_eligibility(1, 3)


if __name__ == "__main__":
    unittest.main()
