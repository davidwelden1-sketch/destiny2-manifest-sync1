"""Synthetic regression coverage for official 9.7.0 named Exotic PvE changes."""
import unittest

from simulator.exotic_target_deltas_970 import (
    EXOTICS, SOURCE_URL, historical_exotic_target_delta,
)


def audit(item_hash, target, activity="pve", version="9.7.0",
          baseline="pre_9_7_0"):
    return historical_exotic_target_delta(
        item_hash=item_hash, target=target, activity=activity,
        source_patch_version=version, reference_baseline=baseline,
    )


SLEEPER = 4036115577
ARBALEST = 2130065553


class ExoticTargetDeltas970Tests(unittest.TestCase):
    def test_exact_weapon_hashes_and_sources(self):
        self.assertEqual(set(EXOTICS), {SLEEPER, ARBALEST})
        for item_hash, item in EXOTICS.items():
            self.assertIn(str(item_hash), item["item_hash_source"])
            self.assertTrue(item["item_hash_source"].startswith("https://www.light.gg/"))

    def test_sleeper_boss_delta(self):
        self.assertAlmostEqual(audit(SLEEPER, "boss")["relative_multiplier"], 1.10)

    def test_sleeper_champion_delta(self):
        self.assertAlmostEqual(audit(SLEEPER, "champion")["relative_multiplier"], 1.10)

    def test_sleeper_elite_has_no_listed_delta(self):
        result = audit(SLEEPER, "elite")
        self.assertEqual(result["status"], "no_listed_target_change")
        self.assertEqual(result["relative_multiplier"], 1.0)

    def test_sleeper_base_combatant_has_no_listed_delta(self):
        self.assertEqual(audit(SLEEPER, "base_combatant")["relative_multiplier"], 1.0)

    def test_arbalest_champion_delta(self):
        self.assertAlmostEqual(audit(ARBALEST, "champion")["relative_multiplier"], 1.33)

    def test_arbalest_boss_not_inherited_from_sleeper(self):
        result = audit(ARBALEST, "boss")
        self.assertEqual(result["relative_multiplier"], 1.0)
        self.assertEqual(result["status"], "no_listed_target_change")

    def test_arbalest_elite_no_listed_delta(self):
        self.assertEqual(audit(ARBALEST, "elite")["relative_multiplier"], 1.0)

    def test_pvp_never_receives_pve_scalar(self):
        for activity in ("pvp", "competitive", "trials"):
            for item_hash in (SLEEPER, ARBALEST):
                with self.subTest(activity=activity, item_hash=item_hash):
                    result = audit(item_hash, "champion", activity=activity)
                    self.assertIsNone(result["relative_multiplier"])
                    self.assertEqual(result["status"], "pvp_not_applicable")

    def test_source_patch_mismatch_fails_closed(self):
        result = audit(SLEEPER, "boss", version="9.7.0.6")
        self.assertIsNone(result["relative_multiplier"])
        self.assertEqual(result["status"], "source_patch_version_mismatch")

    def test_post_patch_baseline_prevents_double_count(self):
        result = audit(SLEEPER, "boss", baseline="post_9_7_0")
        self.assertIsNone(result["relative_multiplier"])
        self.assertEqual(result["status"], "not_a_pre_patch_reference")

    def test_unknown_baseline_does_not_invent_multiplier(self):
        result = audit(ARBALEST, "champion", baseline="unknown")
        self.assertIsNone(result["relative_multiplier"])

    def test_unknown_hash_fails_closed(self):
        result = audit(123456, "champion")
        self.assertEqual(result["status"], "unknown_exact_weapon_hash")
        self.assertIsNone(result["relative_multiplier"])

    def test_reject_bool_zero_and_negative_hash(self):
        for bad in (True, 0, -1, "4036115577"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                audit(bad, "boss")

    def test_reject_invalid_activity_target_baseline(self):
        for kwargs in (
            {"target": "guardian"}, {"target": ""},
            {"activity": "gambit"}, {"baseline": "maybe"},
            {"baseline": ""}, {"version": ""},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                audit(SLEEPER, "boss", **kwargs)

    def test_official_patch_and_hash_evidence_are_separate(self):
        result = audit(ARBALEST, "champion")
        self.assertEqual(result["source_url"], SOURCE_URL)
        self.assertEqual(result["hash_evidence_grade"], "community_manifest_catalog")
        self.assertEqual(result["evidence_grade"], "official_historical_named_exotic_patch")
        self.assertEqual(result["published_on"], "2026-06-09")

    def test_no_measured_damage_or_roll_certification(self):
        result = audit(SLEEPER, "boss")
        self.assertFalse(result["gameplay_measured"])
        self.assertFalse(result["current_game_verified"])
        self.assertFalse(result["current_roll_certified"])
        self.assertFalse(result["artifact_selection_verified"])
        self.assertIsNone(result["absolute_damage"])
        self.assertIsNone(result["boss_dps"])
        self.assertIsNone(result["guardian_ttk"])


if __name__ == "__main__":
    unittest.main()
