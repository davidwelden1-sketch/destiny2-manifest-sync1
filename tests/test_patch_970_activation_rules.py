"""Synthetic historical 9.7.0 activation tests; not gameplay measurements."""
import unittest
from simulator.patch_970_activation_rules import historical_attrition_hits, review_activation

class Patch970ActivationTests(unittest.TestCase):
    def test_wave_and_rocket_hits(self):
        self.assertEqual(historical_attrition_hits(weapon_type="Grenade Launcher", frame="Wave Frame"), 4)
        self.assertEqual(historical_attrition_hits(weapon_type="Rocket Launcher", frame="Adaptive Frame"), 3)

    def test_other_grenade_frames_fail_closed(self):
        for frame in ("Area Denial Frame", "Adaptive Frame", "Rapid-Fire Frame", "Double Fire", "Micro-Missile"):
            self.assertIsNone(historical_attrition_hits(weapon_type="Grenade Launcher", frame=frame))

    def test_hit_count_not_shot_count_or_automatic_proc(self):
        base=dict(perk="Attrition Orbs", activity="pve", observation_date="2026-11-02",
                  weapon_type="Grenade Launcher", frame="Wave Frame")
        self.assertFalse(review_activation(**base, registered_hits=3)["historical_condition_candidate"])
        r=review_activation(**base, registered_hits=4)
        self.assertTrue(r["historical_condition_candidate"])
        self.assertTrue(r["hits_are_not_shots"])
        self.assertFalse(r["runtime_activation_verified"])
        self.assertIsNone(r["pve_boss_dps_measured"])

    def test_desperado_precision_or_rapid_requires_reload(self):
        base=dict(perk="Desperado",activity="pvp",observation_date="2026-11-02")
        self.assertFalse(review_activation(**base, precision_final_blow=True)["historical_condition_candidate"])
        self.assertTrue(review_activation(**base, precision_final_blow=True, reloaded=True)["historical_condition_candidate"])
        self.assertFalse(review_activation(**base, rapid_final_blows=2, reloaded=True)["historical_condition_candidate"])
        self.assertTrue(review_activation(**base, rapid_final_blows=3, reloaded=True)["historical_condition_candidate"])
        self.assertIsNone(review_activation(**base, rapid_final_blows=3, reloaded=True)["pvp_guardian_ttk_measured"])

    def test_competitive_and_trials_artifact_disabled(self):
        for activity in ("competitive","trials"):
            r=review_activation(perk="Desperado",activity=activity,observation_date="2026-11-02",reloaded=True,precision_final_blow=True)
            self.assertFalse(r["artifact_effects_enabled"])
            self.assertFalse(r["certified_for_app_build_recommendation"])

    def test_historical_date_boundaries(self):
        base=dict(perk="Desperado",activity="pvp",reloaded=True,precision_final_blow=True)
        self.assertEqual(review_activation(**base,observation_date="2026-06-08")["status"],"pre_patch_observation")
        self.assertIsNone(review_activation(**base,observation_date="2026-06-09")["historical_condition_candidate"])

    def test_reject_invalid_inputs(self):
        base=dict(perk="Desperado",activity="pvp",observation_date="2026-11-02")
        for kw in (dict(rapid_final_blows=True),dict(rapid_final_blows=-1),dict(reloaded=1),
                   dict(observation_date="2026-2-2"),dict(activity="gambit"),
                   dict(manifest_version=""),dict(registered_hits=2),dict(weapon_type="Rocket Launcher")):
            with self.subTest(kw=kw),self.assertRaises(ValueError):
                review_activation(**dict(base,**kw))

if __name__=="__main__":
    unittest.main()
