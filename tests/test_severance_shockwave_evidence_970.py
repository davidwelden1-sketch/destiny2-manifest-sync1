import unittest

from simulator.severance_shockwave_evidence_970 import assess_severance_shockwave


def assess(**overrides):
    data = dict(guardian_class="titan", activity="pve",
                observation_date="2026-11-01",
                scenario="repeat_shockwave_combatant")
    data.update(overrides)
    return assess_severance_shockwave(**data)


class SeveranceShockwaveEvidenceTests(unittest.TestCase):
    def test_combatant_repeat_exclusion_removed_not_damage_guarantee(self):
        result = assess()
        self.assertEqual(result["official_patch_change"],
                         "short_interval_repeat_hit_exclusion_removed")
        self.assertIsNone(result["repeated_hit_damage_measured"])
        self.assertIsNone(result["shockwave_chain_count_measured"])

    def test_occlusion_relaxed_not_unlimited_cover_penetration(self):
        result = assess(scenario="occluded_combatant")
        self.assertEqual(result["official_patch_change"],
                         "occlusion_requirement_relaxed_not_removed")

    def test_disorientation_duration_unmeasured(self):
        result = assess(scenario="shockwave_disorient_combatant")
        self.assertIn("duration_unspecified", result["official_patch_change"])
        self.assertIsNone(result["disorient_duration_seconds_measured"])

    def test_pvp_guardian_hit_not_inferred_from_combatant_change(self):
        for activity in ("pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                result = assess(activity=activity, scenario="repeat_shockwave_guardian")
                self.assertIsNone(result["official_patch_change"])
                self.assertIsNone(result["measured_pvp_ttk"])

    def test_pvp_does_not_inherit_pve_combatant_patch(self):
        result = assess(activity="pvp")
        self.assertIsNone(result["official_patch_change"])
        self.assertIsNone(result["measured_pve_boss_dps"])

    def test_finisher_chain_and_weapon_kill_are_unresolved(self):
        for scenario in ("finisher_chain", "weapon_kill"):
            with self.subTest(scenario=scenario):
                result = assess(scenario=scenario)
                self.assertIsNone(result["official_patch_change"])
                self.assertIsNone(result["kill_attribution_measured"])

    def test_non_titan_classes_do_not_gain_titan_exotic(self):
        for guardian_class in ("hunter", "warlock"):
            with self.subTest(guardian_class=guardian_class):
                result = assess(guardian_class=guardian_class)
                self.assertFalse(result["exotic_class_eligible"])
                self.assertIsNone(result["official_patch_change"])

    def test_historical_prepatch_not_retroactively_credited(self):
        result = assess(observation_date="2026-06-08")
        self.assertIsNone(result["official_patch_change"])

    def test_competitive_trials_artifact_disabled(self):
        for activity in ("competitive", "trials"):
            with self.subTest(activity=activity):
                result = assess(activity=activity, artifact_name="Example",
                                artifact_perks=("A",))
                self.assertIs(result["artifact_effects_active"], False)
                self.assertFalse(result["artifact_mode_eligible"])

    def test_artifact_limit_and_uniqueness(self):
        for perks in (tuple(str(x) for x in range(8)), ("A", "A")):
            with self.assertRaises(ValueError):
                assess(artifact_name="Example", artifact_perks=perks)
        with self.assertRaises(ValueError):
            assess(artifact_perks=("A",))

    def test_invalid_inputs_fail_closed(self):
        for bad in ("2026-2-01", "2026-13-01", None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(observation_date=bad)
        for key, value in (("guardian_class", "wizard"),
                           ("activity", "gambit"),
                           ("scenario", "instant_double_dps")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                assess(**{key: value})

    def test_manifest_and_damage_not_certified(self):
        result = assess(manifest_version="245114.26.10.13.2000-1-bnet.66137")
        self.assertFalse(result["artifact_allocation_legal_verified"])
        self.assertFalse(result["weapon_roll_verified"])
        self.assertIsNone(result["damage_ownership_measured"])
        self.assertIsNone(result["measured_pve_boss_dps"])


if __name__ == "__main__":
    unittest.main()
