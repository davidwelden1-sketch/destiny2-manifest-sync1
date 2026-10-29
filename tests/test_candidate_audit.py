import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_candidates import audit


class TestCandidateAudit(unittest.TestCase):
    def _audit(self, candidate):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "validation_report.json").write_text(json.dumps({"manifest_version": "test-version"}))
            (root / "item_socket_candidates.json").write_text(json.dumps([candidate]))
            return audit(root)

    def test_clean_candidate_index(self):
        result = self._audit(
            {"item_hash": 123, "roll_legality": "unverified",
             "sockets": [{"candidate_plug_hashes": [11, 12]}]})
        self.assertEqual(result["errors"], [])

    def test_rejects_false_legality_claim(self):
        result = self._audit({"item_hash": 123, "roll_legality": "verified", "sockets": []})
        self.assertIn("Unexpected legality certification", result["errors"])

    def test_rejects_false_enhanced_claim(self):
        result = self._audit({"item_hash": 123, "roll_legality": "unverified",
                              "enhanced_perk_legality": "verified", "sockets": []})
        self.assertIn("Unexpected enhanced legality certification", result["errors"])

    def test_rejects_provenance_union_mismatch(self):
        result = self._audit(
            {"item_hash": 123, "roll_legality": "unverified",
             "sockets": [{"socket_index": 0, "candidate_plug_hashes": [11, 12],
                          "randomized_candidate_plug_hashes": [11],
                          "reusable_candidate_plug_hashes": [],
                          "initial_candidate_plug_hashes": [],
                          "plugset_references": [{"field": "randomizedPlugSetHash", "hash": 5}]}]})
        self.assertIn("Candidate union disagrees with source-specific plugs", result["errors"])

    def test_accepts_consistent_source_provenance(self):
        result = self._audit(
            {"item_hash": 123, "roll_legality": "unverified",
             "enhanced_perk_legality": "unverified",
             "sockets": [{"socket_index": 0, "candidate_plug_hashes": [11, 12],
                          "randomized_candidate_plug_hashes": [11],
                          "reusable_candidate_plug_hashes": [12],
                          "initial_candidate_plug_hashes": [],
                          "plugset_references": [{"field": "randomizedPlugSetHash", "hash": 5},
                                                 {"field": "reusablePlugSetHash", "hash": 6}]}]})
        self.assertEqual(result["errors"], [])
