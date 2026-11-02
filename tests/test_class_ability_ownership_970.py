import unittest

from simulator.class_ability_ownership_970 import assess_class_ability_ownership


def assess(**updates):
    values = dict(aspect="trappers_ambush", guardian_class="hunter",
                  activity="pve", observation_date="2026-11-02",
                  event_kind="aspect_activation")
    values.update(updates)
    return assess_class_ability_ownership(**values)


class ClassAbilityOwnership970Tests(unittest.TestCase):
    def test_hunter_aspect_classification_all_modes(self):
        for aspect in ("trappers_ambush", "ascension", "ensnaring_slam"):
            for activity in ("pve", "pvp", "competitive", "trials"):
                with self.subTest(aspect=aspect, activity=activity):
                    r = assess(aspect=aspect, activity=activity)
                    self.assertEqual(r["event_source_classification"], "class_ability")
                    self.assertFalse(r["individual_perk_proc_verified"])
                    self.assertIsNone(r["measured_pvp_ttk"])

    def test_trappers_ambush_uses_class_energy_not_melee(self):
        self.assertEqual(assess()["class_ability_energy_pool_official"], "class_ability")
        for aspect in ("ascension", "ensnaring_slam"):
            self.assertIsNone(assess(aspect=aspect)["class_ability_energy_pool_official"])

    def test_weapon_final_blow_does_not_inherit_aspect_source(self):
        r = assess(event_kind="weapon_final_blow")
        self.assertEqual(r["event_source_classification"], "weapon")
        self.assertFalse(r["final_blow_attribution_verified"])

    def test_aspect_final_blow_attribution_not_assumed(self):
        r = assess(event_kind="aspect_final_blow")
        self.assertEqual(r["event_source_classification"], "class_ability")
        self.assertFalse(r["final_blow_attribution_verified"])

    def test_class_stat_threshold_is_conditional_not_multiplier(self):
        for aspect in ("trappers_ambush", "ascension"):
            self.assertIsNone(assess(aspect=aspect)["above_100_class_stat_scaling_described"])
            self.assertFalse(assess(aspect=aspect, class_stat=100)["above_100_class_stat_scaling_described"])
            self.assertTrue(assess(aspect=aspect, class_stat=150)["above_100_class_stat_scaling_described"])
        self.assertIsNone(assess(aspect="ensnaring_slam", class_stat=150)["above_100_class_stat_scaling_described"])

    def test_wrong_class_and_prepatch_fail_closed(self):
        for cls in ("titan", "warlock"):
            self.assertIsNone(assess(guardian_class=cls)["event_source_classification"])
        self.assertIsNone(assess(observation_date="2026-06-08")["event_source_classification"])
        self.assertEqual(assess(observation_date="2026-06-09")["event_source_classification"], "class_ability")

    def test_artifact_disabled_modes_and_seven_ceiling(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            r = assess(activity=activity, artifact_name="Example", artifact_perks=("A",))
            self.assertIs(r["artifact_effects_active"],
                          False if activity in ("competitive", "trials") else None)
            self.assertFalse(r["current_artifact_allocation_verified"])
        with self.assertRaises(ValueError):
            assess(artifact_name="Example", artifact_perks=tuple(str(i) for i in range(8)))

    def test_bad_metadata_fails_closed(self):
        invalid = ({"aspect": "other"}, {"guardian_class": "all"},
                   {"activity": "raid"}, {"event_kind": "unknown"},
                   {"observation_date": "2026-6-9"},
                   {"observation_date": "2026-02-30"},
                   {"class_stat": True}, {"class_stat": 201},
                   {"manifest_version": ""}, {"artifact_perks": ("A",)},
                   {"artifact_name": "Example", "artifact_perks": ("A", "A")},
                   {"artifact_name": "Example", "artifact_perks": "A"})
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                assess(**values)

    def test_provenance_and_uncertainty(self):
        r = assess(class_stat=150, manifest_version="test")
        self.assertEqual(r["id"], "d2:patch-rule:970:class-ability-ownership:trappers_ambush")
        self.assertEqual(r["patch_version"], "9.7.0")
        self.assertEqual(r["patch_date"], "2026-06-09")
        self.assertIn("destiny_update_9_7_0", r["source_url"])
        self.assertEqual(r["manifest_version"], "test")
        self.assertFalse(r["current_runtime_verified"])
        self.assertIsNone(r["measured_pve_dps"])
        self.assertIsNone(r["measured_pve_damage_resistance"])
        self.assertIsNone(r["measured_ability_cooldown"])


if __name__ == "__main__":
    unittest.main()
