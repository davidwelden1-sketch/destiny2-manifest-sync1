"""Synthetic regression tests for published 9.7.0 Tarrabah/Jade Rabbit rules."""
import unittest
from simulator.exotic_weapon_970_activation import review_tarrabah, jade_rabbit_transition

class ExoticWeapon970Tests(unittest.TestCase):
    def test_tarrabah_requires_scorched_combatant_damage(self):
        base=dict(activity="pve",observation_date="2026-11-02")
        self.assertTrue(review_tarrabah(**base,target_scorched=True,registered_damage=True)["historical_scorch_condition_candidate"])
        for scorched,damage in ((False,True),(True,False),(False,False)):
            self.assertFalse(review_tarrabah(**base,target_scorched=scorched,registered_damage=damage)["historical_scorch_condition_candidate"])
    def test_tarrabah_progress_not_damage_and_pvp_fail_closed(self):
        base=dict(observation_date="2026-11-02",target_scorched=True,registered_damage=True)
        pve=review_tarrabah(activity="pve",**base)
        self.assertEqual(pve["scorched_combatant_meter_progress_bonus_percent"],33)
        self.assertIsNone(pve["pve_boss_dps_measured"])
        for activity in ("pvp","competitive","trials"):
            result=review_tarrabah(activity=activity,**base)
            self.assertFalse(result["historical_scorch_condition_candidate"])
            self.assertIsNone(result["scorched_combatant_meter_progress_bonus_percent"])
            self.assertIsNone(result["pvp_guardian_ttk_measured"])
    def test_jade_rabbit_stack_events(self):
        base=dict(activity="pvp",observation_date="2026-11-02")
        for event,expected in (("precision_kill",8),("direct_body_damage",6),("reload",7),("firefly_splash",7)):
            self.assertEqual(jade_rabbit_transition(**base,stacks=7,event=event)["historical_next_stacks"],expected)
        self.assertEqual(jade_rabbit_transition(**base,stacks=15,event="precision_kill")["historical_next_stacks"],15)
        self.assertEqual(jade_rabbit_transition(**base,stacks=0,event="direct_body_damage")["historical_next_stacks"],0)
    def test_jade_catalyst_consumes_only_if_active(self):
        base=dict(activity="pvp",observation_date="2026-11-02",stacks=5,event="special_reload")
        self.assertEqual(jade_rabbit_transition(**base,catalyst_active=True)["historical_next_stacks"],0)
        self.assertTrue(jade_rabbit_transition(**base,catalyst_active=True)["historical_micro_missile_candidate"])
        self.assertEqual(jade_rabbit_transition(**base,catalyst_active=False)["historical_next_stacks"],5)
        self.assertFalse(jade_rabbit_transition(**base,catalyst_active=False)["historical_micro_missile_candidate"])
        self.assertFalse(jade_rabbit_transition(**{**base,"stacks":0},catalyst_active=True)["historical_micro_missile_candidate"])
    def test_patch_day_and_before_are_not_certified(self):
        for day in ("2026-06-08","2026-06-09"):
            self.assertIsNone(jade_rabbit_transition(activity="pve",observation_date=day,stacks=5,event="precision_kill")["historical_next_stacks"])
            self.assertIsNone(review_tarrabah(activity="pve",observation_date=day,target_scorched=True,registered_damage=True)["historical_scorch_condition_candidate"])
    def test_invalid_inputs_fail_closed(self):
        base=dict(activity="pve",observation_date="2026-11-02")
        for bad in (dict(activity="gambit"),dict(observation_date="2026-2-2"),dict(target_scorched=1)):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                review_tarrabah(**{**base,"target_scorched":True,"registered_damage":True,**bad})
        for bad in (dict(stacks=True),dict(stacks=-1),dict(stacks=16),dict(catalyst_active=1),dict(event="hit")):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                jade_rabbit_transition(**{**base,"stacks":2,"event":"reload",**bad})
    def test_artifact_and_evidence_gates(self):
        result=jade_rabbit_transition(activity="trials",observation_date="2026-11-02",stacks=4,event="precision_kill")
        self.assertFalse(result["artifact_effects_enabled"])
        self.assertFalse(result["certified_for_app_build_recommendation"])
        self.assertFalse(result["runtime_activation_verified"])
        self.assertIsNone(result["pvp_guardian_ttk_measured"])

if __name__=="__main__":
    unittest.main()
