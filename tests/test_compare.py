import unittest
from simulator.evidence import Evidence, DamageObservation
from simulator.compare import compare_observations

class TestCompare(unittest.TestCase):
    def test_comparison_orders_by_ttk(self):
        evidence = Evidence("https://example.org", "2026-10-29T00:00:00Z",
                            "hypothetical", "test values only")
        observations = [
            DamageObservation(100, 50, 25, "PvP", evidence),
            DamageObservation(200, 100, 50, "PvP", evidence),
        ]
        rows = compare_observations(observations, {100: 120, 200: 120}, 200)
        self.assertEqual([r["weapon_hash"] for r in rows], [200, 100])
        self.assertTrue(all(not r["verified_in_game"] for r in rows))
