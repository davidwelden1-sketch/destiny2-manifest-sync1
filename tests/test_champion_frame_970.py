"""Synthetic checks for source-gated Champion frame rules (not gameplay tests)."""
import json
import unittest
from pathlib import Path

from simulator.champion_frame_970 import (
    BASE_FRAMES, FRAME_OVERRIDES, review_champion_frame,
)


class ChampionFrame970Tests(unittest.TestCase):
    def test_all_six_generic_frames(self):
        for frame, effect in BASE_FRAMES.items():
            with self.subTest(frame=frame):
                result = review_champion_frame(frame=frame, activity="pve")
                self.assertEqual(result["champion_counter_pve"], effect)
                self.assertEqual(result["rule"], "generic_frame_category")
                self.assertFalse(result["certified_for_live_build"])

    def test_specific_overrides_not_generic_fallback(self):
        for (weapon, frame), effect in FRAME_OVERRIDES.items():
            with self.subTest(weapon=weapon, frame=frame):
                result = review_champion_frame(
                    frame=frame, weapon_type=weapon, activity="pve")
                self.assertEqual(result["champion_counter_pve"], effect)
                self.assertEqual(result["rule"], "specific_frame_override")

    def test_support_ar_overload_not_barrier(self):
        r = review_champion_frame(
            frame="support", weapon_type="auto_rifle", activity="pve")
        self.assertEqual(r["champion_counter_pve"], "overload")

    def test_specific_frame_requires_matching_type(self):
        for weapon, frame in FRAME_OVERRIDES:
            with self.subTest(frame=frame):
                with self.assertRaises(ValueError):
                    review_champion_frame(frame=frame, activity="pve")
                with self.assertRaises(ValueError):
                    review_champion_frame(
                        frame=frame, weapon_type="hand_cannon", activity="pve")

    def test_pvp_no_champion_to_guardian_damage_transfer(self):
        for activity in ("pvp", "competitive", "trials"):
            r = review_champion_frame(
                frame="support", weapon_type="auto_rifle", activity=activity)
            self.assertIsNone(r["champion_counter_pve"])
            self.assertIsNone(r["pvp_ttk_measured"])
            self.assertFalse(r["pvp_guardian_damage_inferred"])

    def test_claimed_hash_and_manifest_not_a_certification(self):
        r = review_champion_frame(
            frame="adaptive", activity="pve", item_hash=123456,
            manifest_frame_verified=True)
        self.assertTrue(r["manifest_frame_verified_claimed"])
        self.assertFalse(r["current_item_hash_legality_certified"])
        self.assertFalse(r["enhanced_perk_eligibility_certified"])

    def test_rejects_invalid_types_and_unknown_rules(self):
        cases = [
            {"frame": "unknown"}, {"frame": "Support"},
            {"frame": ""}, {"frame": None},
            {"frame": "adaptive", "item_hash": True},
            {"frame": "adaptive", "item_hash": -1},
            {"frame": "adaptive", "item_hash": 2**32},
            {"frame": "adaptive", "manifest_frame_verified": 1},
            {"frame": "adaptive", "weapon_type": 123},
            {"frame": "adaptive", "activity": "gambit"},
        ]
        for change in cases:
            with self.subTest(change=change), self.assertRaises(ValueError):
                review_champion_frame(**dict({"frame": "adaptive", "activity": "pve"}, **change))

    def test_publisher_data_matches_software_rules(self):
        p = Path(__file__).resolve().parents[1] / "data" / "patch_970_champion_frames_20261102.json"
        d = json.loads(p.read_text())
        records = d["records"]
        self.assertEqual(len(records), len(BASE_FRAMES) + len(FRAME_OVERRIDES))
        self.assertEqual(len({r["id"] for r in records}), len(records))
        for record in records:
            with self.subTest(id=record["id"]):
                r = review_champion_frame(
                    frame=record["frame"], weapon_type=record["weapon_type"],
                    activity="pve")
                self.assertEqual(r["rule_id"], record["id"])
                self.assertEqual(r["champion_counter_pve"], record["effect"])
                self.assertEqual(record["evidence"], "official_historical")
                self.assertIsNone(record["unknown_measurements"]["pve_dps"])
                self.assertIsNone(record["unknown_measurements"]["pvp_ttk"])


if __name__ == "__main__":
    unittest.main()
