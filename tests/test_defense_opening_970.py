"""Regression tests use Bungie's patch statements and synthetic examples only."""
import unittest

from simulator.defense_opening_970 import assess_defense_970


def assess(**changes):
    args = dict(mechanic="frost_armor", guardian_class="hunter", activity="pve",
                observation_date="2026-11-02", event_kind="frost_armor_active",
                frost_stacks=5)
    args.update(changes)
    return assess_defense_970(**args)


class DefenseOpening970Tests(unittest.TestCase):
    def test_five_stacks_pve_is_approximate_anchor(self):
        r = assess()
        self.assertTrue(r["source_supported_candidate"])
        self.assertEqual(r["published_pve_dr_approx"], 0.35)
        self.assertAlmostEqual(r["illustrative_single_source_ehp_multiplier"], 1 / 0.65)
        self.assertIsNone(r["measured_pve_damage_resistance"])

    def test_rime_seven_stacks_has_separate_anchor(self):
        r = assess(frost_stacks=7, whisper_of_rime=True)
        self.assertEqual(r["published_pve_dr_approx"], 0.50)
        self.assertEqual(r["illustrative_single_source_ehp_multiplier"], 2.0)

    def test_six_and_four_stacks_not_interpolated(self):
        for stacks, rime in ((4, False), (6, True)):
            with self.subTest(stacks=stacks):
                r = assess(frost_stacks=stacks, whisper_of_rime=rime)
                self.assertTrue(r["source_supported_candidate"])
                self.assertIsNone(r["published_pve_dr_approx"])

    def test_seven_without_rime_is_not_legal_stack_claim(self):
        r = assess(frost_stacks=7, whisper_of_rime=False)
        self.assertFalse(r["source_supported_candidate"])
        self.assertIsNone(r["published_pve_dr_approx"])

    def test_no_pvp_dr_values_inferred_from_pve_anchors(self):
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = assess(activity=mode, frost_stacks=7, whisper_of_rime=True)
                self.assertIsNone(r["published_pve_dr_approx"])
                self.assertIsNone(r["illustrative_single_source_ehp_multiplier"])
                self.assertIsNone(r["measured_pvp_ttk"])

    def test_no_backup_plans_requires_titan_final_blow_and_active_buff(self):
        base = dict(mechanic="no_backup_plans", guardian_class="titan",
                    event_kind="shotgun_final_blow", frost_stacks=None,
                    active_defensive_buff="woven_mail")
        self.assertTrue(assess(**base)["source_supported_candidate"])
        self.assertTrue(assess(**{**base, "event_kind": "melee_final_blow"})["source_supported_candidate"])
        self.assertFalse(assess(**{**base, "guardian_class": "hunter"})["source_supported_candidate"])
        self.assertFalse(assess(**{**base, "event_kind": "other"})["source_supported_candidate"])
        self.assertFalse(assess(**{**base, "active_defensive_buff": None})["source_supported_candidate"])

    def test_no_backup_plans_buff_list_is_explicit(self):
        for buff in ("void_overshield", "restoration", "amplified", "frost_armor", "woven_mail"):
            with self.subTest(buff=buff):
                r = assess(mechanic="no_backup_plans", guardian_class="titan",
                           event_kind="melee_final_blow", active_defensive_buff=buff)
                self.assertTrue(r["source_supported_candidate"])
                self.assertIsNone(r["measured_cooldown_or_buff_uptime"])
                self.assertFalse(r["live_runtime_activation_verified"])

    def test_smoke_jumper_40_percent_is_max_not_live_dr(self):
        r = assess(mechanic="smoke_jumper", event_kind="set_bonus_active")
        self.assertTrue(r["source_supported_candidate"])
        self.assertEqual(r["published_pve_max_dr_cap"], 0.40)
        self.assertIsNone(r["published_pve_dr_approx"])
        self.assertFalse(r["armor_set_ownership_verified"])
        self.assertIsNone(r["measured_pve_damage_resistance"])

    def test_smoke_jumper_not_assumed_active_in_pvp(self):
        r = assess(mechanic="smoke_jumper", event_kind="set_bonus_active", activity="pvp")
        self.assertIsNone(r["published_pve_max_dr_cap"])
        self.assertIsNone(r["measured_pvp_guardian_damage"])

    def test_pvp_multicharge_starts_at_one_not_all(self):
        for mode in ("pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                r = assess(mechanic="pvp_multicharge", activity=mode,
                           event_kind="match_start", ability_max_charges=3)
                self.assertTrue(r["source_supported_candidate"])
                self.assertEqual(r["published_pvp_match_start_charges"], 1)

    def test_multicharge_pve_and_single_charge_are_not_pvp_claims(self):
        base = dict(mechanic="pvp_multicharge", event_kind="match_start",
                    ability_max_charges=2)
        self.assertFalse(assess(**base)["source_supported_candidate"])
        self.assertFalse(assess(**{**base, "activity": "pvp",
                                    "ability_max_charges": 1})["source_supported_candidate"])
        self.assertFalse(assess(**{**base, "activity": "pvp",
                                    "event_kind": "other"})["source_supported_candidate"])

    def test_prepatch_never_promotes_source_candidate(self):
        r = assess(observation_date="2026-06-08")
        self.assertFalse(r["source_supported_candidate"])
        self.assertIsNone(r["published_pve_dr_approx"])
        self.assertTrue(assess(observation_date="2026-06-09")["source_supported_candidate"])

    def test_artifact_mode_and_selection_safety(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            r = assess(activity=mode, artifact_name="Unverified", artifact_perks=("A",))
            self.assertIs(r["artifact_effects_active"],
                          False if mode in ("competitive", "trials") else None)
            self.assertFalse(r["current_artifact_allocation_verified"])
        for bad in ({"artifact_perks": ("A",)},
                    {"artifact_name": "X", "artifact_perks": ("A", "A")},
                    {"artifact_name": "X", "artifact_perks": tuple(str(x) for x in range(8))},
                    {"artifact_name": "X", "artifact_perks": "A"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_invalid_metadata_rejected(self):
        for bad in ({"mechanic": "unknown"}, {"guardian_class": "other"},
                    {"activity": "raid"}, {"event_kind": "unknown"},
                    {"observation_date": "2026-6-9"}, {"observation_date": "2026-02-30"},
                    {"frost_stacks": True}, {"frost_stacks": 8},
                    {"whisper_of_rime": 1}, {"ability_max_charges": True},
                    {"active_defensive_buff": "unknown"}, {"manifest_version": ""},
                    {"artifact_name": ""}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_stable_id_provenance_and_no_certification(self):
        r = assess(manifest_version="test-version")
        self.assertEqual(r["id"], "d2:patch-rule:970:defense:frost_armor")
        self.assertEqual(r["patch_version"], "9.7.0")
        self.assertEqual(r["patch_date"], "2026-06-09")
        self.assertEqual(r["manifest_version"], "test-version")
        self.assertIn("bungie.net", r["source_url"])
        self.assertFalse(r["certified_for_app_build_recommendation"])
        self.assertFalse(r["pve_stacking_with_other_sources_verified"])
        self.assertIsNone(r["measured_pve_boss_dps"])
        self.assertIsNone(r["measured_pvp_ttk"])


if __name__ == "__main__":
    unittest.main()
