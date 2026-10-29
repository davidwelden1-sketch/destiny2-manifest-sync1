import unittest
from simulator.activity import ActivityContext
from simulator.measurements import SandboxMeasurement
from simulator.research_gaps import missing_research

class TestResearchGaps(unittest.TestCase):
    def test_hypothetical_does_not_close_gap(self):
        context = ActivityContext("pvp", "6v6", "test", False)
        row = SandboxMeasurement(123, "precision_damage", 80, "damage", context,
                                 "https://example.org", "2026-10-29",
                                 "hypothetical", "synthetic test")
        gaps = missing_research([row], "pvp", "6v6", "test", False)
        self.assertIn("precision_damage", [x["metric"] for x in gaps])

    def test_measured_closes_metric_gap(self):
        context = ActivityContext("pve", "boss", "test", True)
        row = SandboxMeasurement(123, "boss_dps", 100, "damage/s", context,
                                 "https://example.org", "2026-10-29",
                                 "measured", "synthetic test")
        gaps = missing_research([row], "pve", "boss", "test", True)
        self.assertNotIn("boss_dps", [x["metric"] for x in gaps])
