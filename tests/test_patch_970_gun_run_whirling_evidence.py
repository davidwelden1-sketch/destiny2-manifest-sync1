"""Synthetic source-scope tests for 9.7.0 Gun and Run / Whirling Ovation."""
import unittest

from simulator.patch_970_gun_run_whirling_evidence import review_970_trigger


def review(key="gun_and_run", event="final_blows_build_stacks", **kw):
    kw.setdefault("activity", "pve")
    kw.setdefault("class_name", "hunter")
    kw.setdefault("observation_date", "2026-11-01")
    return review_970_trigger(key, event=event, **kw)


class GunRunWhirlingEvidenceTests(unittest.TestCase):
    def test_gun_and_run_has_separate_kill_and_sprint_events(self):
        r = review()
        self.assertEqual(r["official_activation_conditions"],
                         ("final_blows_build_stacks", "sprinting_consumes_stack"))
        self.assertIsNone(r["measured_reload_amount"])
        self.assertFalse(r["enhanced_legality_verified"])

    def test_sprint_event_does_not_prove_stacks_or_reload(self):
        r = review(event="sprinting_consumes_stack")
        self.assertEqual(r["status"], "post_patch_not_gameplay_measured")
        self.assertIsNone(r["measured_trigger_rate"])

    def test_bow_draw_speed_is_type_specific(self):
        self.assertTrue(review(weapon_type="bow")["bow_specific_draw_speed_effect"])
        self.assertFalse(review(weapon_type="other")["bow_specific_draw_speed_effect"])

    def test_whirling_ovation_has_qualitative_not_exact_gain(self):
        r = review(key="whirling_ovation", event="damage_grants_anticipation")
        self.assertEqual(r["official_relative_anticipation_gain"],
                         "just_over_11_percent_not_exact")
        self.assertIsNone(r["measured_anticipation_per_damage"])
        self.assertIsNone(r["pve_boss_dps"])

    def test_unrelated_event_is_not_certified(self):
        r = review(event="grenade_kill")
        self.assertEqual(r["status"], "event_not_in_official_activation")

    def test_pvp_and_pve_not_conflated(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                r = review(activity=activity)
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_guardian_ttk"])
                self.assertIs(r["artifact_effects_enabled"], False
                              if activity in ("competitive", "trials") else None)

    def test_patch_date_and_version_gate(self):
        self.assertEqual(review(observation_date="2026-06-08")["status"],
                         "historical_pre_fix_revalidation_required")
        self.assertEqual(review(observation_date="2026-06-09")["status"],
                         "patch_day_deployment_time_unknown")
        self.assertEqual(review(source_patch_version="9.7.0.1")["status"],
                         "source_version_mismatch")

    def test_all_classes_remain_hypotheses(self):
        for cls in ("hunter", "titan", "warlock"):
            r = review(class_name=cls)
            self.assertEqual(r["class_name"], cls)
            self.assertFalse(r["weapon_hash_verified"])

    def test_bad_inputs_fail_closed(self):
        for kw in ({"activity": "unknown"}, {"class_name": "bard"},
                   {"observation_date": "2026-6-9"},
                   {"observation_date": "2026-02-30"},
                   {"weapon_type": "handcannon"},
                   {"source_patch_version": ""}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                review(**kw)
        with self.assertRaises(ValueError):
            review(key="not_an_official_rule")
        with self.assertRaises(ValueError):
            review(event="")


if __name__ == "__main__":
    unittest.main()
