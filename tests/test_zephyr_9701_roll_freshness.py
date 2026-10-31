"""Synthetic regression tests for official Zephyr 9.7.0.1 patch gate."""
import unittest

from simulator.zephyr_9701_roll_freshness import (
    PATCH_DATE, SOURCE_URL, audit_zephyr_left_column,
)


class Zephyr9701FreshnessTests(unittest.TestCase):
    def audit(self, **changes):
        args = {"weapon_name": "Zephyr", "observation_date": "2026-06-15",
                "column": "left", "activity": "pve"}
        return audit_zephyr_left_column(**{**args, **changes})

    def test_pre_fix_left_column_requires_revalidation(self):
        result = self.audit()
        self.assertEqual(result["status"], "pre_fix_left_column_requires_revalidation")
        self.assertTrue(result["leftColumnObservationRevalidationRequired"])

    def test_right_column_not_conflated_with_left(self):
        result = self.audit(column="right")
        self.assertFalse(result["leftColumnObservationRevalidationRequired"])
        self.assertEqual(result["status"], "not_affected_by_this_specific_fix")

    def test_other_weapons_not_inferred_affected(self):
        result = self.audit(weapon_name="Other sword")
        self.assertFalse(result["leftColumnObservationRevalidationRequired"])

    def test_patch_day_time_unknown(self):
        result = self.audit(observation_date="2026-06-16")
        self.assertEqual(result["status"], "patch_day_deployment_time_unknown")
        self.assertTrue(result["leftColumnObservationRevalidationRequired"])

    def test_post_fix_does_not_certify_roll(self):
        result = self.audit(observation_date="2026-06-17")
        self.assertFalse(result["leftColumnObservationRevalidationRequired"])
        self.assertEqual(result["status"], "post_fix_observation_not_roll_certification")
        self.assertFalse(result["currentExactRollCertified"])
        self.assertFalse(result["enhancedTraitCertified"])
        self.assertFalse(result["currentAcquisitionCertified"])

    def test_weapon_name_case_normalization(self):
        self.assertTrue(self.audit(weapon_name=" zEpHyR ")["leftColumnObservationRevalidationRequired"])

    def test_activity_independence_and_artifact_gate(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                result = self.audit(activity=activity)
                self.assertTrue(result["leftColumnObservationRevalidationRequired"])
                self.assertIs(result["artifactEnabled"],
                              False if activity in ("competitive", "trials") else None)
                self.assertFalse(result["pveBossDpsMeasured"])
                self.assertFalse(result["pvpTtkMeasured"])

    def test_invalid_inputs_fail_closed(self):
        cases = ({"weapon_name": ""}, {"weapon_name": None},
                 {"column": "both"}, {"activity": "unknown"},
                 {"observation_date": "2026-02-30"},
                 {"observation_date": "2026-6-16"},
                 {"observation_date": 20260616})
        for change in cases:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.audit(**change)

    def test_official_patch_provenance(self):
        result = self.audit()
        self.assertEqual(PATCH_DATE, "2026-06-16")
        self.assertIn("destiny_update_9_7_0_1", SOURCE_URL)
        self.assertEqual(result["evidenceGrade"],
                         "official_patch_note_not_live_instance_evidence")


if __name__ == "__main__":
    unittest.main()
