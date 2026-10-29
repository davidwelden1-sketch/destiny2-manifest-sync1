import unittest
from scripts.build_socket_candidates import build_index

class TestSocketCandidates(unittest.TestCase):
    def test_deduplicates_and_keeps_provenance(self):
        items = [{"hash": 100, "name": "Example", "equippable": True,
                  "itemType": 3, "itemSubType": 6,
                  "socketEntries": [{"randomizedPlugSetHash": 10,
                                     "reusablePlugSetHash": 11}]}]
        plugsets = {"10": [20, 30], "11": [30, 40]}
        result = build_index(items, plugsets)
        self.assertEqual(result[0]["sockets"][0]["candidate_plug_hashes"], [20, 30, 40])
        self.assertEqual(result[0]["roll_legality"], "unverified")
        self.assertEqual(len(result[0]["sockets"][0]["plugset_references"]), 2)

    def test_non_equippable_excluded(self):
        items = [{"hash": 101, "name": "Example", "equippable": False,
                  "socketEntries": [{"randomizedPlugSetHash": 10}]}]
        self.assertEqual(build_index(items, {"10": [20]}), [])
