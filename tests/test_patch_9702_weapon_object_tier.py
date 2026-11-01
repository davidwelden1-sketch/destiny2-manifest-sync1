"""Synthetic provenance and scope tests for 9.7.0.2 weapon corrections."""
import unittest
from simulator.patch_9702_weapon_object_tier import review_weapon_interaction


def review(**kw):
    opts = dict(event="turncoat_object_damage", activity="pve",
                observation_date="2026-11-01")
    opts.update(kw)
    return review_weapon_interaction(**opts)


class Patch9702WeaponObjectTierTests(unittest.TestCase):
    def test_turncoat_empowered_object_damage_not_kill_attribution(self):
        r = review()
        self.assertEqual(r["weapon"], "Turncoat")
        self.assertEqual(r["class_interaction_lead"], "Hunter")
        self.assertIn("Gunpowder Gamble", r["official_correction"])
        self.assertIsNone(r["gunpowder_gamble_detonation_attribution"])
        self.assertIsNone(r["object_damage_ownership"])

    def test_cynosure_higher_tier_extra_traits_not_exact_roll(self):
        r = review(event="cynosure_higher_tier_extra_traits")
        self.assertEqual(r["weapon"], "Cynosure")
        self.assertIsNone(r["exact_extra_trait_threshold"])
        self.assertIsNone(r["obtainable_socket_pair"])
        self.assertEqual(r["enhanced_perk_legality"], "unverified")

    def test_pve_and_pvp_do_not_share_damage_values(self):
        for event in ("turncoat_object_damage", "cynosure_higher_tier_extra_traits"):
            for activity in ("pve", "pvp", "competitive", "trials"):
                with self.subTest(event=event, activity=activity):
                    r = review(event=event, activity=activity)
                    self.assertIsNone(r["pve_boss_dps"])
                    self.assertIsNone(r["pvp_guardian_ttk"])
                    self.assertFalse(r["gameplay_measured"])

    def test_competitive_and_trials_artifact_disabled(self):
        for mode in ("competitive", "trials"):
            self.assertIs(review(activity=mode)["artifact_effects_enabled"], False)
        self.assertIsNone(review(activity="pvp")["artifact_effects_enabled"])

    def test_historical_patch_boundaries(self):
        self.assertEqual(review(observation_date="2026-06-22")["status"],
                         "historical_observation_requires_post_patch_revalidation")
        self.assertEqual(review(observation_date="2026-06-23")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(review(observation_date="2026-06-24")["status"],
                         "official_historical_fix_not_current_measurement")
        self.assertEqual(review(source_patch_version="9.7.0.3")["status"],
                         "source_patch_version_mismatch")

    def test_no_current_manifest_or_drop_claims(self):
        for event in ("turncoat_object_damage", "cynosure_higher_tier_extra_traits"):
            r = review(event=event)
            self.assertIsNone(r["exact_weapon_hash"])
            self.assertIsNone(r["manifest_version"])
            self.assertEqual(r["current_obtainability"], "unverified")
            self.assertFalse(r["current_artifact_allocation_verified"])

    def test_invalid_events_and_activities_fail_closed(self):
        for kw in ({"event": "not real"}, {"event": True}, {"activity": "gambit"},
                   {"activity": []}, {"source_patch_version": None},
                   {"source_patch_version": ""}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                review(**kw)

    def test_invalid_dates_fail_closed(self):
        for invalid in (None, "2026-6-24", "2026-02-30", "2026-11-01T00:00Z"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                review(observation_date=invalid)


if __name__ == "__main__":
    unittest.main()
