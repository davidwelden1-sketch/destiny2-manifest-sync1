"""Synthetic source-boundary tests for the 9.7.0 Saint/Ward rework."""
import unittest

from simulator.helm_saint_970_evidence import review_saint_ward


def review(**changes):
    args = dict(class_name="titan", activity="pve", event="kill",
                damage_type="void", weapons_of_light_active=True,
                observation_date="2026-11-01")
    args.update(changes)
    return review_saint_ward(**args)


class SaintWardEvidenceTests(unittest.TestCase):
    def test_titan_void_kill_is_an_activation_lead_not_measurement(self):
        r = review()
        self.assertTrue(r["the_saint_stack_generation_eligible"])
        self.assertTrue(r["void_or_kinetic_suppression_eligible"])
        self.assertIsNone(r["stack_gain_per_kill"])
        self.assertIsNone(r["suppression_radius_meters"])

    def test_kinetic_damage_source_is_also_a_suppression_lead(self):
        self.assertTrue(review(damage_type="kinetic")["void_or_kinetic_suppression_eligible"])

    def test_other_damage_not_automatically_suppressing(self):
        for damage_type in ("other", "unknown"):
            with self.subTest(damage_type=damage_type):
                r = review(damage_type=damage_type)
                self.assertTrue(r["the_saint_stack_generation_eligible"])
                self.assertFalse(r["void_or_kinetic_suppression_eligible"])

    def test_sustained_damage_is_an_official_trigger_but_not_a_rate(self):
        r = review(event="sustained_damage")
        self.assertTrue(r["the_saint_stack_generation_eligible"])
        self.assertIsNone(r["stack_gain_per_damage"])

    def test_ward_pickup_has_two_relocations_but_unknown_duration(self):
        r = review(event="ward_pickup")
        self.assertEqual(r["official_max_ward_relocations"], 2)
        self.assertTrue(r["ward_pickup_consumes_stacks_and_extends_duration_official"])
        self.assertFalse(r["the_saint_stack_generation_eligible"])
        self.assertIsNone(r["ward_duration_extension_seconds"])

    def test_allied_hunter_warlock_cannot_equip_helm(self):
        for class_name in ("hunter", "warlock"):
            with self.subTest(class_name=class_name):
                r = review(class_name=class_name)
                self.assertEqual(r["status"], "helm_not_equippable_on_class")
                self.assertFalse(r["the_saint_stack_generation_eligible"])
                self.assertFalse(r["void_or_kinetic_suppression_eligible"])
                self.assertIsNone(r["official_max_ward_relocations"])

    def test_weapons_of_light_is_a_required_condition(self):
        r = review(weapons_of_light_active=False)
        self.assertEqual(r["status"], "weapons_of_light_not_active")
        self.assertFalse(r["the_saint_stack_generation_eligible"])
        self.assertFalse(r["void_or_kinetic_suppression_eligible"])

    def test_historical_patch_boundaries(self):
        self.assertEqual(review(observation_date="2026-06-08")["status"],
                         "pre_rework_observation_requires_revalidation")
        self.assertEqual(review(observation_date="2026-06-09")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(review(source_patch_version="9.7.0.2")["status"],
                         "source_patch_version_mismatch")

    def test_pve_pvp_are_separate_and_no_ttk_or_dps_is_claimed(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                r = review(activity=activity)
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_guardian_ttk"])
                self.assertIsNone(r["damage_ownership"])
                self.assertIsNone(r["kill_attribution"])
                self.assertIsNone(r["suppression_duration_seconds"])
                self.assertFalse(r["current_artifact_allocation_verified"])
                self.assertIs(r["artifact_effects_enabled"],
                              False if activity in ("competitive", "trials") else None)

    def test_invalid_inputs_rejected(self):
        for change in ({"class_name": "guardian"}, {"activity": "gambit"},
                       {"event": "grenade"}, {"damage_type": "arc"},
                       {"weapons_of_light_active": 1},
                       {"observation_date": "2026-6-9"},
                       {"observation_date": None},
                       {"observation_date": "2026-02-30"},
                       {"source_patch_version": ""}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                review(**change)


if __name__ == "__main__":
    unittest.main()
