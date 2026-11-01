"""Contract tests for app-ready, source-gated official preview evidence."""
import json
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "data" / "official_exotic_armor_preview_crossclass_2026_11_01.json"


class TestOfficialPreviewCrossclassEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_source_is_dated_and_official_but_not_live_verified(self):
        s = self.dataset["source"]
        self.assertEqual(s["published_on"], "2025-11-19")
        self.assertEqual(s["evidence_type"], "official_pre_release_preview")
        self.assertFalse(s["current_runtime_revalidated"])
        self.assertTrue(s["url"].startswith("https://www.bungie.net/"))

    def test_all_three_classes_have_unique_stable_ids(self):
        rows = self.dataset["records"]
        self.assertEqual({r["class"] for r in rows}, {"Titan", "Warlock", "Hunter"})
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith("d2:exotic-armor:") for i in ids))

    def test_not_certified_as_measured_gameplay(self):
        c = self.dataset["certification"]
        self.assertEqual(c["current_patch_implementation"], "unverified")
        for key in ("measured_pve_dps", "measured_pvp_ttk", "measured_dr"):
            self.assertIs(c[key], False)
        self.assertEqual(c["competitive_and_trials_artifact_effects"],
                         "disabled_per_9_7_0")

    def test_each_hypothesis_has_both_modes_and_blockers(self):
        for row in self.dataset["records"]:
            self.assertTrue(row["pve_hypothesis"])
            self.assertTrue(row["pvp_hypothesis"])
            self.assertGreaterEqual(len(row["measurement_blockers"]), 3)

    def test_titan_three_orb_y_pattern_not_three_damage_multiplier(self):
        row = next(r for r in self.dataset["records"] if r["class"] == "Titan")
        self.assertEqual(row["facts"][0]["count"], 3)
        self.assertEqual(row["facts"][1]["barricade_count"], 3)
        self.assertEqual(row["facts"][1]["pattern"], "Y")
        self.assertNotIn("damage_multiplier", row["facts"][1])

    def test_warlock_ramp_and_time_are_distinct_mechanics(self):
        row = next(r for r in self.dataset["records"] if r["class"] == "Warlock")
        self.assertEqual(row["facts"][0]["new_kills_to_cap"], 4)
        self.assertEqual(row["facts"][1]["max_relative_damage_bonus_percent"], 30)
        self.assertEqual(row["facts"][1]["seconds_to_max"], 10)

    def test_hunter_invisibility_recharge_not_infinite_ability_claim(self):
        row = next(r for r in self.dataset["records"] if r["class"] == "Hunter")
        self.assertEqual(row["facts"][0]["max_stacks"], 3)
        self.assertIn("timer_does_not_deplete", row["facts"][1]["effect"])
        self.assertIn("pve_and_pvp_regen_rates", row["measurement_blockers"])


if __name__ == "__main__":
    unittest.main()
