import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_definition_families import audit

class TestDefinitionAudit(unittest.TestCase):
    def test_valid_catalog(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "definitions_Test.json").write_text(json.dumps([
                {"hash": 1, "name": "Example", "raw_definition": {}}]))
            (root / "definition_catalog.json").write_text(json.dumps({
                "manifest_version": "test", "unavailable_families": [],
                "families": {"Test": {"file": "definitions_Test.json", "count": 1}}}))
            self.assertEqual(audit(root)["errors"], [])

    def test_missing_file_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "definition_catalog.json").write_text(json.dumps({
                "manifest_version": "test", "unavailable_families": [],
                "families": {"Test": {"file": "missing.json", "count": 1}}}))
            self.assertTrue(audit(root)["errors"])
