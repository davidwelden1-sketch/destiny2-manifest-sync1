"""Synthetic regressions for historical Anarchy/Divinity patch evidence."""
import unittest

from simulator.patch_970_exotic_trap_evidence import RULES, audit_exotic_mechanic


def audit(weapon="anarchy", mechanic="armed_trap_lifetime_seconds", **kw):
    args = dict(weapon=weapon, mechanic=mechanic, activity="pve",
                observation_date="2026-06-10")
    args.update(kw)
    return audit_exotic_mechanic(**args)


class ExoticTrapEvidenceTests(unittest.TestCase):
    def test_anarchy_trap_lifetime_is_10_to_15_not_15_extra(self):
        r = audit()
        self.assertEqual((r["historical_previous"], r["historical_post_patch"]), (10, 15))
        self.assertIsNone(r["historical_relative_factor"])

    def test_anarchy_combatant_damage_changes_are_distinct(self):
        for mechanic, expected in (
            ("trap_damage_vs_combatants_factor", 1.30),
            ("detonation_damage_vs_combatants_factor", 2.0),
        ):
            with self.subTest(mechanic=mechanic):
                r = audit(mechanic=mechanic)
                self.assertAlmostEqual(r["historical_relative_factor"], expected)
                self.assertIsNone(r["boss_dps"])
                self.assertIsNone(r["damage_per_tick"])

    def test_anarchy_trait_replacement_is_not_random_roll(self):
        r = audit(mechanic="trait_replacement")
        self.assertEqual(r["historical_previous"], "Moving Target")
        self.assertEqual(r["historical_post_patch"], "Impromptu Ammunition")
        self.assertFalse(r["current_roll_certified"])

    def test_divinity_penance_damage_relative_not_dps(self):
        r = audit(weapon="divinity", mechanic="penance_damage_factor")
        self.assertEqual(r["historical_relative_factor"], 1.20)
        self.assertIsNone(r["boss_dps"])

    def test_divinity_activation_time(self):
        r = audit(weapon="divinity", mechanic="penance_activation_seconds")
        self.assertEqual((r["historical_previous"], r["historical_post_patch"]), (4, 3))

    def test_divinity_cage_shots(self):
        r = audit(weapon="divinity", mechanic="cage_activation_shots")
        self.assertEqual((r["historical_previous"], r["historical_post_patch"]), (14, 10))

    def test_pvp_has_no_imported_pve_damage_or_ttk(self):
        for mode in ("pvp", "competitive", "trials"):
            for weapon, mechanic in (
                ("anarchy", "trap_damage_vs_combatants_factor"),
                ("divinity", "penance_damage_factor"),
            ):
                with self.subTest(mode=mode, weapon=weapon):
                    r = audit(weapon=weapon, mechanic=mechanic, activity=mode)
                    self.assertEqual(r["status"], "pvp_application_not_established")
                    self.assertIsNone(r["historical_relative_factor"])
                    self.assertIsNone(r["guardian_ttk"])
                    self.assertIs(r["artifact_enabled"], False if mode != "pvp" else None)

    def test_freshness_pre_patch_patch_day_and_mismatch(self):
        for change, expected in (
            ({"observation_date": "2026-06-08"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-09"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.6"}, "source_patch_version_mismatch"),
            ({"reference_baseline": "post_9_7_0"}, "not_a_pre_patch_reference"),
            ({"reference_baseline": "unknown"}, "not_a_pre_patch_reference"),
        ):
            with self.subTest(change=change):
                r = audit(**change)
                self.assertEqual(r["status"], expected)
                self.assertIsNone(r["historical_post_patch"])

    def test_no_current_measurement_or_artifact_certification(self):
        for weapon, mechanics in RULES.items():
            for mechanic in mechanics:
                with self.subTest(weapon=weapon, mechanic=mechanic):
                    r = audit(weapon=weapon, mechanic=mechanic)
                    self.assertFalse(r["gameplay_measured"])
                    self.assertFalse(r["damage_ownership_measured"])
                    self.assertFalse(r["current_artifact_selection_verified"])
                    self.assertFalse(r["exact_item_hash_verified"])
                    self.assertFalse(r["current_game_verified"])

    def test_bad_inputs_rejected(self):
        for change in (
            {"weapon": "unknown"}, {"mechanic": "imaginary"},
            {"activity": "gambit"}, {"reference_baseline": "latest"},
            {"observation_date": "2026-02-30"},
            {"observation_date": "2026-6-10"}, {"observation_date": None},
            {"source_patch_version": ""}, {"weapon": True},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                audit(**change)


if __name__ == "__main__":
    unittest.main()
