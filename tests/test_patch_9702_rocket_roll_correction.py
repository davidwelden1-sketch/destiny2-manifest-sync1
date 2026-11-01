"""Synthetic tests for 9.7.0.2 historical rocket roll correction triage."""
import unittest

from simulator.patch_9702_rocket_roll_correction import review_rocket_roll_correction


def review(**changes):
    params = dict(origin="europa", perk="Lead from Gold",
                  observation_date="2026-06-24", activity="pve")
    params.update(changes)
    return review_rocket_roll_correction(**params)


class RocketRollCorrectionTests(unittest.TestCase):
    def test_europa_historical_unintended_drop(self):
        r = review()
        self.assertEqual(r["status"], "official_historical_unintended_drop_corrected")
        self.assertEqual(r["official_intended_replacement"], "Impromptu Ammunition")
        self.assertEqual(r["lead_from_gold_reserved_for"], "Special ammo weapons")

    def test_moon_historical_unintended_drop(self):
        r = review(origin="moon")
        self.assertEqual(r["status"], "official_historical_unintended_drop_corrected")

    def test_replacement_is_named_not_exact_roll_certified(self):
        r = review(perk="Impromptu Ammunition")
        self.assertEqual(r["status"], "official_historical_replacement_named")
        self.assertIsNone(r["exact_item_hash"])
        self.assertIsNone(r["affected_socket_index"])
        self.assertFalse(r["current_manifest_socket_verified"])
        self.assertEqual(r["enhanced_perk_legality"], "unverified")

    def test_patch_day_not_assumed_deployed(self):
        r = review(observation_date="2026-06-23")
        self.assertEqual(r["status"], "patch_day_deployment_time_unknown")

    def test_earlier_observations_preserved_not_overwritten(self):
        r = review(observation_date="2026-06-22")
        self.assertEqual(r["status"], "pre_patch_roll_observation_requires_versioned_review")

    def test_source_patch_mismatch_blocks_patch_inference(self):
        r = review(source_patch_version="9.7.0.3")
        self.assertEqual(r["status"], "source_patch_version_mismatch")

    def test_never_certifies_acquisition_or_current_manifest(self):
        for origin in ("europa", "moon"):
            for perk in ("Lead from Gold", "Impromptu Ammunition"):
                with self.subTest(origin=origin, perk=perk):
                    r = review(origin=origin, perk=perk)
                    self.assertIsNone(r["current_manifest_version"])
                    self.assertEqual(r["current_obtainability"], "unverified")
                    self.assertFalse(r["current_drop_observed"])

    def test_no_gameplay_numbers_in_pve_or_pvp(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                r = review(activity=activity)
                self.assertFalse(r["gameplay_measured"])
                self.assertIsNone(r["boss_dps"])
                self.assertIsNone(r["guardian_ttk"])

    def test_artifact_disabled_in_competitive_and_trials(self):
        for activity in ("competitive", "trials"):
            self.assertIs(review(activity=activity)["artifact_effects_enabled"], False)
        self.assertIsNone(review(activity="pvp")["artifact_effects_enabled"])

    def test_invalid_family_perk_and_activity_fail_closed(self):
        for kw in ({"origin": "cosmodrome"}, {"origin": True},
                   {"perk": "Collective Action"}, {"perk": True},
                   {"activity": "gambit"}, {"activity": []}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                review(**kw)

    def test_invalid_date_and_version_fail_closed(self):
        for kw in ({"observation_date": "2026-02-30"},
                   {"observation_date": "2026-6-24"},
                   {"observation_date": None},
                   {"source_patch_version": ""},
                   {"source_patch_version": None}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                review(**kw)


if __name__ == "__main__":
    unittest.main()
