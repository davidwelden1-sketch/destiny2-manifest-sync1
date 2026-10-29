import unittest
from simulator.activity import ActivityContext, Metric, filter_metrics

class TestActivityEvidence(unittest.TestCase):
    def test_pve_pvp_cannot_mix(self):
        pve = ActivityContext("pve", "boss", "test", True)
        pvp = ActivityContext("pvp", "6v6", "test", False)
        rows = [
            Metric("damage", 100, "damage", pve, "https://example.org/pve", "hypothetical"),
            Metric("damage", 30, "damage", pvp, "https://example.org/pvp", "hypothetical"),
        ]
        self.assertEqual([m.value for m in filter_metrics(rows, pvp)], [30])
        self.assertEqual([m.value for m in filter_metrics(rows, pve)], [100])

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):
            ActivityContext("pvp", "grandmaster", "test")

    def test_artifact_status_part_of_context(self):
        enabled = ActivityContext("pvp", "6v6", "test", True)
        disabled = ActivityContext("pvp", "6v6", "test", False)
        self.assertNotEqual(enabled, disabled)

    def test_artifact_disabled_in_current_competitive_and_trials(self):
        for mode in ("competitive", "trials"):
            for version in ("9.7.0", "9.7.0.6", "10.0.0", "unknown"):
                with self.subTest(mode=mode, version=version):
                    with self.assertRaises(ValueError):
                        ActivityContext("pvp", mode, version, True)
                    self.assertFalse(ActivityContext("pvp", mode, version, False).artifact_enabled)

    def test_historical_artifact_state_and_noncompetitive_modes(self):
        self.assertTrue(ActivityContext("pvp", "trials", "9.6.0", True).artifact_enabled)
        self.assertTrue(ActivityContext("pvp", "6v6", "9.7.0.6", True).artifact_enabled)
        self.assertIsNone(ActivityContext("pvp", "competitive", "9.7.0.6").artifact_enabled)

if __name__ == "__main__":
    unittest.main()
