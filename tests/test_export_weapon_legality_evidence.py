import copy
import unittest

from scripts.export_weapon_legality_evidence import export_weapon_evidence


def metadata():
    source = {"url": "https://www.bungie.net/common/destiny2_content/json/en/test.json",
              "sha256": "a" * 64, "count": 1}
    return {"manifest_version": "test-manifest",
            "retrieved_at_utc": "2026-11-01T21:00:00+00:00",
            "sources": {"DestinyInventoryItemDefinition": dict(source),
                        "DestinyPlugSetDefinition": dict(source)}}


def weapon(item_hash=100, name="Variant"):
    return {"item_hash": item_hash, "name": name, "item_type": 3, "item_subtype": 6,
            "sockets": [
                {"socket_index": 3,
                 "randomized_candidate_plug_hashes": [11, 12, 13],
                 "currently_rollable_randomized_candidate_plug_hashes": [11],
                 "noncurrent_randomized_candidate_plug_hashes": [12],
                 "unknown_current_roll_randomized_candidate_plug_hashes": [13],
                 "plugset_references": [{"field": "randomizedPlugSetHash", "hash": 90}]},
                {"socket_index": 4,
                 "randomized_candidate_plug_hashes": [],
                 "currently_rollable_randomized_candidate_plug_hashes": [],
                 "noncurrent_randomized_candidate_plug_hashes": [],
                 "unknown_current_roll_randomized_candidate_plug_hashes": [],
                 "plugset_references": [{"field": "singleInitialItemHash", "hash": 55}]},
            ]}


class TestWeaponLegalityEvidenceExport(unittest.TestCase):
    def test_exact_hash_ids_and_version_provenance(self):
        result = export_weapon_evidence([weapon(101), weapon(100)], metadata())
        self.assertEqual([w["id"] for w in result["weapons"]],
                         ["d2:weapon:100", "d2:weapon:101"])
        self.assertEqual(result["weapon_count"], 2)
        self.assertEqual(result["manifest_version"], "test-manifest")
        self.assertEqual(result["provenance"]["evidence_grade"],
                         "official_manifest_structural_only")
        self.assertEqual(result["weapons"][0]["sockets"][0]["randomized_plug_set_hash"], 90)

    def test_roll_state_does_not_certify_acquisition_or_enhancement(self):
        result = export_weapon_evidence([weapon()], metadata())
        w = result["weapons"][0]
        self.assertEqual(w["current_acquisition"], "unverified")
        self.assertEqual(w["enhanced_perk_legality"], "unverified")
        self.assertIsNone(w["pve_damage_measurement"])
        self.assertIsNone(w["pvp_damage_measurement"])
        self.assertFalse(w["sockets"][0]["trait_role_certified"])
        self.assertEqual(w["sockets"][0]["explicit_current_flag_plug_hashes"], [11])
        self.assertEqual(w["sockets"][0]["unknown_current_flag_plug_hashes"], [13])

    def test_same_name_different_hashes_never_merge(self):
        a, b = weapon(100), weapon(101)
        b["sockets"][0]["randomized_candidate_plug_hashes"] = [77]
        b["sockets"][0]["currently_rollable_randomized_candidate_plug_hashes"] = [77]
        b["sockets"][0]["noncurrent_randomized_candidate_plug_hashes"] = []
        b["sockets"][0]["unknown_current_roll_randomized_candidate_plug_hashes"] = []
        records = export_weapon_evidence([a, b], metadata())["weapons"]
        self.assertEqual(records[0]["sockets"][0]["randomized_plug_hashes"], [11, 12, 13])
        self.assertEqual(records[1]["sockets"][0]["randomized_plug_hashes"], [77])

    def test_duplicate_weapon_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicated exact weapon"):
            export_weapon_evidence([weapon(), weapon()], metadata())

    def test_duplicate_or_boolean_socket_index_rejected(self):
        row = weapon()
        row["sockets"][1]["socket_index"] = 3
        with self.assertRaisesRegex(ValueError, "duplicate socket"):
            export_weapon_evidence([row], metadata())
        row["sockets"][1]["socket_index"] = True
        with self.assertRaisesRegex(ValueError, "socket index"):
            export_weapon_evidence([row], metadata())

    def test_incomplete_or_conflicting_roll_state_rejected(self):
        row = weapon()
        row["sockets"][0]["unknown_current_roll_randomized_candidate_plug_hashes"] = []
        with self.assertRaisesRegex(ValueError, "partition"):
            export_weapon_evidence([row], metadata())
        row = weapon()
        row["sockets"][0]["noncurrent_randomized_candidate_plug_hashes"] = [11, 12]
        with self.assertRaisesRegex(ValueError, "partition"):
            export_weapon_evidence([row], metadata())

    def test_missing_randomized_source_is_not_certified(self):
        row = weapon()
        row["sockets"][0]["plugset_references"] = []
        with self.assertRaisesRegex(ValueError, "provenance"):
            export_weapon_evidence([row], metadata())

    def test_boolean_or_duplicate_plug_hash_rejected(self):
        row = weapon()
        row["sockets"][0]["randomized_candidate_plug_hashes"] = [True, 12, 13]
        with self.assertRaisesRegex(ValueError, "invalid plug hash"):
            export_weapon_evidence([row], metadata())
        row = weapon()
        row["sockets"][0]["randomized_candidate_plug_hashes"] = [11, 11, 13]
        with self.assertRaisesRegex(ValueError, "duplicate plug"):
            export_weapon_evidence([row], metadata())

    def test_missing_manifest_version_and_utc_rejected(self):
        for change in ({"manifest_version": ""}, {"retrieved_at_utc": "2026-11-01"},
                       {"retrieved_at_utc": "2026-11-01T22:00:00+01:00"}):
            meta = metadata()
            meta.update(change)
            with self.assertRaises(ValueError):
                export_weapon_evidence([weapon()], meta)

    def test_missing_source_digest_rejected(self):
        meta = metadata()
        meta["sources"]["DestinyPlugSetDefinition"]["sha256"] = "not-a-sha"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            export_weapon_evidence([weapon()], meta)

    def test_untrusted_manifest_host_rejected(self):
        meta = metadata()
        meta["sources"]["DestinyInventoryItemDefinition"]["url"] = (
            "https://example.org/pretend-bungie-manifest.json")
        with self.assertRaisesRegex(ValueError, "Untrusted manifest"):
            export_weapon_evidence([weapon()], meta)

    def test_non_weapon_entries_do_not_leak(self):
        armor = weapon(200)
        armor["item_type"] = 2
        result = export_weapon_evidence([armor, weapon()], metadata())
        self.assertEqual(result["weapon_count"], 1)
        self.assertEqual(result["weapons"][0]["item_hash"], 100)

    def test_malformed_sockets_are_not_silently_empty(self):
        row = weapon()
        row.pop("sockets")
        with self.assertRaisesRegex(ValueError, "socket evidence"):
            export_weapon_evidence([row], metadata())


if __name__ == "__main__":
    unittest.main()
