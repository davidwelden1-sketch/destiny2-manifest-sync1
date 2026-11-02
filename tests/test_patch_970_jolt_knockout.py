"""Synthetic patch-condition regression tests, not in-game measurements."""
import unittest
from decimal import Decimal
from simulator.patch_970_jolt_knockout import review_construct_jolt, review_knockout_pvp


class Patch970JoltKnockoutTests(unittest.TestCase):
    def test_spark_arc_soul_four_second_boundary(self):
        base = dict(fragment="Spark of Shock", construct="Arc Soul", activity="pve", observation_date="2026-11-02")
        for v in (0, Decimal("3.9999999999999999999999")):
            self.assertEqual(review_construct_jolt(**base, seconds_since_last_application=v)["historical_timing_gate"], "inside_four_second_cooldown")
        for v in (4, "4.0000000000000000000001"):
            r = review_construct_jolt(**base, seconds_since_last_application=v)
            self.assertEqual(r["historical_timing_gate"], "outside_four_second_cooldown_proc_not_guaranteed")
            self.assertFalse(r["activation_guaranteed"])
            self.assertIsNone(r["pve_boss_dps_measured"])

    def test_spark_ionic_sentry_but_not_dominance_ionic(self):
        b = dict(construct="Ionic Sentry", activity="pve", observation_date="2026-11-02", seconds_since_last_application=4)
        self.assertTrue(review_construct_jolt(fragment="Spark of Shock", **b)["combination_documented"])
        r = review_construct_jolt(fragment="Facet of Dominance", **b)
        self.assertFalse(r["combination_documented"])
        self.assertIsNone(r["historical_timing_gate"])

    def test_no_first_jolt_or_cross_construct_inference(self):
        r = review_construct_jolt(fragment="Facet of Dominance", construct="Arc Soul", activity="pvp", observation_date="2026-11-02")
        self.assertIsNone(r["historical_timing_gate"])
        self.assertFalse(r["cross_construct_shared_timer_verified"])
        self.assertIsNone(r["pvp_guardian_damage_measured"])

    def test_knockout_pvp_only_and_not_ttk(self):
        for activity in ("pvp", "competitive", "trials"):
            r = review_knockout_pvp(activity=activity, observation_date="2026-11-02")
            self.assertTrue(r["pvp_specific_rule_applicable"])
            self.assertFalse(r["bonus_lunge_range_vs_players"])
            self.assertFalse(r["activating_melee_receives_early_knockout_bonus"])
            self.assertIsNone(r["pvp_ttk_measured"])
        self.assertIsNone(review_knockout_pvp(activity="pve", observation_date="2026-11-02")["bonus_lunge_range_vs_players"])

    def test_artifact_off_in_competitive_and_trials(self):
        for activity in ("competitive", "trials"):
            r = review_construct_jolt(fragment="Spark of Shock", construct="Arc Soul", activity=activity, observation_date="2026-11-02")
            self.assertFalse(r["artifact_effects_active"])
            self.assertFalse(r["certified_for_app_build_recommendation"])

    def test_patch_boundary_and_mismatch_fail_closed(self):
        b = dict(fragment="Spark of Shock", construct="Arc Soul", activity="pve", seconds_since_last_application=4)
        for day in ("2026-06-08", "2026-06-09"):
            r = review_construct_jolt(**b, observation_date=day)
            self.assertIsNone(r["historical_timing_gate"])
        r = review_knockout_pvp(activity="pvp", observation_date="2026-11-02", source_patch_version="9.7.0.6")
        self.assertFalse(r["pvp_specific_rule_applicable"])
        self.assertIsNone(r["bonus_lunge_range_vs_players"])

    def test_reject_unreliable_inputs(self):
        b = dict(fragment="Spark of Shock", construct="Arc Soul", activity="pve", observation_date="2026-11-02")
        for changes in (dict(seconds_since_last_application=3.5), dict(seconds_since_last_application=-1),
                        dict(seconds_since_last_application="NaN"), dict(seconds_since_last_application="Infinity"),
                        dict(seconds_since_last_application=True), dict(fragment="unknown"),
                        dict(construct="Jolting Feedback"), dict(activity="gambit"),
                        dict(observation_date="2026-2-2"), dict(source_patch_version="")):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                review_construct_jolt(**dict(b, **changes))


if __name__ == "__main__":
    unittest.main()
