import unittest
from simulator.raw_evidence import validate_observation

class EvidenceTests(unittest.TestCase):
    def test_empty_rejected(self):
        self.assertIn("missing_raw_events", validate_observation({}))
    def test_simulation_rejected(self):
        self.assertIn("simulated_data_not_measurement", validate_observation({"source_kind":"simulation","is_simulated":True}))
    def test_no_unreviewed_certification(self):
        self.assertIn("independent_review_required", validate_observation({"validation_state":"verified_current"}))
    def test_boolean_not_numeric(self):
        self.assertIn("invalid_raw_event", validate_observation({"raw_events":[{"value":True}],"sample_count":1}))
