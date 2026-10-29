import unittest
from simulator.activity import ActivityContext
from simulator.measurements import SandboxMeasurement, group_by_activity

class TestMeasurements(unittest.TestCase):
    def test_activity_separation(self):
        pve = ActivityContext("pve", "boss", "test", True)
        pvp = ActivityContext("pvp", "6v6", "test", False)
        def make(ctx):
            return SandboxMeasurement(123, "damage", 100, "points", ctx,
                                      "https://example.org/test", "2026-10-29T00:00:00Z",
                                      "hypothetical", "synthetic test")
        grouped = group_by_activity([make(pve), make(pvp)])
        self.assertEqual(len(grouped["pve"]), 1)
        self.assertEqual(len(grouped["pvp"]), 1)

    def test_missing_conditions_rejected(self):
        ctx = ActivityContext("pve", "boss", "test")
        with self.assertRaises(ValueError):
            SandboxMeasurement(123, "damage", 100, "points", ctx,
                               "https://example.org", "2026-10-29", "measured", "")
