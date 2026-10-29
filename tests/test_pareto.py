import unittest
from simulator.activity import ActivityContext
from simulator.pareto import BuildScore, pareto_frontier

class TestPareto(unittest.TestCase):
    def test_nondominated_builds(self):
        ctx = ActivityContext("pve", "boss", "test", True)
        rows = [
            BuildScore("damage", ctx, 100, 40, 30, "hypothetical"),
            BuildScore("tank", ctx, 60, 90, 60, "hypothetical"),
            BuildScore("dominated", ctx, 40, 30, 20, "hypothetical"),
        ]
        self.assertEqual({x.build_id for x in pareto_frontier(rows)}, {"damage", "tank"})

    def test_different_modes_cannot_be_compared(self):
        pve = ActivityContext("pve", "boss", "test", True)
        pvp = ActivityContext("pvp", "6v6", "test", False)
        rows = [
            BuildScore("a", pve, 100, 50, 30, "hypothetical"),
            BuildScore("b", pvp, 100, 50, 30, "hypothetical"),
        ]
        with self.assertRaises(ValueError):
            pareto_frontier(rows)
