"""Regression tests: a successful manifest sync may still have missing families."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_definition_families import audit


class TestDefinitionFamilyCoverage(unittest.TestCase):
    def make_catalog(self, root, expected, available=("A",), unavailable=()):
        families = {}
        for family in available:
            filename = f"definitions_{family}.json"
            (root / filename).write_text(json.dumps([
                {"hash": 1, "name": "Sample", "raw_definition": {"hash": 1}}
            ]))
            families[family] = {"file": filename, "count": 1}
        (root / "definition_catalog.json").write_text(json.dumps({
            "manifest_version": "fixture", "expected_families": list(expected),
            "families": families, "unavailable_families": list(unavailable),
        }))

    def test_partial_manifest_paths_are_explicit_not_successful_completeness(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_catalog(root, ["A", "B"], unavailable=["B"])
            report = audit(root)
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["coverage_state"], "partial")
            self.assertFalse(report["coverage_complete"])
            self.assertEqual(report["expected_families"], 2)
            self.assertEqual(report["unavailable_families"], ["B"])

    def test_all_requested_families_present(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_catalog(root, ["A", "B"], available=("A", "B"))
            self.assertEqual(audit(root)["coverage_state"], "complete")

    def test_unaccounted_expected_family_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_catalog(root, ["A", "B"])
            self.assertEqual(audit(root)["coverage_state"], "invalid")

    def test_overlap_of_available_and_missing_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_catalog(root, ["A"], unavailable=["A"])
            self.assertEqual(audit(root)["coverage_state"], "invalid")

    def test_empty_catalog_is_not_complete(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_catalog(root, ["A"], available=(), unavailable=["A"])
            self.assertEqual(audit(root)["coverage_state"], "invalid")

    def test_invalid_hash_is_error_even_if_sorted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_catalog(root, ["A"])
            (root / "definitions_A.json").write_text(json.dumps([{"hash": True}]))
            self.assertEqual(audit(root)["coverage_state"], "invalid")


if __name__ == "__main__":
    unittest.main()
