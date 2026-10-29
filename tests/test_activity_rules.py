import unittest

from simulator.activity_rules import activity_constraints, candidate_conflicts


class ActivityRulesTests(unittest.TestCase):
    def test_arena_collision_official_weapon_and_ability_constraints(self):
        rules = activity_constraints("  ARENA   COLLISION ")
        self.assertEqual(rules["status"], "official_historical_arena_collision")
        self.assertIs(rules["special_weapons_allowed"], False)
        self.assertIs(rules["supers_allowed"], False)
        self.assertIs(rules["powered_melees_allowed"], False)
        self.assertIs(rules["passive_grenade_recharge"], False)
        self.assertIs(rules["passive_class_ability_recharge"], False)
        self.assertEqual(rules["primary_damage_multiplier"], 1.0)
        self.assertEqual(rules["airborne_effectiveness_bonus"], 60)
        self.assertIsNone(rules["heavy_damage_multiplier"])
        self.assertIsNone(rules["artifact_enabled"])
        self.assertFalse(rules["current_playlist_verified"])

    def test_arena_candidate_conflicts(self):
        report = candidate_conflicts("arena collision", special=True,
                                     super_required=True, powered_melee=True,
                                     passive_ability_regen=True)
        self.assertEqual(report["conflicts"], [
            "special_weapon_disabled", "super_disabled",
            "powered_melee_disabled", "passive_ability_recharge_disabled"])
        self.assertFalse(report["legal_certified"])

    def test_trials_competitive_artifacts_disabled(self):
        for mode in ("Trials of Osiris", "competitive crucible"):
            self.assertIs(activity_constraints(mode)["artifact_enabled"], False)
            self.assertEqual(candidate_conflicts(mode, artifact_required=True)["conflicts"],
                             ["artifact_disabled"])

    def test_other_modes_do_not_inherit_arena_rules(self):
        for mode in ("control", "iron banner", "grandmaster nightfall"):
            rules = activity_constraints(mode)
            self.assertEqual(rules["status"], "mode_specific_review_required")
            self.assertIsNone(rules["special_weapons_allowed"])
            self.assertIsNone(rules["primary_damage_multiplier"])
            self.assertEqual(candidate_conflicts(mode, special=True)["conflicts"], [])

    def test_invalid_activity_and_candidate_flags_rejected(self):
        for activity in ("", "   ", None, 123):
            with self.assertRaises(ValueError):
                activity_constraints(activity)
        with self.assertRaises(ValueError):
            candidate_conflicts("arena collision", special=1)


if __name__ == "__main__":
    unittest.main()
