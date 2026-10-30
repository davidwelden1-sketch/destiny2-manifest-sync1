import unittest

from simulator.weapon_tier_rules import assess_tier_upgrade


class WeaponTierRulesTests(unittest.TestCase):
    def check(self, **overrides):
        args = dict(crafted_legendary=False, integrated_gear_tiering=True,
                    owned_perk_hashes=[100, 200], desired_perk_hashes=[100, 200])
        args.update(overrides)
        return assess_tier_upgrade(**args)

    def test_existing_roll_can_have_documented_tier_path(self):
        result = self.check()
        self.assertEqual(result["upgrade_path"], "documented_for_category")
        self.assertFalse(result["tier_upgrade_alone_cannot_supply_desired_roll"])
        self.assertEqual(result["enhanced_perk_legality"], "unverified")

    def test_upgrade_does_not_invent_missing_perk(self):
        result = self.check(desired_perk_hashes=[100, 999])
        self.assertEqual(result["desired_perks_absent_from_instance"], [999])
        self.assertTrue(result["tier_upgrade_alone_cannot_supply_desired_roll"])
        self.assertFalse(result["tier_upgrade_can_add_missing_perks"])

    def test_crafted_legendary_has_documented_path(self):
        result = self.check(crafted_legendary=True, integrated_gear_tiering=False)
        self.assertEqual(result["upgrade_path"], "documented_for_category")

    def test_unclassified_weapon_not_certified(self):
        result = self.check(integrated_gear_tiering=False)
        self.assertEqual(result["upgrade_path"], "not_established")

    def test_manifest_pool_not_treated_as_owned_instance(self):
        result = self.check(owned_perk_hashes=[100], desired_perk_hashes=[100, 200])
        self.assertEqual(result["desired_perks_absent_from_instance"], [200])
        self.assertFalse(result["live_instance_verified"])

    def test_invalid_hashes_fail_closed(self):
        for bad in ([True], [0], [-1], ["100"], None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.check(owned_perk_hashes=bad)

    def test_eligibility_unknown_is_not_truthy(self):
        with self.assertRaises(ValueError):
            self.check(crafted_legendary=None)


if __name__ == "__main__":
    unittest.main()
