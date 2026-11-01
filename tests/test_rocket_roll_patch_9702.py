import unittest
from simulator.rocket_roll_patch_9702 import assess_rocket_roll_patch


def assess(**changes):
    params = dict(guardian_class="titan", activity="pve",
                  observation_date="2026-11-01", destination="europa",
                  weapon_type="rocket_launcher", perk_name="Lead from Gold")
    params.update(changes)
    return assess_rocket_roll_patch(**params)


class RocketRollPatchTests(unittest.TestCase):
    def test_official_negative_roll_for_europa_and_moon(self):
        for destination in ("europa", "moon"):
            with self.subTest(destination=destination):
                r = assess(destination=destination)
                self.assertIs(r["lead_from_gold_current_legality_supported"], False)
                self.assertEqual(r["reported_replacement_perk"], "Impromptu Ammunition")
                self.assertFalse(r["replacement_on_this_exact_hash_verified"])

    def test_no_unsupported_positive_roll_claim(self):
        for changes in ({"destination": "other"}, {"destination": "unknown"},
                        {"weapon_type": "fusion_rifle"},
                        {"perk_name": "Impromptu Ammunition"},
                        {"observation_date": "2026-06-22"}):
            with self.subTest(changes=changes):
                r = assess(**changes)
                self.assertIsNone(r["lead_from_gold_current_legality_supported"])
                self.assertFalse(r["current_acquisition_verified"])
                self.assertFalse(r["enhanced_perk_verified"])

    def test_replacement_not_falsely_assigned_to_unrelated_perks(self):
        for perk in ("Impromptu Ammunition", "Explosive Light", "Bait and Switch"):
            with self.subTest(perk=perk):
                r = assess(perk_name=perk)
                self.assertIsNone(r["reported_replacement_perk"])
                self.assertIsNone(r["lead_from_gold_current_legality_supported"])
                self.assertFalse(r["replacement_on_this_exact_hash_verified"])

    def test_boundary_date(self):
        self.assertIsNone(assess(observation_date="2026-06-22")["lead_from_gold_current_legality_supported"])
        self.assertIs(assess(observation_date="2026-06-23")["lead_from_gold_current_legality_supported"], False)

    def test_pve_pvp_and_class_separation(self):
        for cls in ("hunter", "titan", "warlock"):
            for activity in ("pve", "pvp", "competitive", "trials"):
                with self.subTest(cls=cls, activity=activity):
                    r = assess(guardian_class=cls, activity=activity)
                    self.assertIsNone(r["measured_pve_boss_dps"])
                    self.assertIsNone(r["measured_pvp_ttk"])
                    self.assertIsNone(r["measured_ammo_regeneration"])
                    self.assertEqual(r["artifact_effects_active"] is False,
                                     activity in ("competitive", "trials"))

    def test_item_hash_does_not_certify_replacement(self):
        r = assess(item_hash=123456789, manifest_version="test-manifest")
        self.assertEqual(r["item_hash_reported_by_caller"], 123456789)
        self.assertFalse(r["replacement_on_this_exact_hash_verified"])
        self.assertEqual(r["manifest_version"], "test-manifest")

    def test_artifact_limits_and_duplicates(self):
        with self.assertRaises(ValueError):
            assess(artifact_name="Tablet", artifact_perks=tuple(str(x) for x in range(8)))
        with self.assertRaises(ValueError):
            assess(artifact_name="Tablet", artifact_perks=("X", "X"))
        with self.assertRaises(ValueError):
            assess(artifact_perks=("X",))
        r = assess(artifact_name="Tablet", artifact_perks=("X",))
        self.assertFalse(r["artifact_allocation_legal_verified"])

    def test_invalid_date_hash_and_metadata_fail_closed(self):
        for changes in ({"observation_date": "2026-6-23"},
                        {"observation_date": "2026-02-30"},
                        {"item_hash": True}, {"item_hash": 0},
                        {"manifest_version": ""},
                        {"destination": "mars"}, {"perk_name": ""}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                assess(**changes)

    def test_official_source_provenance_and_stable_id(self):
        r = assess()
        self.assertEqual(r["id"], "d2:patch-rule:9702:europa-moon-rocket-lead-from-gold")
        self.assertIn("bungie.net", r["source_url"])
        self.assertEqual(r["patch_date"], "2026-06-23")
        self.assertIn("not_live_verified", r["evidence_grade"])


if __name__ == "__main__":
    unittest.main()
