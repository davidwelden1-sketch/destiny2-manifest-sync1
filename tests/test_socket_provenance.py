import unittest
from simulator.socket_provenance import socket_provenance

class SocketProvenanceTests(unittest.TestCase):
    def test_source_flags_and_fake_set(self):
        items = {"123": {"sockets": {"socketEntries": [{
            "plugSources": 12, "randomizedPlugSetHash": 77,
            "singleInitialItemHash": 4
        }]}}}
        result = socket_provenance(123, items, {"77": {"isFakePlugSet": True}})
        entry = result["sockets"][0]
        self.assertEqual(entry["runtime_sources"], ["profile_plug_set", "character_plug_set"])
        self.assertEqual(entry["fake_plug_sets"], ["randomizedPlugSetHash"])
        self.assertFalse(entry["certified_roll"])

    def test_unresolved_reference(self):
        items = {123: {"sockets": {"socketEntries": [{"randomizedPlugSetHash": 99}]}}}
        self.assertEqual(socket_provenance(123, items, {})["sockets"][0]["unresolved_references"],
                         ["randomizedPlugSetHash"])

    def test_exact_hash_not_name(self):
        self.assertEqual(socket_provenance(999, {123: {"sockets": {"socketEntries": []}}}, {})["status"],
                         "item_missing")

    def test_malformed_flags(self):
        items = {123: {"sockets": {"socketEntries": [{"plugSources": True}]}}}
        self.assertEqual(socket_provenance(123, items, {})["status"], "malformed_plug_sources")

if __name__ == "__main__":
    unittest.main()
