import unittest

from simulator.crossbow_osteo_proc_gate_970 import assess_crossbow_osteo_catalyst


def assess(**overrides):
    data = dict(guardian_class="warlock", activity="pve",
                observation_date="2026-11-01",
                kill_source="crossbow_charged_bolts")
    data.update(overrides)
    return assess_crossbow_osteo_catalyst(**data)


class CrossbowOsteoProcGateTests(unittest.TestCase):
    def test_post_patch_charged_bolt_kill_not_catalyst_proc(self):
        result = assess()
        self.assertIs(result["osteo_catalyst_trigger_supported"], False)
        self.assertIn("official_patch", result["evidence_grade"])
        self.assertIsNone(result["measured_kill_attribution"])

    def test_pvp_does_not_import_pve_damage_or_procs(self):
        result = assess(activity="pvp", guardian_class="hunter")
        self.assertIs(result["osteo_catalyst_trigger_supported"], False)
        self.assertIsNone(result["measured_pvp_ttk"])
        self.assertIsNone(result["measured_pve_boss_dps"])

    def test_pre_patch_not_retroactively_classified(self):
        result = assess(observation_date="2026-06-08")
        self.assertIsNone(result["osteo_catalyst_trigger_supported"])

    def test_other_kill_source_does_not_infer_positive_proc(self):
        result = assess(kill_source="crossbow_other_kill")
        self.assertIsNone(result["osteo_catalyst_trigger_supported"])

    def test_competitive_trials_disable_artifact_effects(self):
        for mode in ("competitive", "trials"):
            with self.subTest(mode=mode):
                result = assess(activity=mode, artifact_name="Example Artifact",
                                artifact_perks=("Example perk",))
                self.assertIs(result["artifact_effects_active"], False)
                self.assertFalse(result["artifact_mode_eligible"])

    def test_artifact_perk_limit_and_duplicates(self):
        with self.assertRaises(ValueError):
            assess(artifact_name="One", artifact_perks=tuple(str(i) for i in range(8)))
        with self.assertRaises(ValueError):
            assess(artifact_name="One", artifact_perks=("A", "A"))
        with self.assertRaises(ValueError):
            assess(artifact_perks=("A",))

    def test_invalid_date_and_kill_source_fail_closed(self):
        for bad in ("2026-2-01", "2026-13-01", None):
            with self.subTest(date=bad), self.assertRaises(ValueError):
                assess(observation_date=bad)
        for bad in ("", None, 1):
            with self.subTest(source=bad), self.assertRaises(ValueError):
                assess(kill_source=bad)

    def test_all_classes_allowed_without_class_specific_proc_assumption(self):
        for guardian_class in ("hunter", "titan", "warlock"):
            with self.subTest(guardian_class=guardian_class):
                self.assertIs(assess(guardian_class=guardian_class)[
                    "osteo_catalyst_trigger_supported"], False)


if __name__ == "__main__":
    unittest.main()
