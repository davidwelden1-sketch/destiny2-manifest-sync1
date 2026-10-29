import unittest
from simulator.evidence import Evidence, DamageObservation
from simulator.evaluate import evaluate_observation

class TestEvaluation(unittest.TestCase):
    def test_sourced_result_not_automatically_verified(self):
        source = Evidence("https://example.org/test", "2026-10-29T00:00:00Z",
                          "measured", "example test context")
        observation = DamageObservation(1234, 80, 40, "PvP", source)
        result = evaluate_observation(observation, 140, 200)
        self.assertEqual(result["shots"], 3)
        self.assertEqual(result["evidence_status"], "measured")
        self.assertFalse(result["verified_in_game"])
        self.assertEqual(result["weapon_hash"], 1234)
