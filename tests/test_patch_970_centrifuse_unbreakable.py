"""Synthetic tests for official 9.7.0 Centrifuse/Unbreakable evidence gates."""
import unittest

from simulator.patch_970_centrifuse_unbreakable import (
    audit_centrifuse_refill, audit_unbreakable_devour,
)


class CentrifuseEvidenceTests(unittest.TestCase):
    def refill(self, **overrides):
        args = dict(observation_date="2026-06-10", activity="pve",
                    event="refill_trigger", weapon_name="Centrifuse")
        args.update(overrides)
        return audit_centrifuse_refill(**args)

    def test_post_patch_refill_amount_not_trigger_frequency(self):
        r = self.refill()
        self.assertEqual(r["status"], "official_post_patch_refill_amount_only")
        self.assertEqual(r["previous_refill_percent_per_trigger_official"], 4)
        self.assertEqual(r["post_patch_refill_percent_per_trigger_official"], 10)
        self.assertIsNone(r["refill_trigger_conditions"])
        self.assertIsNone(r["refill_frequency"])
        self.assertFalse(r["actual_refill_measured"])
        self.assertFalse(r["current_manifest_item_verified"])

    def test_other_weapon_or_event_does_not_inherit_centrifuse_rule(self):
        self.assertEqual(self.refill(weapon_name="Riskrunner")["status"],
                         "weapon_identity_not_established")
        self.assertIsNone(self.refill(weapon_name="Riskrunner")
                          ["post_patch_refill_percent_per_trigger_official"])
        self.assertEqual(self.refill(event="weapon_kill")["status"],
                         "event_not_supported_by_patch_note")

    def test_pvp_numbers_not_invented(self):
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = self.refill(activity=mode)
                self.assertEqual(r["post_patch_refill_percent_per_trigger_official"], 10)
                self.assertIsNone(r["pvp_guardian_ttk"])
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIs(r["artifact_enabled"], False if mode != "pvp" else None)

    def test_patch_day_and_version_mismatch_are_not_current_certification(self):
        for kwargs, status in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.1"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(kwargs=kwargs):
                r = self.refill(**kwargs)
                self.assertEqual(r["status"], status)
                self.assertIsNone(r["post_patch_refill_percent_per_trigger_official"])

    def test_bad_refill_inputs_rejected(self):
        for bad in (
            {"observation_date": "2026-6-10"},
            {"observation_date": "2026-02-30"},
            {"observation_date": 20260610},
            {"activity": "gambit"},
            {"event": ""},
            {"weapon_name": None},
            {"source_patch_version": ""},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.refill(**bad)


class UnbreakableEvidenceTests(unittest.TestCase):
    def devour(self, **overrides):
        args = dict(observation_date="2026-06-10", activity="pve",
                    class_name="titan", event="unbreakable_blast_final_blow",
                    aspect_equipped=True)
        args.update(overrides)
        return audit_unbreakable_devour(**args)

    def test_titan_blast_final_blow_is_only_documented_condition(self):
        r = self.devour()
        self.assertEqual(r["status"], "official_post_patch_condition_only")
        self.assertTrue(r["official_devour_grant_condition_met"])
        self.assertIsNone(r["devour_duration_seconds"])
        self.assertFalse(r["devour_healing_measured"])
        self.assertFalse(r["blast_kill_attribution_measured"])
        self.assertFalse(r["guardian_final_blow_verified"])

    def test_other_classes_cannot_inherit_titan_aspect(self):
        for cls in ("hunter", "warlock"):
            with self.subTest(cls=cls):
                r = self.devour(class_name=cls)
                self.assertEqual(r["status"], "class_not_supported_by_aspect")
                self.assertFalse(r["official_devour_grant_condition_met"])

    def test_aspect_absent_or_nonblast_kill_fails_closed(self):
        self.assertEqual(self.devour(aspect_equipped=False)["status"],
                         "aspect_not_equipped")
        self.assertEqual(self.devour(event="weapon_kill")["status"],
                         "event_not_supported_by_patch_note")

    def test_pve_and_pvp_require_separate_measurements(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = self.devour(activity=mode)
                self.assertTrue(r["official_devour_grant_condition_met"])
                self.assertIsNone(r["pve_damage_resistance"])
                self.assertIsNone(r["pvp_guardian_ttk"])
                self.assertFalse(r["ability_regeneration_measured"])
                self.assertIs(r["artifact_enabled"], False if mode in ("competitive", "trials") else None)

    def test_patch_freshness_and_invalid_conditions(self):
        self.assertEqual(self.devour(observation_date="2026-06-09")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(self.devour(source_patch_version="9.7.0.2")["status"],
                         "source_patch_version_mismatch")
        for bad in (
            {"class_name": "druid"},
            {"event": None},
            {"aspect_equipped": 1},
            {"aspect_equipped": None},
            {"observation_date": "2026-02-30"},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.devour(**bad)


if __name__ == "__main__":
    unittest.main()
