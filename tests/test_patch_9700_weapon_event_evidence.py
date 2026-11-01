"""Synthetic tests for historical weapon-event facts, not gameplay results."""
import unittest
from simulator.patch_9700_weapon_event_evidence import (
    CORRECTIONS, audit_weapon_event,
)


def audit(mechanic="trinity_ghoul_lightning_rod_chain_kill_ammo_progress", **kwargs):
    inputs = dict(mechanic=mechanic, activity="pve", observation_date="2026-06-10")
    inputs.update(kwargs)
    return audit_weapon_event(**inputs)


class WeaponEventEvidenceTests(unittest.TestCase):
    def test_trinity_chain_kill_progress_is_not_a_brick_claim(self):
        r = audit()
        self.assertIn("ammo progress", r["historical_correction"])
        self.assertIsNone(r["ammo_progress_per_chain_kill"])
        self.assertIsNone(r["ammo_bricks_per_kill"])
        self.assertFalse(r["kill_attribution_measured"])

    def test_new_land_beyond_refresh_requires_existing_active_buff(self):
        r = audit("new_land_beyond_bullseye_bolster_precision_timer_refresh")
        self.assertIn("already active", r["historical_correction"])
        self.assertIsNone(r["bullseye_bolster_timer_seconds"])
        self.assertIsNone(r["guardian_ttk"])

    def test_no_unsupported_activity_specific_activation_claim(self):
        for mechanic in CORRECTIONS:
            for mode in ("pve", "pvp", "competitive", "trials"):
                with self.subTest(mechanic=mechanic, mode=mode):
                    r = audit(mechanic, activity=mode)
                    self.assertFalse(r["activity_specific_activation_verified"])
                    self.assertIsNone(r["damage_ownership"])
                    self.assertFalse(r["gameplay_measured"])

    def test_competitive_and_trials_artifacts_disabled(self):
        for mode in ("competitive", "trials"):
            r = audit(activity=mode)
            self.assertFalse(r["artifact_mode_eligible"])
            self.assertIs(r["artifact_effects_active"], False)

    def test_pve_and_ordinary_pvp_activation_not_assumed(self):
        for mode in ("pve", "pvp"):
            r = audit(activity=mode)
            self.assertTrue(r["artifact_mode_eligible"])
            self.assertIsNone(r["artifact_effects_active"])
            self.assertFalse(r["current_artifact_rotation_verified"])

    def test_historical_date_and_version_boundaries(self):
        for kw, status in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.2"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(kw=kw):
                r = audit(**kw)
                self.assertEqual(r["status"], status)
                self.assertIsNone(r["historical_correction"])

    def test_reject_malformed_inputs(self):
        for kw in (
            {"mechanic": "other"}, {"mechanic": True}, {"activity": []},
            {"activity": "gambit"}, {"observation_date": None},
            {"observation_date": "2026-6-10"}, {"observation_date": "2026-02-30"},
            {"source_patch_version": ""}, {"source_patch_version": None},
        ):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                audit(**kw)

    def test_no_invented_damage_or_roll_certification(self):
        for mechanic in CORRECTIONS:
            r = audit(mechanic)
            self.assertEqual(r["evidence_grade"], "official_historical_patch_not_measured")
            self.assertFalse(r["exact_weapon_hash_verified"])
            self.assertIsNone(r["boss_dps"])
            self.assertIsNone(r["guardian_ttk"])
            self.assertFalse(r["gameplay_measured"])


if __name__ == "__main__":
    unittest.main()
