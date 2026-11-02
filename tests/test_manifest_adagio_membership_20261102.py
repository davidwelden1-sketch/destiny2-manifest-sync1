"""Conservative regression guards for manifest-derived Adagio membership evidence."""
import json
import unittest
from pathlib import Path

DATA=Path(__file__).resolve().parents[1]/"data"/"manifest_adagio_membership_20261102.json"

class ManifestAdagioMembershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(DATA.read_text(encoding="utf-8"))
    def test_manifest_version_and_source_provenance(self):
        self.assertEqual(self.data["source"]["manifest_version"],"245114.26.10.13.2000-1-bnet.66137")
        self.assertIn("/actions/runs/41469891959",self.data["source"]["source_artifact"])
        self.assertEqual(self.data["evidence"],"manifest_structural")
    def test_count_is_definitions_not_unique_obtainable_weapons(self):
        summary=self.data["summary"]
        self.assertEqual(summary["weapon_definitions_scanned"],2208)
        self.assertEqual(summary["definitions_with_named_adagio_in_randomized_plug_set"],100)
        self.assertFalse(summary["all_100_memberships_currently_obtainable"])
    def test_sample_exact_hashes_and_socket(self):
        records=self.data["sample_memberships"]
        self.assertEqual(len(records),10)
        self.assertEqual(len({r["weapon_hash"] for r in records}),10)
        for r in records:
            with self.subTest(hash=r["weapon_hash"]):
                self.assertEqual(r["socket_index"],4)
                self.assertGreater(r["plug_set_hash"],0)
                self.assertTrue(set(r["named_adagio_plug_hashes"]) <= {3673922083,2889515627})
                self.assertFalse(r["exact_current_acquisition_verified"])
                self.assertFalse(r["enhanced_perk_eligibility_verified"])
    def test_duplicate_names_not_collapsed(self):
        records=self.data["sample_memberships"]
        self.assertEqual(len([r for r in records if r["weapon_name"]=="Vulpecula"]),2)
        self.assertEqual(len([r for r in records if r["weapon_name"]=="Crimil's Dagger"]),2)
    def test_no_measured_damage_or_playable_certification(self):
        self.assertFalse(self.data["gameplay_measured"])
        self.assertIn("not 100 unique obtainable",self.data["limitations"])

if __name__=="__main__":
    unittest.main()
