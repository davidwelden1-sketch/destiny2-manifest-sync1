"""Synthetic regressions for dated Bungie 9.7.0.2 changes, not gameplay."""
import unittest

from simulator.patch_9702_ammo_armor_evidence import RULES, audit_patch_9702


def audit(mechanic="kings_fall_special_ammo_progress_bonus", **kwargs):
    data = dict(mechanic=mechanic, activity="pve",
                observation_date="2026-06-24")
    data.update(kwargs)
    return audit_patch_9702(**data)


class Patch9702EvidenceTests(unittest.TestCase):
    def test_kings_fall_special_nerf_is_to_bonus_not_total_progress(self):
        r = audit()
        self.assertEqual((r["historical_previous"], r["historical_post_patch"]), (1.0, 0.30))
        self.assertEqual(r["unit"], "fraction_of_old_bonus_not_total_progress")
        self.assertIsNone(r["total_ammo_meter_progress"])

    def test_kings_fall_heavy_nerf_is_to_bonus_not_total_progress(self):
        r = audit("kings_fall_heavy_ammo_progress_bonus")
        self.assertEqual(r["historical_post_patch"], 0.25)
        self.assertIsNone(r["boss_dps"])

    def test_ergo_sum_vortex_cost_fixed_to_four(self):
        r = audit("ergo_sum_vortex_heavy_attack_ammo_cost")
        self.assertEqual((r["historical_previous"], r["historical_post_patch"]), (6, 4))
        self.assertFalse(r["current_weapon_hash_verified"])

    def test_truth_reserves_not_damage(self):
        r = audit("truth_maximum_ammo_reserves")
        self.assertEqual((r["historical_previous"], r["historical_post_patch"]), (14, 10))
        self.assertIsNone(r["boss_dps"])

    def test_hierarchy_guidance_is_pvp_only_and_unquantified(self):
        r = audit("hierarchy_precision_player_guidance", activity="pvp")
        self.assertIs(r["historical_post_patch"], True)
        self.assertIsNone(r["guidance_energy_per_precision_hit"])
        self.assertIsNone(r["guardian_ttk"])

    def test_frostees_pvp_reduction_is_not_a_number(self):
        r = audit("frostees_pvp_frost_armor_generation", activity="pvp")
        self.assertEqual(r["historical_post_patch"], "reduced_amount_unspecified")
        self.assertIsNone(r["frost_armor_generation_rate"])

    def test_ex_diris_mothkeeper_charge_condition_removed(self):
        r = audit("ex_diris_mothkeeper_requires_active_moth_charge")
        self.assertIs(r["historical_previous"], True)
        self.assertIs(r["historical_post_patch"], False)
        self.assertIsNone(r["damage_ownership"])

    def test_no_pve_to_pvp_or_pvp_to_pve_transfer(self):
        for mechanic, mode in (
            ("kings_fall_special_ammo_progress_bonus", "pvp"),
            ("ergo_sum_vortex_heavy_attack_ammo_cost", "trials"),
            ("hierarchy_precision_player_guidance", "pve"),
            ("frostees_pvp_frost_armor_generation", "pve"),
        ):
            with self.subTest(mechanic=mechanic, mode=mode):
                r = audit(mechanic, activity=mode)
                self.assertEqual(r["status"], "cross_mode_transfer_not_supported")
                self.assertIsNone(r["historical_post_patch"])

    def test_competitive_and_trials_disable_artifact_even_on_pvp_fact(self):
        for mode in ("competitive", "trials"):
            r = audit("hierarchy_precision_player_guidance", activity=mode)
            self.assertIs(r["artifact_effects_enabled"], False)
            self.assertIsNone(r["guardian_ttk"])

    def test_pre_patch_patch_day_and_source_mismatch(self):
        for kw, expected in (
            ({"observation_date": "2026-06-22"}, "pre_patch_observation_requires_revalidation"),
            ({"observation_date": "2026-06-23"}, "patch_day_deployment_time_unknown"),
            ({"source_patch_version": "9.7.0.3"}, "source_patch_version_mismatch"),
        ):
            with self.subTest(kw=kw):
                r = audit(**kw)
                self.assertEqual(r["status"], expected)
                self.assertIsNone(r["historical_post_patch"])

    def test_reject_invalid_inputs(self):
        for kw in (
            {"mechanic": "fake"}, {"mechanic": True},
            {"activity": []}, {"activity": "gambit"},
            {"observation_date": "2026-02-30"},
            {"observation_date": "2026-6-24"},
            {"observation_date": None},
            {"source_patch_version": ""},
        ):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                audit(**kw)

    def test_all_facts_explicitly_uncertified(self):
        for mechanic, (scope, _, _, _) in RULES.items():
            with self.subTest(mechanic=mechanic):
                r = audit(mechanic, activity="pve" if scope == "pve" else "pvp")
                self.assertFalse(r["gameplay_measured"])
                self.assertFalse(r["current_artifact_selection_verified"])
                self.assertFalse(r["enhanced_perk_legality_verified"])
                self.assertIsNone(r["boss_dps"])
                self.assertIsNone(r["guardian_ttk"])


if __name__ == "__main__":
    unittest.main()
