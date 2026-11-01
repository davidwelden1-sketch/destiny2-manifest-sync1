"""Synthetic guard tests; no measured Destiny 2 gameplay is asserted."""
import unittest

from simulator.known_issue_synergy_gates_2026 import (
    ISSUE_CONDITIONS, SOURCE_URL, assess_synergy_issue,
)


def assess(issue, activity="pve", **overrides):
    flags = {key: True for key in ISSUE_CONDITIONS[issue]}
    flags.update(overrides)
    return assess_synergy_issue(
        issue=issue, activity=activity, conditions=flags,
        observation_date="2026-11-01",
        manifest_version="245114.26.10.13.2000-1-bnet.66137",
    )


class KnownIssueSynergyGatesTests(unittest.TestCase):
    def test_forerunner_prismatic_hunter_blocker_in_both_sandboxes(self):
        for activity in ("pve", "pvp"):
            with self.subTest(activity=activity):
                result = assess("forerunner_prismatic_gunpowder_gamble", activity)
                self.assertEqual(
                    result["status"],
                    "official_known_issue_blocks_certification_pending_retest")
                self.assertIsNone(result["measured_pve_boss_dps"])
                self.assertIsNone(result["measured_pvp_guardian_ttk"])
                self.assertEqual(result["source_url"], SOURCE_URL)

    def test_forerunner_nonprismatic_is_not_positive_certification(self):
        result = assess("forerunner_prismatic_gunpowder_gamble",
                        hunter_prismatic=False)
        self.assertEqual(result["status"],
                         "conditions_not_all_met_no_positive_certification")
        self.assertTrue(result["gameplay_retest_required"])

    def test_fusion_charge_time_masterwork_blocks_controlled_burst(self):
        for activity in ("pve", "pvp"):
            with self.subTest(activity=activity):
                result = assess("controlled_burst_charge_time_masterwork", activity)
                self.assertTrue(result["affected_configuration_matches"])
                self.assertFalse(result["enhanced_roll_legality_verified"])
                self.assertEqual(result["evidence_grade"],
                                 "official_known_issue_not_measured_gameplay")

    def test_no_charge_time_masterwork_not_assumed_to_be_measured(self):
        result = assess("controlled_burst_charge_time_masterwork",
                        charge_time_masterwork=False)
        self.assertEqual(result["status"],
                         "conditions_not_all_met_no_positive_certification")
        self.assertIsNone(result["measured_pve_boss_dps"])

    def test_warlock_solar_super_mantle_blocks_surges_not_all_damage(self):
        result = assess("mantle_solar_super_weapon_surge")
        self.assertIn("weapon surge", result["official_issue_description"])
        self.assertEqual(result["status"],
                         "official_known_issue_blocks_certification_pending_retest")
        self.assertIsNone(result["measured_damage_resistance"])

    def test_argent_blade_disabled_in_competitive_and_trials(self):
        for activity in ("competitive", "trials"):
            with self.subTest(activity=activity):
                result = assess("argent_blade_only_armor_charge_source", activity)
                self.assertEqual(result["status"],
                                 "artifact_disabled_no_artifact_synergy")
                self.assertFalse(result["artifact_effects_enabled"])

    def test_argent_blade_solo_source_requires_retest_in_pve(self):
        result = assess("argent_blade_only_armor_charge_source", "pve")
        self.assertEqual(result["status"],
                         "official_known_issue_blocks_certification_pending_retest")
        self.assertTrue(result["artifact_effects_enabled"])
        self.assertFalse(result["current_artifact_allocation_verified"])

    def test_artifact_additional_charge_source_not_certified(self):
        result = assess("argent_blade_only_armor_charge_source",
                        only_armor_charge_source=False)
        self.assertEqual(result["status"],
                         "conditions_not_all_met_no_positive_certification")

    def test_observation_predating_source_is_not_retroactively_verified(self):
        flags = {key: True for key in ISSUE_CONDITIONS[
            "forerunner_prismatic_gunpowder_gamble"]}
        result = assess_synergy_issue(
            issue="forerunner_prismatic_gunpowder_gamble",
            activity="pve", conditions=flags, observation_date="2026-06-01")
        self.assertEqual(result["status"],
                         "observation_predates_known_issue_snapshot")

    def test_rejects_bad_conditions_and_noncanonical_dates(self):
        key = "controlled_burst_charge_time_masterwork"
        good = {name: True for name in ISSUE_CONDITIONS[key]}
        for invalid in ({}, {"fusion_rifle": True}, {**good, "extra": True},
                        {**good, "fusion_rifle": 1},
                        {**good, "controlled_burst": "true"}):
            with self.subTest(conditions=invalid), self.assertRaises(ValueError):
                assess_synergy_issue(issue=key, activity="pve",
                                     conditions=invalid, observation_date="2026-11-01")
        for invalid in ("2026-1-1", "not-a-date", None):
            with self.subTest(date=invalid), self.assertRaises(ValueError):
                assess_synergy_issue(issue=key, activity="pve",
                                     conditions=good, observation_date=invalid)

    def test_rejects_unsupported_issue_activity_and_manifest_version(self):
        with self.assertRaises(ValueError):
            assess_synergy_issue(issue="unknown", activity="pve",
                                 conditions={}, observation_date="2026-11-01")
        with self.assertRaises(ValueError):
            assess("controlled_burst_charge_time_masterwork", "unknown")
        key = "controlled_burst_charge_time_masterwork"
        with self.assertRaises(ValueError):
            assess_synergy_issue(
                issue=key, activity="pve",
                conditions={name: True for name in ISSUE_CONDITIONS[key]},
                observation_date="2026-11-01", manifest_version="")
                

if __name__ == "__main__":
    unittest.main()
