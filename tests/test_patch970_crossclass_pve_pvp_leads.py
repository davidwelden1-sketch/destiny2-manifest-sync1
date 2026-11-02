"""Guard official component deltas against accidental gameplay certification."""
import json
from pathlib import Path
import unittest


DATA = json.loads(
    (Path(__file__).resolve().parents[1] /
     "data/patch970_crossclass_pve_pvp_leads_20261102.json").read_text(encoding="utf-8")
)


class CrossclassPatch970IndexTests(unittest.TestCase):
    def test_stable_ids_and_official_provenance(self):
        self.assertEqual(DATA["schema_version"], "1.0.0")
        ids = [row["id"] for row in DATA["records"]]
        self.assertEqual(len(ids), len(set(ids)))
        for row in DATA["records"]:
            self.assertTrue(row["id"].startswith("d2:patch-rule:970:"))
            self.assertEqual(row["patch_version"], "9.7.0")
            self.assertEqual(row["patch_published_on"], "2026-06-09")
            self.assertEqual(row["source_url"],
                             "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0")

    def test_no_gameplay_values_or_certified_builds(self):
        for row in DATA["records"]:
            self.assertFalse(row["certified_for_app_build_recommendation"])
            self.assertFalse(row["exact_hash_legality_verified"])
            self.assertFalse(row["current_artifact_verified"])
            self.assertFalse(row["mode_applicability_measured"])
            for key in ("pve_boss_dps_measured", "pve_dr_measured",
                        "pvp_guardian_damage_measured", "pvp_ttk_measured"):
                self.assertIsNone(row[key])

    def test_component_scope_and_activity_separation(self):
        records = {row["id"]: row for row in DATA["records"]}
        crossbow = records["d2:patch-rule:970:hunter:mobius-quiver-crossbow-buff-cap"]
        self.assertEqual(crossbow["published_change"]["max_buff_relative_to_prepatch"], 0.5)
        self.assertIsNone(crossbow["published_change"]["postpatch_max_buff"])
        knife = records["d2:patch-rule:970:hunter:proximity-knife-detonation"]
        self.assertEqual(knife["published_change"]["detonation_damage_after"], 100)
        storm = records["d2:patch-rule:970:titan:storm-grenade-tracking-duration"]
        self.assertEqual(storm["published_change"]["max_tracking_speed_vs_combatants_relative"], 1.38)
        self.assertIn("Guardian", storm["pvp_research"])


if __name__ == "__main__":
    unittest.main()
