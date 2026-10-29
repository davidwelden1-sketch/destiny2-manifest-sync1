import unittest
from simulator.armor_sets import check_armor_set_budget


class TestArmorSets(unittest.TestCase):
    def test_four_piece_set_plus_exotic_fits(self):
        self.assertTrue(check_armor_set_budget({"Wayward Psyche": 4}, 1)["fits_five_armor_slots"])

    def test_two_two_plus_exotic_fits(self):
        self.assertTrue(check_armor_set_budget({"Smoke Jumper": 2, "Other": 2}, 1)["fits_five_armor_slots"])

    def test_two_plus_four_impossible_even_without_exotic(self):
        self.assertFalse(check_armor_set_budget({"Smoke Jumper": 2, "Wayward Psyche": 4}, 0)["fits_five_armor_slots"])

    def test_invalid_counts_rejected(self):
        for counts in ({"X": -1}, {"X": 1.2}, {"X": True}, {"": 2}):
            with self.assertRaises(ValueError):
                check_armor_set_budget(counts)
        with self.assertRaises(ValueError):
            check_armor_set_budget({}, 2)


if __name__ == "__main__":
    unittest.main()
