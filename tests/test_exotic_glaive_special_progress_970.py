"""Synthetic source-bound Exotic Glaive checks; NOT gameplay measurements."""
import unittest

from simulator.exotic_glaive_special_progress_970 import (
    GLAIVES, SOURCE_970, assess_exotic_glaive_progress,
)


def check(weapon="edge_of_action", guardian_class="warlock", activity="pve",
          projectile_hits=3, melee_hits=0, observation_date="2026-11-01",
          **extra):
    return assess_exotic_glaive_progress(
        weapon=weapon, guardian_class=guardian_class, activity=activity,
        projectile_hits=projectile_hits, melee_hits=melee_hits,
        observation_date=observation_date, **extra,
    )


class ExoticGlaiveProgress970Tests(unittest.TestCase):
    def test_all_three_glaives_can_be_assessed_on_all_classes(self):
        for weapon in GLAIVES:
            for guardian_class in ("hunter", "titan", "warlock"):
                with self.subTest(weapon=weapon, guardian_class=guardian_class):
                    r = check(weapon=weapon, guardian_class=guardian_class)
                    self.assertTrue(r["cross_class_use_officially_supported"])
                    self.assertIn(SOURCE_970, r["source_urls"])
                    self.assertFalse(r["special_shot_ready_in_game_verified"])

    def test_three_projectiles_nominally_reach_six_units(self):
        r = check(projectile_hits=3)
        self.assertEqual(r["nominal_special_progress_units"], 6)
        self.assertTrue(r["nominal_threshold_reached"])
        self.assertEqual(r["projectile_progress_units_per_hit"], 2)

    def test_two_projectiles_do_not_nominally_reach_threshold(self):
        self.assertFalse(check(projectile_hits=2)["nominal_threshold_reached"])

    def test_six_melees_nominally_reach_threshold(self):
        r = check(projectile_hits=0, melee_hits=6)
        self.assertEqual(r["nominal_special_progress_units"], 6)
        self.assertEqual(r["melee_progress_units_per_hit"], 1)

    def test_mixed_projectile_and_melee_progress(self):
        self.assertEqual(check(projectile_hits=2, melee_hits=1)[
            "nominal_special_progress_units"], 5)
        self.assertTrue(check(projectile_hits=2, melee_hits=2)[
            "nominal_threshold_reached"])

    def test_pre_patch_is_not_retroactively_doubled(self):
        r = check(observation_date="2026-06-08")
        self.assertIsNone(r["nominal_special_progress_units"])
        self.assertIsNone(r["nominal_threshold_reached"])
        self.assertEqual(r["status"], "pre_patch_no_retroactive_double_progress")

    def test_exact_patch_date_uses_new_nominal_rule(self):
        self.assertEqual(check(observation_date="2026-06-09")[
            "nominal_special_progress_units"], 6)

    def test_separate_pve_and_pvp_never_invent_damage(self):
        for activity in ("pve", "pvp"):
            with self.subTest(activity=activity):
                r = check(activity=activity)
                self.assertIsNone(r["measured_pve_boss_dps"])
                self.assertIsNone(r["measured_pvp_guardian_ttk"])
                self.assertIsNone(r["measured_damage_resistance"])
                self.assertFalse(r["enhanced_perk_legality_verified"])

    def test_competitive_and_trials_artifact_effects_disabled(self):
        for activity in ("competitive", "trials"):
            with self.subTest(activity=activity):
                r = check(activity=activity, artifact_name="one_artifact",
                          artifact_perks=("one_perk",))
                self.assertFalse(r["artifact_mode_eligible"])
                self.assertFalse(r["artifact_effects_active"])

    def test_normal_pvp_artifact_not_assumed_active(self):
        r = check(activity="pvp", artifact_name="one_artifact",
                  artifact_perks=("one_perk",))
        self.assertTrue(r["artifact_mode_eligible"])
        self.assertIsNone(r["artifact_effects_active"])
        self.assertFalse(r["artifact_allocation_legal_verified"])

    def test_single_artifact_up_to_seven_not_slot_certified(self):
        perks = tuple("perk_%d" % i for i in range(7))
        r = check(artifact_name="one_artifact", artifact_perks=perks)
        self.assertEqual(r["selected_artifact_perks"], perks)
        self.assertFalse(r["artifact_allocation_legal_verified"])
        with self.assertRaises(ValueError):
            check(artifact_name="one_artifact", artifact_perks=perks + ("extra",))

    def test_rejects_invalid_hit_counts(self):
        for value in (-1, 1.5, True, "3", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                check(projectile_hits=value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                check(melee_hits=value)

    def test_rejects_invalid_dates_and_activity(self):
        for value in ("2026-6-9", "not-a-date", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                check(observation_date=value)
        with self.assertRaises(ValueError):
            check(activity="private_match")

    def test_rejects_bad_weapon_class_and_manifest_version(self):
        with self.assertRaises(ValueError):
            check(weapon="legendary_glaive")
        with self.assertRaises(ValueError):
            check(guardian_class="other")
        with self.assertRaises(ValueError):
            check(manifest_version="")

    def test_rejects_ambiguous_artifact_inputs(self):
        for kwargs in (
            {"artifact_perks": ("perk",)},
            {"artifact_name": "", "artifact_perks": ()},
            {"artifact_name": "a", "artifact_perks": ("p", "p")},
            {"artifact_name": "a", "artifact_perks": ("p", 5)},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                check(**kwargs)


if __name__ == "__main__":
    unittest.main()
