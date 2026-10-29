import unittest
from simulator.source_evidence import validate_evidence_record, sourced_phase_status

class SourceEvidenceTests(unittest.TestCase):
    def test_missing_source(self):
        self.assertFalse(validate_evidence_record('damage', {'status': 'verified', 'kind': 'measurement'}))

    def test_simulation_not_measurement(self):
        self.assertFalse(validate_evidence_record('damage', {'status': 'verified', 'kind': 'simulation', 'source_url': 'https://bungie.net'}))

    def test_partial_phase(self):
        self.assertFalse(sourced_phase_status(1, {})['complete'])

if __name__ == '__main__':
    unittest.main()
