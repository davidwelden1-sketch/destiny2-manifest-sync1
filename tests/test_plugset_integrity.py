import unittest
from scripts.audit_plugset_integrity import audit_references


class TestPlugsetIntegrity(unittest.TestCase):
    def test_missing_distinct_from_defined_empty_and_invalid(self):
        items = [{"hash": 100, "itemType": 3, "equippable": True, "socketEntries": [
            {"randomizedPlugSetHash": 10}, {"randomizedPlugSetHash": 11},
            {"reusablePlugSetHash": 12}, {"randomizedPlugSetHash": 13}]}]
        result = audit_references(items, {"10": [20], "11": [], "12": [0]})
        self.assertEqual(result["referenced_plugsets"], 4)
        self.assertEqual(result["missing_reference_count"], 1)
        self.assertEqual(result["defined_empty_reference_count"], 1)
        self.assertEqual(result["invalid_reference_count"], 1)
        self.assertEqual(result["missing_references"][0]["socket_index"], 3)

    def test_ignores_non_weapons_and_non_equippable(self):
        items = [{"hash": 1, "itemType": 2, "equippable": True,
                  "socketEntries": [{"randomizedPlugSetHash": 42}]},
                 {"hash": 2, "itemType": 3, "equippable": False,
                  "socketEntries": [{"randomizedPlugSetHash": 42}]}]
        self.assertEqual(audit_references(items, {})["referenced_plugsets"], 0)

    def test_complete_reference_has_no_warning(self):
        items = [{"hash": 3, "itemType": 3, "equippable": True,
                  "socketEntries": [{"randomizedPlugSetHash": 55}]}]
        r = audit_references(items, {"55": [2, 3]})
        self.assertEqual(r["missing_reference_count"], 0)
        self.assertEqual(r["invalid_reference_count"], 0)

    def test_boolean_plug_hash_rejected(self):
        items = [{"hash": 3, "itemType": 3, "equippable": True,
                  "socketEntries": [{"randomizedPlugSetHash": 55}]}]
        self.assertEqual(audit_references(items, {"55": [True]})["invalid_reference_count"], 1)


if __name__ == "__main__":
    unittest.main()
