"""Offline integration test: two same-version components, no live Bungie fetch."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from scripts import sync_manifest


class ManifestPlugSetIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"ErrorCode": 1, "Response": {
            "version": "synthetic-v1", "jsonWorldComponentContentPaths": {"en": {
                "DestinyInventoryItemDefinition": "/fixture/items.json",
                "DestinyPlugSetDefinition": "/fixture/plugsets.json"}}}}
        self.items = {"101": {"itemType": 3, "displayProperties": {"name": "Test"},
                              "sockets": {"socketEntries": [
                                  {"randomizedPlugSetHash": 900}]}},
                      "102": {"itemType": 2},
                      "777": {"itemType": 19, "displayProperties": {"name": "Synthetic Trait"}}}
        self.plugsets = {"900": {"reusablePlugItems": [
            {"plugItemHash": 777, "currentlyCanRoll": True},
            {"plugItemHash": 778, "currentlyCanRoll": False}]}}
        self.urls = {
            "https://www.bungie.net/Platform/Destiny2/Manifest/": json.dumps(self.manifest).encode(),
            "https://www.bungie.net/fixture/items.json": json.dumps(self.items).encode(),
            "https://www.bungie.net/fixture/plugsets.json": json.dumps(self.plugsets).encode()}

    def test_writes_resolved_plugs_and_source_checksums(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(sync_manifest, "OUT", pathlib.Path(folder)):
                with patch.object(sync_manifest, "get", side_effect=self.urls.__getitem__) as get:
                    sync_manifest.main()
            self.assertEqual(get.call_count, 3)
            path = pathlib.Path(folder)
            rows = json.loads((path / "weapon_plug_set_refs_index.json").read_text())
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["itemHash"], 101)
            plugs = rows[0]["resolvedPlugSets"][0]["plugs"]
            self.assertEqual([(p["plugItemHash"], p["currentlyCanRoll"]) for p in plugs],
                             [(777, True), (778, False)])
            self.assertFalse(rows[0]["certifiedObtainableRoll"])
            self.assertFalse(rows[0]["certifiedEnhancedPerks"])
            self.assertEqual(plugs[0]["plugName"], "Synthetic Trait")
            self.assertTrue(plugs[0]["plugDefinitionFound"])
            self.assertIsNone(plugs[1]["plugName"])
            self.assertFalse(plugs[1]["plugDefinitionFound"])
            meta = json.loads((path / "manifest_metadata.json").read_text())
            self.assertEqual(meta["manifest_version"], "synthetic-v1")
            self.assertEqual(meta["plug_set_definition_count"], 1)
            self.assertEqual(meta["resolved_weapon_definition_count"], 1)
            self.assertEqual(meta["plug_set_definition_sha256"],
                             hashlib.sha256(self.urls["https://www.bungie.net/fixture/plugsets.json"]).hexdigest())

    def test_missing_plug_set_component_fails_closed(self):
        del self.manifest["Response"]["jsonWorldComponentContentPaths"]["en"]["DestinyPlugSetDefinition"]
        self.urls["https://www.bungie.net/Platform/Destiny2/Manifest/"] = json.dumps(self.manifest).encode()
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(sync_manifest, "OUT", pathlib.Path(folder)):
                with patch.object(sync_manifest, "get", side_effect=self.urls.__getitem__):
                    with self.assertRaises(KeyError):
                        sync_manifest.main()
            self.assertFalse((pathlib.Path(folder) / "weapon_plug_set_refs_index.json").exists())

    def test_malformed_plug_set_component_fails_closed(self):
        self.urls["https://www.bungie.net/fixture/plugsets.json"] = b"[]"
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(sync_manifest, "OUT", pathlib.Path(folder)):
                with patch.object(sync_manifest, "get", side_effect=self.urls.__getitem__):
                    with self.assertRaises(ValueError):
                        sync_manifest.main()
            self.assertFalse((pathlib.Path(folder) / "weapon_plug_set_refs_index.json").exists())


if __name__ == "__main__":
    unittest.main()
