"""Synthetic scope tests for Bungie's June 23 Xur weapon acquisition note."""
import unittest

from simulator.patch_9702_xur_weapon_acquisition import (
    WEAPONS, CHANNELS, PATCH_DATE, PATCH_VERSION, SOURCE_URL,
    review_xur_weapon_lead,
)


class XurWeaponAcquisitionTests(unittest.TestCase):
    def review(self, weapon="Goldtusk", channel="xur_strange_engram",
               when="2026-07-01", **kwargs):
        return review_xur_weapon_lead(
            weapon_name=weapon, channel=channel, observation_date=when, **kwargs
        )

    def test_all_four_weapons_and_two_channels_are_official_historical_leads(self):
        self.assertEqual(len(WEAPONS), 4)
        self.assertEqual(len(CHANNELS), 2)
        for weapon in WEAPONS:
            for channel in CHANNELS:
                with self.subTest(weapon=weapon, channel=channel):
                    result = self.review(weapon, channel)
                    self.assertEqual(result["status"],
                                     "official_historical_possible_acquisition_channel")
                    self.assertFalse(result["drop_guaranteed"])
                    self.assertFalse(result["current_acquisition_verified"])

    def test_pattern_harmonizer_does_not_prove_enhanced_perk(self):
        result = self.review()
        self.assertEqual(result["deepsight_harmonizer_pattern_unlock"],
                         "officially_supported")
        self.assertEqual(result["weapon_gear_tier"],
                         "un-tiered_in_official_patch")
        self.assertEqual(result["enhanced_perk_legality"], "unverified")
        self.assertIsNone(result["exact_item_hash"])
        self.assertFalse(result["current_manifest_socket_verified"])

    def test_pve_and_pvp_do_not_share_damage_or_ttk_claims(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                result = self.review(activity=activity)
                self.assertIsNone(result["pve_boss_dps"])
                self.assertIsNone(result["pvp_guardian_ttk"])
                self.assertFalse(result["gameplay_measured"])
                self.assertEqual(result["artifact_effects_active"],
                                 False if activity in ("competitive", "trials") else None)

    def test_pre_patch_not_retroactively_certified(self):
        self.assertEqual(self.review(when="2026-06-22")["status"],
                         "pre_patch_acquisition_not_established")

    def test_patch_day_unknown_deployment_time(self):
        self.assertEqual(self.review(when=PATCH_DATE.isoformat())["status"],
                         "patch_day_deployment_time_unknown")

    def test_source_version_mismatch_blocks_inference(self):
        self.assertEqual(self.review(source_patch_version="9.7.0.1")["status"],
                         "source_patch_version_mismatch")

    def test_invalid_weapon_channel_and_activity_fail_closed(self):
        for args in (
            {"weapon": "Unknown"},
            {"weapon": "goldtusk"},
            {"channel": "guaranteed_drop"},
            {"channel": ""},
            {"activity": "gambit"},
            {"activity": None},
            {"source_patch_version": ""},
        ):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    self.review(**args)

    def test_invalid_date_rejected(self):
        for when in ("2026-6-23", "2026-02-30", "today", None, 20260623):
            with self.subTest(when=when):
                with self.assertRaises(ValueError):
                    self.review(when=when)

    def test_official_source_and_class_scope_not_inferred(self):
        self.assertEqual(PATCH_VERSION, "9.7.0.2")
        self.assertIn("bungie.net", SOURCE_URL)
        result = self.review(weapon="Throne-Cleaver")
        self.assertEqual(result["class_eligibility"], "unverified")
        self.assertEqual(result["evidence_grade"],
                         "official_historical_acquisition_family_only")


if __name__ == "__main__":
    unittest.main()
