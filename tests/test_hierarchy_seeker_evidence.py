import unittest

from simulator.hierarchy_seeker_evidence import (
    SOURCE_970, SOURCE_9702, hierarchy_event_evidence,
)


class HierarchySeekerEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.base = dict(
            weapon_name="Hierarchy of Needs", event_kind="seeker_hit",
            target_kind="combatant", activity="pve",
            anti_barrier_active=None, catalyst_equipped=None,
        )

    def check(self, **changes):
        return hierarchy_event_evidence(**{**self.base, **changes})

    def test_seeker_hit_combatant_has_official_text_not_damage(self):
        r = self.check()
        self.assertEqual(r["status"], "official_seeker_scorch_text_not_gameplay_measured")
        self.assertEqual(r["combatant_seeker_base_scorch"], 15)
        self.assertEqual(r["parenthetical_bonus_stacks"], 5)
        self.assertIsNone(r["pve_boss_dps"])

    def test_parenthetical_bonus_condition_not_invented(self):
        self.assertIsNone(self.check()["parenthetical_bonus_condition"])

    def test_catalyst_not_required_for_published_seeker_effect(self):
        for value in (True, False, None):
            with self.subTest(catalyst=value):
                self.assertEqual(self.check(catalyst_equipped=value)["combatant_seeker_base_scorch"], 15)

    def test_precision_hit_does_not_inherit_seeker_scorch(self):
        r = self.check(event_kind="precision_hit")
        self.assertIsNone(r["combatant_seeker_base_scorch"])
        self.assertIsNone(r["published_seeker_scorch_text"])
        self.assertEqual(r["status"], "precision_hit_amount_unverified")

    def test_pvp_precision_hit_guidance_fix_not_amount(self):
        r = self.check(event_kind="precision_hit", target_kind="guardian", activity="pvp")
        self.assertEqual(r["status"], "official_pvp_guidance_energy_fix_amount_unverified")
        self.assertIsNone(r["guidance_energy_amount"])
        self.assertIsNone(r["pvp_ttk"])

    def test_pvp_seeker_hit_does_not_import_combatant_stacks(self):
        r = self.check(target_kind="guardian", activity="pvp")
        self.assertEqual(r["status"], "official_seeker_scorch_text_guardian_values_unverified")
        self.assertIsNone(r["combatant_seeker_base_scorch"])
        self.assertEqual(r["published_seeker_scorch_text"], "+15 (+5)")

    def test_anti_barrier_combatant_shield_conditional(self):
        r = self.check(event_kind="seeker_shield_contact", anti_barrier_active=True)
        self.assertEqual(r["status"], "official_conditional_combatant_shield_overpenetration")
        self.assertIsNone(r["combatant_seeker_base_scorch"])

    def test_anti_barrier_missing_or_false_not_claimed(self):
        for value, expected in ((False, "anti_barrier_condition_not_met"),
                                (None, "anti_barrier_condition_unknown")):
            with self.subTest(active=value):
                self.assertEqual(self.check(event_kind="seeker_shield_contact",
                                            anti_barrier_active=value)["status"], expected)

    def test_guardian_shield_not_covered_by_combatant_rule(self):
        r = self.check(event_kind="seeker_shield_contact", target_kind="guardian",
                       activity="pvp", anti_barrier_active=True)
        self.assertEqual(r["status"], "guardian_shield_overpenetration_not_established")

    def test_competitive_and_trials_artifact_disabled(self):
        for mode in ("competitive", "trials", "trials of osiris"):
            with self.subTest(mode=mode):
                r = self.check(event_kind="precision_hit", target_kind="guardian", activity=mode)
                self.assertIs(r["artifact_enabled"], False)
                self.assertFalse(r["current_artifact_verified"])

    def test_unknown_pve_artifact_stays_unknown(self):
        self.assertIsNone(self.check()["artifact_enabled"])

    def test_wrong_weapon_and_mismatched_target_fail_closed(self):
        self.assertEqual(self.check(weapon_name="Tarrabah")["status"], "different_weapon")
        self.assertEqual(self.check(target_kind="guardian")["status"], "activity_target_mismatch")
        self.assertEqual(self.check(activity="pvp")["status"], "activity_target_mismatch")

    def test_no_exotic_synergy_or_ownership_certification(self):
        r = self.check()
        self.assertIsNone(r["dawn_chorus_ignition_bonus"])
        self.assertIsNone(r["scorch_source_ownership"])
        self.assertFalse(r["gameplay_activation_measured"])
        self.assertFalse(r["current_weapon_identity_verified"])

    def test_reject_invalid_inputs(self):
        bad = (("weapon_name", ""), ("event_kind", "bodyshot"),
               ("target_kind", "boss"), ("activity", "unknown"),
               ("anti_barrier_active", 1), ("catalyst_equipped", "yes"))
        for key, value in bad:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(**{key: value})

    def test_official_sources_are_distinct_patches(self):
        self.assertIn("9_7_0", SOURCE_970)
        self.assertIn("9_7_0_2", SOURCE_9702)


if __name__ == "__main__":
    unittest.main()
