import unittest
from scripts.diff_definitions import compare_snapshots

class TestDefinitionDiff(unittest.TestCase):
    def test_add_remove_modify(self):
        old = [{"hash": 1, "name": "A"}, {"hash": 2, "name": "B"}]
        new = [{"hash": 1, "name": "Changed"}, {"hash": 3, "name": "C"}]
        result = compare_snapshots(old, new)
        self.assertEqual(result["added_hashes"], ["3"])
        self.assertEqual(result["removed_hashes"], ["2"])
        self.assertEqual(result["modified_hashes"], ["1"])

    def test_reordered_records_are_unchanged(self):
        rows = [{"hash": 1, "name": "A"}, {"hash": 2, "name": "B"}]
        self.assertEqual(compare_snapshots(rows, list(reversed(rows)))["modified"], 0)
