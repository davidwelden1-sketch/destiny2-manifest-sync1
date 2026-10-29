import unittest
from simulator.survivability import effective_resistance, effective_health

class SurvivabilityFiniteInputTests(unittest.TestCase):
    def test_nan_resistance_rejected(self):
        with self.assertRaises(ValueError):
            effective_resistance([float("nan")])

    def test_infinite_resistance_rejected(self):
        with self.assertRaises(ValueError):
            effective_resistance([float("inf")])

    def test_nan_health_rejected(self):
        with self.assertRaises(ValueError):
            effective_health(float("nan"))

    def test_infinite_shields_rejected(self):
        with self.assertRaises(ValueError):
            effective_health(100, float("inf"))

if __name__ == "__main__":
    unittest.main()
