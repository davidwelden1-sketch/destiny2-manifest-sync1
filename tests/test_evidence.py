import unittest
from simulator.evidence import Evidence, DamageObservation

class TestEvidence(unittest.TestCase):
    def test_hypothetical_is_not_certified(self):
        e = Evidence("https://example.org/example", "2026-10-29T00:00:00Z", "hypothetical", "illustrative only")
        d = DamageObservation(12345, 80.0, 40.0, "PvP", e)
        self.assertFalse(d.certified)

    def test_measured_requires_context(self):
        with self.assertRaises(ValueError):
            Evidence("https://example.org", "2026-10-29T00:00:00Z", "measured", "")

    def test_invalid_damage_rejected(self):
        e = Evidence("https://example.org/example", "2026-10-29T00:00:00Z", "estimated", "example")
        with self.assertRaises(ValueError):
            DamageObservation(123, float("nan"), 40, "PvP", e)
