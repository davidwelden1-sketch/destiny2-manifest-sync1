"""Synthetic evidence-scope regression tests for Bungie 9.7.0 corrections."""
import unittest
from simulator.patch_970_grenade_verb_synergies import review_verb_activation


def review(**changes):
    args = dict(event="adrenaline_junkie_nonstandard_grenade",
                trigger="hellion", class_name="warlock", activity="pve",
                observation_date="2026-11-01")
    args.update(changes)
    return review_verb_activation(**args)


class GrenadeVerbSynergyEvidenceTests(unittest.TestCase):
    def test_warlock_hellion_is_an_official_activation_lead(self):
        r = review()
        self.assertIn("Hellion", r["official_correction"])
        self.assertEqual(r["status"], "official_historical_fix_not_gameplay_measurement")
        self.assertFalse(r["trigger_activation_measured"])

    def test_grapple_melee_is_a_cross_class_research_lead_not_measured(self):
        for cls in ("hunter", "titan", "warlock"):
            with self.subTest(cls=cls):
                r = review(trigger="grapple_melee", class_name=cls)
                self.assertEqual(r["status"], "official_historical_fix_not_gameplay_measurement")
                self.assertIsNone(r["kill_attribution"])

    def test_hellion_does_not_transfer_to_other_classes(self):
        for cls in ("hunter", "titan"):
            self.assertEqual(review(class_name=cls)["status"],
                             "class_trigger_scope_not_established")

    def test_bombardiers_hunter_native_arc_blind_pve_ten_seconds(self):
        r = review(event="bombardiers_native_debuff", trigger="arc_blind",
                   class_name="hunter")
        self.assertEqual(r["pve_arc_blind_seconds_official"], 10)
        self.assertIsNone(r["pve_void_suppress_seconds_official"])
        self.assertFalse(r["trigger_activation_measured"])

    def test_bombardiers_hunter_native_void_suppress_pve_ten_seconds(self):
        r = review(event="bombardiers_native_debuff", trigger="void_suppress",
                   class_name="hunter")
        self.assertEqual(r["pve_void_suppress_seconds_official"], 10)
        self.assertIsNone(r["pve_arc_blind_seconds_official"])

    def test_bombardiers_cannot_be_assigned_to_titan_or_warlock(self):
        for cls in ("titan", "warlock"):
            r = review(event="bombardiers_native_debuff", trigger="arc_blind",
                       class_name=cls)
            self.assertEqual(r["status"], "class_trigger_scope_not_established")
            self.assertIsNone(r["pve_arc_blind_seconds_official"])

    def test_pvp_durations_are_not_inferred_from_pve(self):
        for activity in ("pvp", "competitive", "trials"):
            for trigger in ("arc_blind", "void_suppress"):
                with self.subTest(activity=activity, trigger=trigger):
                    r = review(event="bombardiers_native_debuff",
                               trigger=trigger, class_name="hunter", activity=activity)
                    self.assertIsNone(r["pvp_debuff_duration_seconds"])
                    self.assertIsNone(r["pve_arc_blind_seconds_official"])
                    self.assertIsNone(r["pve_void_suppress_seconds_official"])

    def test_artifacts_disabled_in_competitive_and_trials(self):
        for activity in ("competitive", "trials"):
            self.assertIs(review(activity=activity)["artifact_effects_enabled"], False)
        self.assertIsNone(review(activity="pvp")["artifact_effects_enabled"])

    def test_historical_date_boundaries_and_version_mismatch(self):
        self.assertEqual(review(observation_date="2026-06-08")["status"],
                         "pre_fix_observation_requires_revalidation")
        self.assertEqual(review(observation_date="2026-06-09")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(review(source_patch_version="9.7.0.2")["status"],
                         "source_patch_version_mismatch")

    def test_invalid_inputs_fail_closed(self):
        for changes in (
            {"event": True}, {"event": "unknown"}, {"trigger": "grenade_hit"},
            {"class_name": "hunter", "trigger": "void_suppress"},
            {"activity": "gambit"}, {"observation_date": "2026-6-9"},
            {"observation_date": "2026-02-30"}, {"observation_date": None},
            {"source_patch_version": ""}, {"source_patch_version": None},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                review(**changes)

    def test_no_unearned_damage_roll_or_kill_certification(self):
        for event, trigger, cls in (
            ("adrenaline_junkie_nonstandard_grenade", "hellion", "warlock"),
            ("adrenaline_junkie_nonstandard_grenade", "grapple_melee", "titan"),
            ("bombardiers_native_debuff", "arc_blind", "hunter"),
        ):
            r = review(event=event, trigger=trigger, class_name=cls)
            self.assertIsNone(r["pve_boss_dps"])
            self.assertIsNone(r["pvp_guardian_ttk"])
            self.assertIsNone(r["damage_ownership"])
            self.assertIsNone(r["cooldown_seconds"])
            self.assertEqual(r["current_enhanced_perk_legality"], "unverified")
            self.assertFalse(r["current_artifact_allocation_verified"])


if __name__ == "__main__":
    unittest.main()
