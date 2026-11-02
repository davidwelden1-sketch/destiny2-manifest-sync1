"""Regression tests for sourced historical rules, not gameplay measurements."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("collective_action_970", ROOT / "simulator" / "collective_action_970.py")
rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rules)


class CollectiveAction970Tests(unittest.TestCase):
    def test_pve_base(self):
        self.assertEqual(rules.collective_action("pve", False, "firesprite")["damage_bonus"], 0.30)

    def test_pve_enhanced(self):
        self.assertEqual(rules.collective_action("pve", True, "void_breach")["damage_bonus"], 0.33)

    def test_pvp_base(self):
        self.assertEqual(rules.collective_action("pvp", False, "ionic_trace")["damage_bonus"], 0.10)

    def test_pvp_enhanced(self):
        self.assertEqual(rules.collective_action("pvp", True, "stasis_shard")["damage_bonus"], 0.11)

    def test_pickup_durations(self):
        self.assertEqual(rules.collective_action("pve", False, "void_breach")["initial_duration_seconds"], 8)
        self.assertEqual(rules.collective_action("pve", False, "tangle_throw")["initial_duration_seconds"], 4)

    def test_maximum_duration(self):
        self.assertEqual(rules.collective_action("pve", False, "tangle_detonation")["maximum_duration_seconds"], 16)

    def test_reject_unknown_activity(self):
        with self.assertRaises(ValueError):
            rules.collective_action("gambit", False, "firesprite")

    def test_reject_non_boolean_enhancement(self):
        with self.assertRaises(ValueError):
            rules.collective_action("pvp", "yes", "firesprite")

    def test_reject_unknown_pickup(self):
        with self.assertRaises(ValueError):
            rules.collective_action("pvp", False, "artifact_orb")

    def test_no_fabricated_measurements(self):
        result = rules.collective_action("pvp", False, "firesprite")
        self.assertIsNone(result["guardian_ttk_measured"])
        self.assertIsNone(result["boss_dps_measured"])
        self.assertFalse(result["runtime_verified"])

    def test_corruption_categories_coexist_not_double_potent(self):
        result = rules.corruption_categories()
        self.assertTrue(result["can_coexist"])
        self.assertFalse(result["potent_stacks_with_itself"])
        self.assertIn("Thorn", result["corruption_sources"])
        self.assertIn("Necrotic Grip", result["potent_corruption_sources"])
        self.assertIsNone(result["tick_damage_measured"])

    def test_guides_retain_unique_ids_and_source(self):
        data = json.loads((ROOT / "data" / "player_discoveries.json").read_text(encoding="utf-8"))
        ids = [r["id"] for r in data["records"]]
        self.assertEqual(len(ids), len(set(ids)))
        for key in ("player:collective-action-pve-pvp-970", "player:corruption-potent-corruption-970", "player:focused-fury-970"):
            entry = next(r for r in data["records"] if r["id"] == key)
            self.assertEqual(entry["player"]["version"], 1)
            self.assertEqual(entry["evidence"], "official_historical")
            self.assertEqual(entry["source_published_at"], "2026-06-09")
            self.assertFalse(entry["runtime_verified"])


if __name__ == "__main__":
    unittest.main()
