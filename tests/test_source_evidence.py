import unittest
from simulator.source_evidence import validate_evidence_record, sourced_phase_status

class SourceEvidenceTests(unittest.TestCase):
    def test_missing_source(self):
        self.assertFalse(validate_evidence_record('damage', {'status': 'verified', 'kind': 'measurement'}))

    def test_simulation_not_measurement(self):
        self.assertFalse(validate_evidence_record('damage', {'status': 'verified', 'kind': 'simulation', 'source_url': 'https://bungie.net'}))

    def test_manifest_cannot_certify_active_frame(self):
        record = {"status": "verified", "kind": "manifest", "source_url": "https://bungie.net"}
        self.assertFalse(validate_evidence_record("active_frame", record))

    def test_unsupported_calibration_kind(self):
        record = {"status": "verified", "kind": "official", "source_url": "https://bungie.net"}
        self.assertFalse(validate_evidence_record("calibration", record))

    def test_measurement_requires_protocol(self):
        record = {"status": "verified", "kind": "measurement", "source_url": "https://example.org"}
        self.assertFalse(validate_evidence_record("ttk", record))

    def test_measurement_with_protocol_is_structurally_valid(self):
        record = {"status": "verified", "kind": "measurement",
                  "source_url": "https://example.org/study",
                  "method": "controlled repeat captures", "sample_size": 3,
                  "game_version": "9.7.0.6", "activity": "private match",
                  "measured_on": "2026-10-29"}
        self.assertTrue(validate_evidence_record("ttk", record))

    def test_partial_phase(self):
        self.assertFalse(sourced_phase_status(1, {})['complete'])

if __name__ == '__main__':
    unittest.main()
