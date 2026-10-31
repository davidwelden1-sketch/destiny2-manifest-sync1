import unittest

from simulator.weapon_enhancement_970 import classify_enhancement_evidence as classify


class WeaponEnhancement970Tests(unittest.TestCase):
    def check(self, **changes):
        args = dict(item_hash=1976481399, gear_tier=3, category="crafted")
        return classify(**{**args, **changes})

    def test_tier_two_does_not_unlock_enhanced_mod(self):
        r = self.check(gear_tier=2, enhanced_mod_compatible=True)
        self.assertFalse(r["enhanced_weapon_mod_tier_requirement_met"])
        self.assertFalse(r["enhanced_weapon_mod_use_established_from_supplied_inputs"])

    def test_tier_three_unlock_rule_not_enhanced_trait(self):
        r = self.check(gear_tier=3, enhanced_mod_compatible=True)
        self.assertTrue(r["enhanced_weapon_mod_use_established_from_supplied_inputs"])
        self.assertEqual(r["enhanced_trait_perk_legality"], "not_established_by_tier_or_mod")
        self.assertFalse(r["current_roll_certified"])

    def test_unknown_mod_compatibility_does_not_certify_use(self):
        self.assertIsNone(self.check()["enhanced_weapon_mod_use_established_from_supplied_inputs"])

    def test_explicit_incompatible_mod_not_certified(self):
        self.assertFalse(self.check(enhanced_mod_compatible=False)["enhanced_weapon_mod_use_established_from_supplied_inputs"])

    def test_unknown_tier_does_not_infer_unlock(self):
        r = self.check(gear_tier=None, enhanced_mod_compatible=True)
        self.assertIsNone(r["enhanced_weapon_mod_tier_requirement_met"])
        self.assertIsNone(r["enhanced_weapon_mod_use_established_from_supplied_inputs"])

    def test_crafted_and_reshape_adept_tier_five_path_documented(self):
        for category in ("crafted", "reshape_capable_raid_adept"):
            with self.subTest(category=category):
                self.assertTrue(self.check(category=category)["tier_five_upgrade_category_documented"])

    def test_other_category_not_declared_ineligible(self):
        r = self.check(category="other")
        self.assertFalse(r["tier_five_upgrade_category_documented"])
        self.assertFalse(r["current_obtainability_certified"])

    def test_enhanced_intrinsic_prerequisite_separate(self):
        for value in (True, False, None):
            with self.subTest(value=value):
                r = self.check(enhanced_intrinsic=value)
                self.assertIs(r["enhanced_intrinsic_stat_bonus_prerequisite_met"], value)
                self.assertIsNone(r["additive_stat_bonus_amount"])

    def test_tier_five_does_not_imply_intrinsic_or_enhanced_trait(self):
        r = self.check(gear_tier=5, enhanced_intrinsic=None)
        self.assertIsNone(r["enhanced_intrinsic_stat_bonus_prerequisite_met"])
        self.assertIsNone(r["enhanced_trait_socket_hashes"])

    def test_competitive_and_trials_artifact_disabled(self):
        for activity in ("competitive", "trials"):
            with self.subTest(activity=activity):
                r = self.check(activity=activity)
                self.assertIs(r["artifact_enabled"], False)
                self.assertFalse(r["pvp_ttk_measured"])

    def test_pve_pvp_damage_not_inferred(self):
        for activity in ("pve", "pvp"):
            r = self.check(activity=activity)
            self.assertFalse(r["pve_damage_measured"])
            self.assertFalse(r["pvp_ttk_measured"])
            self.assertIsNone(r["artifact_enabled"])

    def test_bad_hash_tier_category_and_flags_rejected(self):
        cases = [dict(item_hash=0), dict(item_hash=True), dict(gear_tier=0),
                 dict(gear_tier=6), dict(gear_tier=True), dict(category="adept"),
                 dict(enhanced_intrinsic=1), dict(enhanced_mod_compatible="yes"),
                 dict(activity="unknown")]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.check(**case)

    def test_no_item_hash_cross_contamination(self):
        a = self.check(item_hash=111)
        b = self.check(item_hash=222)
        self.assertEqual(a["item_hash"], 111)
        self.assertEqual(b["item_hash"], 222)
        self.assertFalse(a["live_instance_verified"])

    def test_source_and_review_dates_present(self):
        r = self.check()
        self.assertIn("destiny_update_9_7_0", r["source_url"])
        self.assertEqual(r["source_date"], "2026-06-09")
        self.assertEqual(r["reviewed_date"], "2026-10-31")


if __name__ == "__main__":
    unittest.main()
