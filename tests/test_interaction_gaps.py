import unittest
from simulator.activity import ActivityContext
from simulator.interactions import Interaction
from simulator.interaction_gaps import interaction_research_queue

class TestInteractionGaps(unittest.TestCase):
    def test_missing_rules_and_evidence_are_prioritized(self):
        context = ActivityContext("pve", "boss", "test", True)
        row = Interaction("example", 1, 2, context, "unknown", "unknown",
                          "hypothetical", "https://example.org")
        queue = interaction_research_queue([row])
        self.assertEqual(len(queue[0]["missing"]), 3)
        self.assertIn("stacking_rule", queue[0]["missing"])
