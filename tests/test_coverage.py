import unittest
from simulator.activity import ActivityContext
from simulator.measurements import SandboxMeasurement
from simulator.coverage import coverage_report

class TestCoverage(unittest.TestCase):
    def test_separates_activity_and_evidence(self):
        def row(activity, mode, status):
            context = ActivityContext(activity, mode, "test", False)
            return SandboxMeasurement(123, "damage", 80, "points", context,
                                      "https://example.org", "2026-10-29",
                                      status, "synthetic test")
        report = coverage_report([
            row("pve", "boss", "measured"),
            row("pvp", "6v6", "hypothetical")])
        self.assertEqual(len(report), 2)
        pve = next(r for r in report if r["activity"] == "pve")
        self.assertEqual(pve["verified_source_records"], 1)
        pvp = next(r for r in report if r["activity"] == "pvp")
        self.assertEqual(pvp["hypothetical_records"], 1)
