"""Source-provenance and activity isolation checks; no gameplay certification."""
import json
import unittest
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "super_970_activity_split_20261102.json"


class SuperActivitySplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.records = {r["id"]: r for r in cls.dataset["records"]}

    def test_stable_ids_and_uniqueness(self):
        self.assertEqual(len(self.records), 2)
        self.assertEqual(len(self.dataset["records"]), 2)
        self.assertTrue(all(k.startswith("d2:patch-rule:970:") for k in self.records))

    def test_official_patch_provenance_and_dates(self):
        for record in self.records.values():
            self.assertEqual(record["patch_version"], "9.7.0")
            self.assertEqual(record["patch_published_on"], "2026-06-09")
            self.assertIn("bungie.net", record["source_url"])
            self.assertEqual(record["confidence_grade"], "official_historical_patch_not_live_measured")

    def test_pve_nova_lance_has_no_invented_timing_or_damage(self):
        r = self.records["d2:patch-rule:970:warlock:skull-dire-ahamkara-nova-lance"]
        self.assertEqual(r["guardian_class"], "warlock")
        self.assertTrue(r["official_behavior"]["grants_short_nova_lance_window"])
        self.assertIsNone(r["official_behavior"]["window_duration_seconds"])
        self.assertIsNone(r["measured_pve_dps"])

    def test_pvp_deadshot_gain_component_not_weapon_damage(self):
        r = self.records["d2:patch-rule:970:hunter:deadshot-player-kill-super-energy"]
        self.assertEqual(r["activity"], "pvp")
        self.assertEqual(r["official_behavior"]["super_energy_gain_from_player_kills_relative_multiplier"], 0.6)
        self.assertEqual(r["official_behavior"]["super_energy_gain_reduction_fraction"], 0.4)
        self.assertIsNone(r["measured_pvp_ttk"])

    def test_no_gameplay_certification_leaks(self):
        for r in self.records.values():
            self.assertFalse(r["current_runtime_verified"])
            self.assertFalse(r["current_artifact_allocation_verified"])
            self.assertFalse(r["certified_for_app_build_recommendation"])
            self.assertIsNone(r["measured_pvp_guardian_damage"])
            self.assertIsNone(r["measured_ability_cooldown_seconds"])


if __name__ == "__main__":
    unittest.main()
