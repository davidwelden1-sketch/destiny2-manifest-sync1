import unittest
from simulator.activity import ActivityContext
from simulator.interactions import Interaction, interaction_candidates, confirmed_interactions

class TestInteractions(unittest.TestCase):
    def test_activity_isolation(self):
        pve = ActivityContext("pve", "boss", "test", True)
        pvp = ActivityContext("pvp", "6v6", "test", False)
        rows = [
            Interaction("example", 1, 2, pve, "on hit", "unknown", "hypothetical",
                        "https://example.org"),
        ]
        self.assertEqual(interaction_candidates(rows, pvp), [])
        self.assertEqual(len(interaction_candidates(rows, pve)), 1)
        self.assertEqual(confirmed_interactions(rows, pve), [])

    def test_requires_explicit_stacking(self):
        pve = ActivityContext("pve", "boss", "test", True)
        row = Interaction("example", 1, 2, pve, "on hit", "unknown",
                          "measured", "https://example.org")
        self.assertEqual(confirmed_interactions([row], pve), [])
