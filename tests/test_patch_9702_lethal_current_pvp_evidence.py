"""Synthetic PvP/PvE scope tests for the official Lethal Current fix."""
import unittest

from simulator.patch_9702_lethal_current_pvp_evidence import review_lethal_current


def review(**changes):
    args = dict(activity="pvp", observation_date="2026-06-24")
    args.update(changes)
    return review_lethal_current(**args)


class LethalCurrent9702Tests(unittest.TestCase):
    def test_pvp_historical_multi_proc_fix(self):
        r = review()
        self.assertEqual(r["status"], "official_historical_pvp_multi_activation_bug_fixed")
        self.assertEqual(r["class"], "Hunter")
        self.assertEqual(r["aspect"], "Lethal Current")

    def test_pve_not_inferred_from_pvp_fix(self):
        self.assertEqual(review(activity="pve")["status"],
                         "pve_transfer_not_supported_by_pvp_patch_note")

    def test_competitive_trials_artifact_disabled(self):
        for mode in ("competitive", "trials"):
            r = review(activity=mode)
            self.assertIs(r["artifact_effects_enabled"], False)
            self.assertEqual(r["status"], "official_historical_pvp_multi_activation_bug_fixed")

    def test_normal_pvp_artifact_activation_not_assumed(self):
        self.assertIsNone(review()["artifact_effects_enabled"])

    def test_pre_patch_pvp_one_shots_not_current_calibration(self):
        self.assertEqual(review(observation_date="2026-06-22")["status"],
                         "pre_patch_pvp_multi_proc_observation_requires_revalidation")

    def test_patch_day_and_wrong_source_version(self):
        self.assertEqual(review(observation_date="2026-06-23")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(review(source_patch_version="9.7.0.3")["status"],
                         "source_patch_version_mismatch")

    def test_no_unsupported_ttk_or_damage_claims(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            r = review(activity=mode)
            self.assertIsNone(r["guardian_ttk"])
            self.assertIsNone(r["pve_boss_dps"])
            self.assertIsNone(r["all_one_shots_eliminated"])
            self.assertIsNone(r["damage_ownership"])
            self.assertIsNone(r["activation_count_measured"])
            self.assertFalse(r["gameplay_measured"])

    def test_reject_invalid_activity_and_date(self):
        for kw in ({"activity": []}, {"activity": "gambit"},
                   {"observation_date": None}, {"observation_date": "2026-6-24"},
                   {"observation_date": "2026-02-30"},
                   {"source_patch_version": ""}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                review(**kw)


if __name__ == "__main__":
    unittest.main()
