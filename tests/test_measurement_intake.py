import json
import unittest
from scripts.validate_measurements import validate_lines

class TestMeasurementIntake(unittest.TestCase):
    def test_valid_and_invalid_rows(self):
        valid = {"item_hash": 123, "metric": "precision_damage", "value": 80,
                 "unit": "damage", "context": {"activity": "pvp", "mode": "6v6",
                 "sandbox_version": "test", "artifact_enabled": False},
                 "source_url": "https://example.org", "observed_at": "2026-10-29",
                 "evidence_status": "hypothetical", "conditions": "synthetic test"}
        result = validate_lines([json.dumps(valid), '{"broken": true}'])
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["pvp"], 1)
        self.assertEqual(len(result["errors"]), 1)
