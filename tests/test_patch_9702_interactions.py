import unittest
from simulator.patch_9702_interactions import assess_patch_9702_interaction


def assess(**changes):
    params = dict(interaction_id="ergo_sum_vortex_heavy", guardian_class="titan",
                  activity="pve", observation_date="2026-11-01")
    params.update(changes)
    return assess_patch_9702_interaction(**params)


class Patch9702InteractionTests(unittest.TestCase):
    def test_ergo_sum_vortex_ammo_patch_not_dps(self):
        for cls in ("hunter", "titan", "warlock"):
            for activity in ("pve", "pvp", "competitive", "trials"):
                with self.subTest(cls=cls, activity=activity):
                    r = assess(guardian_class=cls, activity=activity)
                    self.assertEqual(r["ergo_sum_vortex_heavy_ammo_cost_official"], 4)
                    self.assertEqual(r["ergo_sum_vortex_pre_fix_cost_official"], 6)
                    self.assertIsNone(r["measured_pve_dps"])
                    self.assertIsNone(r["measured_pvp_ttk"])

    def test_hierarchy_guidance_guardian_only(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            r = assess(interaction_id="hierarchy_precision_guidance", activity=activity)
            self.assertEqual(r["hierarchy_precision_guardian_guidance_fixed"],
                             True if activity != "pve" else None)
            self.assertIsNone(r["ergo_sum_vortex_heavy_ammo_cost_official"])
            self.assertEqual(r["post_patch_scope"], activity != "pve")

    def test_lethal_current_hunter_only_and_pvp_only(self):
        for cls in ("hunter", "titan", "warlock"):
            for activity in ("pve", "pvp", "competitive", "trials"):
                r = assess(interaction_id="hunter_lethal_current_multi_activation",
                           guardian_class=cls, activity=activity)
                expected = cls == "hunter" and activity != "pve"
                self.assertEqual(r["lethal_current_multi_activation_pvp_one_shot_bug_fixed"],
                                 True if expected else None)
                self.assertEqual(r["post_patch_scope"], expected)

    def test_prepatch_does_not_project_fixes_backwards(self):
        for interaction in ("ergo_sum_vortex_heavy", "hierarchy_precision_guidance",
                            "hunter_lethal_current_multi_activation"):
            r = assess(interaction_id=interaction, guardian_class="hunter",
                       activity="pvp", observation_date="2026-06-22")
            self.assertFalse(r["post_patch_scope"])
            self.assertIsNone(r["ergo_sum_vortex_heavy_ammo_cost_official"])
            self.assertIsNone(r["hierarchy_precision_guardian_guidance_fixed"])
            self.assertIsNone(r["lethal_current_multi_activation_pvp_one_shot_bug_fixed"])

    def test_patch_boundary(self):
        self.assertIsNone(assess(observation_date="2026-06-22")["ergo_sum_vortex_heavy_ammo_cost_official"])
        self.assertEqual(assess(observation_date="2026-06-23")["ergo_sum_vortex_heavy_ammo_cost_official"], 4)

    def test_artifact_disabled_in_competitive_and_trials(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            r = assess(activity=activity, artifact_name="Example Artifact", artifact_perks=("Example Perk",))
            self.assertIs(r["artifact_effects_active"], False if activity in ("competitive", "trials") else None)
            self.assertFalse(r["artifact_allocation_legal_verified"])

    def test_artifact_invalid_allocations_fail_closed(self):
        for changes in ({"artifact_perks": ("A",)},
                        {"artifact_name": "A", "artifact_perks": ("B", "B")},
                        {"artifact_name": "A", "artifact_perks": tuple(map(str, range(8)))},
                        {"artifact_name": ""}, {"artifact_name": "A", "artifact_perks": (None,)},
                        {"artifact_name": "A", "artifact_perks": "AB"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                assess(**changes)

    def test_metadata_validation(self):
        for changes in ({"interaction_id": "unknown"}, {"guardian_class": "any"},
                        {"activity": "raid"}, {"observation_date": "2026-6-23"},
                        {"observation_date": "2026-02-30"}, {"item_hash": True},
                        {"item_hash": -1}, {"item_hash": 2**32},
                        {"manifest_version": ""}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                assess(**changes)

    def test_provenance_and_exact_hash_uncertainty(self):
        r = assess(item_hash=123456, manifest_version="test-version")
        self.assertEqual(r["id"], "d2:patch-rule:9702:ergo_sum_vortex_heavy")
        self.assertEqual(r["patch_version"], "9.7.0.2")
        self.assertEqual(r["patch_date"], "2026-06-23")
        self.assertEqual(r["source_url"],
                         "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2")
        self.assertEqual(r["item_hash_reported_by_caller"], 123456)
        self.assertFalse(r["item_hash_identity_verified"])
        self.assertFalse(r["current_acquisition_verified"])
        self.assertFalse(r["enhanced_perk_legality_verified"])
        self.assertFalse(r["current_runtime_verified"])


if __name__ == "__main__":
    unittest.main()
