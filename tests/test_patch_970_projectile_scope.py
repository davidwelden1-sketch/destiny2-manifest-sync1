"""Synthetic source-gating tests for official 9.7.0 projectile patch scope."""
import unittest

from simulator.patch_970_projectile_scope import (
    SHIELD_PROJECTILE_FAMILIES, audit_projectile_patch,
)


def audit(rule="anti_barrier_shield_overpenetration",
          family="rocket_launcher_projectile", **changes):
    args = dict(rule=rule, family=family, activity="pve",
                observation_date="2026-06-10", anti_barrier_capable=True)
    args.update(changes)
    return audit_projectile_patch(**args)


class ProjectilePatchScopeTests(unittest.TestCase):
    def test_all_three_explicit_anti_barrier_projectile_families(self):
        self.assertEqual(len(SHIELD_PROJECTILE_FAMILIES), 3)
        for family in SHIELD_PROJECTILE_FAMILIES:
            with self.subTest(family=family):
                r = audit(family=family)
                self.assertEqual(r["status"], "official_historical_patch_scope_only")
                self.assertIn("combatant shields", r["historical_effect"])
                self.assertFalse(r["champion_stun_verified"])

    def test_no_unconditional_penetration_without_anti_barrier(self):
        self.assertEqual(audit(anti_barrier_capable=None)["status"],
                         "anti_barrier_capability_unverified")
        self.assertEqual(audit(anti_barrier_capable=False)["status"],
                         "anti_barrier_capability_absent")
        self.assertIsNone(audit(anti_barrier_capable=False)["historical_effect"])

    def test_not_all_sword_hits_or_all_projectile_families(self):
        for family in ("sword_melee", "sniper_rifle", "ordinary_arrow"):
            with self.subTest(family=family):
                self.assertEqual(audit(family=family)["status"],
                                 "projectile_family_not_in_official_list")

    def test_meganeura_scaling_fix_is_not_a_numerical_multiplier(self):
        r = audit(rule="meganeura_detonation_scaling_fix",
                  family="meganeura_trait_detonation",
                  anti_barrier_capable=None)
        self.assertEqual(r["status"], "official_historical_patch_scope_only")
        self.assertIn("scaling was corrected", r["historical_effect"])
        self.assertIsNone(r["damage_multiplier"])
        self.assertIsNone(r["affected_exact_item_hashes"])

    def test_meganeura_not_assumed_for_other_traits(self):
        r = audit(rule="meganeura_detonation_scaling_fix",
                  family="dragonfly_trait_detonation")
        self.assertEqual(r["status"], "trait_family_not_in_official_list")

    def test_pvp_and_artifact_disabled_modes_do_not_import_pve(self):
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = audit(activity=mode)
                self.assertEqual(r["status"], "pvp_application_not_established")
                self.assertIsNone(r["historical_effect"])
                self.assertIsNone(r["guardian_ttk"])
                self.assertIs(r["artifact_enabled"], False if mode != "pvp" else None)

    def test_patch_version_and_date_freshness(self):
        for changes, status in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.6"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(changes=changes):
                r = audit(**changes)
                self.assertEqual(r["status"], status)
                self.assertIsNone(r["historical_effect"])

    def test_no_claims_about_rolls_stuns_ownership_or_damage(self):
        for r in (audit(), audit(rule="meganeura_detonation_scaling_fix",
                                  family="meganeura_trait_detonation")):
            for key in ("obtainable_roll_verified", "enhanced_perk_verified",
                        "active_artifact_verified", "current_gameplay_verified",
                        "gameplay_measured", "damage_ownership_measured",
                        "champion_stun_verified", "guardian_shield_penetration_verified"):
                self.assertFalse(r[key])
            self.assertIsNone(r["boss_dps"])
            self.assertIsNone(r["damage_multiplier"])

    def test_invalid_inputs_fail_closed(self):
        for changes in (
            {"rule": "unknown"}, {"family": ""}, {"family": True},
            {"activity": "gambit"}, {"observation_date": "2026-02-30"},
            {"observation_date": "2026-6-10"}, {"observation_date": None},
            {"source_patch_version": ""}, {"anti_barrier_capable": 1},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                audit(**changes)


if __name__ == "__main__":
    unittest.main()
