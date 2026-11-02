"""Source-gate two historical Bungie 9.7.0 weapon mechanics; no gameplay measurements."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "exotic_weapon_970_pve_pvp_20261102.json"
GUIDES = ROOT / "data" / "player_discoveries.json"


class ExoticWeapon970EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(DATA.read_text())
        cls.guides = json.loads(GUIDES.read_text())

    def test_source_and_version_are_explicit(self):
        source = self.index["source"]
        self.assertEqual(source["publisher"], "Bungie")
        self.assertEqual(source["patch_version"], "9.7.0")
        self.assertEqual(source["published_at"], "2026-06-09")
        self.assertEqual(source["url"], "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0")

    def test_distinct_pve_pvp_guides_and_no_synthetic_measurements(self):
        records = self.index["records"]
        self.assertEqual(len(records), 2)
        self.assertEqual(len({r["id"] for r in records}), 2)
        guide_ids = {g["id"] for g in self.guides["records"]}
        for r in records:
            self.assertIn(r["player_guide_id"], guide_ids)
            self.assertFalse(r["certified_for_app_build_recommendation"])
            self.assertFalse(r["current_artifact_verified"])
            self.assertIsNone(r["pve_boss_dps_measured"])
            self.assertIsNone(r["pvp_guardian_ttk_measured"])
        self.assertIn("PvE", records[0]["activity"])
        self.assertIn("PvP", records[1]["activity"])

    def test_hierarchy_scortch_is_not_direct_damage(self):
        r = self.index["records"][0]
        self.assertEqual(r["weapon"], "Hierarchy of Needs")
        self.assertEqual(r["published_mechanic"]["seekers_apply_scorch_published_notation"], "+15 (+5)")
        self.assertTrue(r["published_mechanic"]["seeker_hidden_tracking_to_precision_damaged_targets"])
        self.assertNotIn("guardian_damage", r["published_mechanic"])

    def test_mida_radar_duration_remains_unknown(self):
        r = self.index["records"][1]
        self.assertEqual(r["weapon"], "MIDA Multi-Tool")
        self.assertTrue(r["published_mechanic"]["catalyst_activation_requires_weapon_in_hand"])
        self.assertTrue(r["published_mechanic"]["catalyst_improved_radar_resolution_persists_after_stow"])
        self.assertIsNone(r["published_mechanic"]["stowed_persistence_duration_seconds"])

    def test_player_guides_are_human_readable_and_source_labelled(self):
        by_id = {g["id"]: g for g in self.guides["records"]}
        for r in self.index["records"]:
            g = by_id[r["player_guide_id"]]
            self.assertEqual(g["source_published_at"], "2026-06-09")
            self.assertEqual(g["evidence"], "official_historical")
            self.assertIs(g["runtime_verified"], False)
            self.assertGreaterEqual(len(g["player"]["steps"]), 3)
            self.assertIn("not", g["player"]["watch_out"].lower())


if __name__ == "__main__":
    unittest.main()
