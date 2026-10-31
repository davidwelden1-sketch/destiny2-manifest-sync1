import unittest
from simulator.no_backup_plans_evidence import (
    no_backup_plans_evidence, DEFENSIVE_BUFFS, SOURCE_DATE, SOURCE_URL,
)


class NoBackupPlansEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(class_name="Titan", exotic_equipped=True,
                         event_kind="shotgun_final_blow", weapon_type="shotgun",
                         active_defensive_buffs=["Woven Mail"], activity="pve")

    def classify(self, **changes):
        return no_backup_plans_evidence(**{**self.args, **changes})

    def test_shotgun_final_blow_conditional_trigger(self):
        r = self.classify()
        self.assertEqual(r["status"], "official_trigger_conditions_met_not_gameplay_measured")
        self.assertTrue(r["health_regeneration_trigger_described"])
        self.assertTrue(r["buff_timer_extension_described"])
        self.assertTrue(r["damage_bonus_condition_described"])

    def test_melee_final_blow_without_shotgun(self):
        self.assertTrue(self.classify(event_kind="melee_final_blow",
                                      weapon_type=None)["health_regeneration_trigger_described"])

    def test_hits_are_not_final_blows(self):
        for kind in ("shotgun_hit", "melee_hit", "other_final_blow"):
            with self.subTest(kind=kind):
                self.assertFalse(self.classify(event_kind=kind)["health_regeneration_trigger_described"])

    def test_all_five_official_buffs_supported(self):
        self.assertEqual(len(DEFENSIVE_BUFFS), 5)
        for buff in DEFENSIVE_BUFFS:
            with self.subTest(buff=buff):
                r = self.classify(active_defensive_buffs=[buff])
                self.assertTrue(r["buff_timer_extension_described"])
                self.assertEqual(r["listed_active_buffs"], [buff])

    def test_absent_buff_no_extension_or_damage_condition(self):
        r = self.classify(active_defensive_buffs=[])
        self.assertFalse(r["buff_timer_extension_described"])
        self.assertFalse(r["damage_bonus_condition_described"])
        self.assertTrue(r["health_regeneration_trigger_described"])

    def test_unknown_buff_state_is_not_assumed(self):
        r = self.classify(active_defensive_buffs=None)
        self.assertEqual(r["buff_state"], "unknown_existing_buff_state")
        self.assertIsNone(r["damage_bonus_condition_described"])

    def test_unlisted_buffs_not_eligible(self):
        self.assertFalse(self.classify(active_defensive_buffs=["Radiant", "Devour"])[
            "damage_bonus_condition_described"])

    def test_trigger_does_not_grant_free_defensive_buff(self):
        r = self.classify(active_defensive_buffs=[])
        self.assertEqual(r["buffs_granted_by_trigger"], [])
        self.assertIsNone(r["void_overshield_partial_heal_condition"])

    def test_existing_overshield_partial_heal_requires_final_blow(self):
        self.assertEqual(self.classify(active_defensive_buffs=["Void Overshield"])[
            "void_overshield_partial_heal_condition"],
            "existing_void_overshield_and_qualifying_final_blow")
        self.assertIsNone(self.classify(event_kind="shotgun_hit",
            active_defensive_buffs=["Void Overshield"])["void_overshield_partial_heal_condition"])

    def test_other_class_or_missing_exotic_fails(self):
        for field, val in (("class_name", "Hunter"), ("class_name", "Warlock"),
                           ("exotic_equipped", False)):
            with self.subTest(field=field, val=val):
                r = self.classify(**{field: val})
                self.assertFalse(r["health_regeneration_trigger_described"])
                self.assertFalse(r["damage_bonus_condition_described"])

    def test_wrong_weapon_type_fails(self):
        self.assertFalse(self.classify(weapon_type="sidearm")[
            "health_regeneration_trigger_described"])

    def test_unknown_weapon_type_fails_closed(self):
        self.assertEqual(self.classify(weapon_type=None)["status"], "insufficient_trigger_evidence")

    def test_unknown_exotic_fails_closed(self):
        r = self.classify(exotic_equipped=None)
        self.assertEqual(r["status"], "insufficient_trigger_evidence")
        self.assertIsNone(r["damage_bonus_condition_described"])

    def test_pve_pvp_separation_and_artifact_policy(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = self.classify(activity=mode)
                self.assertIsNone(r["pve_boss_dps"])
                self.assertIsNone(r["pvp_ttk"])
                self.assertIsNone(r["pve_damage_resistance"])
                if mode in ("trials", "competitive"):
                    self.assertFalse(r["artifact_enabled"])
                else:
                    self.assertFalse(r["current_artifact_selection_verified"])

    def test_no_invented_measured_values_or_rolls(self):
        r = self.classify()
        for field in ("duration_extension_seconds", "damage_bonus_multiplier",
                      "healing_per_second"):
            self.assertIsNone(r[field])
        self.assertFalse(r["exact_shotgun_hash_verified"])
        self.assertFalse(r["enhanced_perk_roll_verified"])
        self.assertFalse(r["gameplay_measured"])

    def test_validation(self):
        for change in ({"class_name": ""}, {"exotic_equipped": 1},
                       {"event_kind": "shotgun_precision_hit"}, {"activity": "unknown"},
                       {"weapon_type": ""}, {"active_defensive_buffs": "woven mail"},
                       {"active_defensive_buffs": [None]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.classify(**change)

    def test_source_metadata(self):
        self.assertEqual(SOURCE_DATE, "2026-06-09")
        self.assertIn("destiny_update_9_7_0", SOURCE_URL)


if __name__ == "__main__":
    unittest.main()
