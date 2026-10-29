import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_candidates import audit

class TestCandidateAudit(unittest.TestCase):
    def test_clean_candidate_index(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "validation_report.json").write_text(json.dumps({"manifest_version": "test-version"}))
            (root / "item_socket_candidates.json").write_text(json.dumps([
                {"item_hash": 123, "roll_legality": "unverified",
                 "sockets": [{"candidate_plug_hashes": [11, 12]}]}
            ]))
            result = audit(root)
            self.assertEqual(result["errors"], [])
            self.assertTrue((root / "candidate_audit.json").exists())

    def test_rejects_false_legality_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "validation_report.json").write_text(json.dumps({"manifest_version": "test-version"}))
            (root / "item_socket_candidates.json").write_text(json.dumps([
                {"item_hash": 123, "roll_legality": "verified", "sockets": []}
            ]))
            self.assertIn("Unexpected legality certification", audit(root)["errors"])
