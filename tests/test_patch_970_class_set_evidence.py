import unittest

from simulator.patch_970_class_set_evidence import (
    assess_patch_970_class_set, RULES,
)


def assess(**changes):
    args = {
        "mechanic": "pale_heart_two_piece",
        "guardian_class": "hunter",
        "activity": "pve",
        "event_kind": "stack_em_up_stack_gained",
        "observation_date": "2026-11-02",
    }
    args.update(changes)
    return assess_patch_970_class_set(**args)


class Patch970ClassSetEvidenceTests(unittest.TestCase):
    def test_pale_heart_flat_energy_but_unknown_amounts(self):
        r = assess()
        self.assertTrue(r["official_historical_rule_applicable"])
        self.assertTrue(r["published_component_change"]["flat_amounts_instead_of_multiplier"])
        self.assertIsNone(r["published_component_change"]["light_energy_per_stack"])
        self.assertIsNone(r["published_component_change"]["dark_energy_per_stack"])
        self.assertFalse(r["mode_applicability_verified"])
        self.assertFalse(r["set_bonus_activation_measured"])

    def test_pale_heart_wrong_trigger_not_certified(self):
        r = assess(event_kind="weapon_final_blow")
        self.assertFalse(r["official_historical_rule_applicable"])
        self.assertIsNone(r["published_component_change"])

    def test_scatter_pvp_chase_only(self):
        for activity in ("pvp", "competitive", "trials"):
            r = assess(mechanic="scatter_grenade_chase", activity=activity,
                       event_kind="scatter_seekers_chase_player")
            self.assertEqual(r["published_component_change"], {
                "chase_distance_relative_to_prepatch": 0.5})
            self.assertTrue(r["mode_applicability_verified"])
            self.assertIsNone(r["pvp_guardian_ttk_measured"])
            self.assertEqual(r["artifact_effects_active"],
                             False if activity in ("competitive", "trials") else None)
        r = assess(mechanic="scatter_grenade_chase", activity="pve",
                   event_kind="scatter_seekers_chase_player")
        self.assertFalse(r["official_historical_rule_applicable"])

    def test_scatter_perk_energy_component_not_total_cooldown(self):
        for activity in ("pve", "pvp"):
            r = assess(mechanic="scatter_grenade_perk_energy", activity=activity,
                       event_kind="scatter_grenade_receives_perk_energy")
            self.assertEqual(r["published_component_change"][
                "perk_energy_gain_relative_to_prepatch"], 0.875)
            self.assertIsNone(r["ability_cooldown_or_uptime_measured"])
            self.assertFalse(r["mode_applicability_verified"])

    def test_titan_combatant_melees_not_guardian_ttk(self):
        for mechanic, event in (
            ("hammer_strike_combatant", "hammer_strike_hits_combatant"),
            ("shield_bash_combatant", "shield_bash_hits_combatant"),
            ("seismic_strike_combatant", "seismic_strike_hits_combatant"),
        ):
            r = assess(mechanic=mechanic, event_kind=event,
                       guardian_class="titan")
            self.assertEqual(r["published_component_change"][
                "attack_damage_relative_to_prepatch"], 2.0)
            self.assertIsNone(r["pve_boss_dps_measured"])
            self.assertIsNone(r["melee_damage_measured"])
            for activity in ("pvp", "competitive", "trials"):
                self.assertFalse(assess(mechanic=mechanic, event_kind=event,
                                        guardian_class="titan", activity=activity)[
                    "official_historical_rule_applicable"])
            self.assertFalse(assess(mechanic=mechanic, event_kind=event,
                                    guardian_class="warlock")[
                "official_historical_rule_applicable"])

    def test_all_classes_are_candidates_not_loadout_certified(self):
        for cls in ("hunter", "titan", "warlock"):
            r = assess(guardian_class=cls)
            self.assertTrue(r["official_historical_rule_applicable"])
            self.assertFalse(r["current_artifact_allocation_verified"])
            self.assertFalse(r["exact_item_hash_and_enhanced_roll_legality_verified"])

    def test_prepatch_and_patch_day_not_certified(self):
        for mechanic, event, patch_day in (
            ("pale_heart_two_piece", "stack_em_up_stack_gained", "2026-06-23"),
            ("scatter_grenade_chase", "scatter_seekers_chase_player", "2026-06-09"),
        ):
            for day in ("2026-06-08", patch_day):
                r = assess(mechanic=mechanic, event_kind=event,
                           activity="pvp" if mechanic.startswith("scatter") else "pve",
                           observation_date=day)
                self.assertFalse(r["official_historical_rule_applicable"])

    def test_patch_source_version_mismatch(self):
        r = assess(source_patch_version="9.7.0")
        self.assertEqual(r["status"], "source_patch_version_mismatch")
        self.assertIsNone(r["published_component_change"])

    def test_artifact_seven_perk_ceiling_and_no_competitive_effects(self):
        r = assess(artifact_name="uncertified", artifact_perks=tuple("abcdefg"),
                   activity="competitive")
        self.assertEqual(len(r["selected_artifact_perks"]), 7)
        self.assertFalse(r["artifact_effects_active"])
        self.assertFalse(r["current_artifact_allocation_verified"])
        for bad in (
            {"artifact_perks": ("a",)},
            {"artifact_name": "x", "artifact_perks": ("a", "a")},
            {"artifact_name": "x", "artifact_perks": tuple("abcdefgh")},
            {"artifact_name": "x", "artifact_perks": "a"},
            {"artifact_name": "x", "artifact_perks": ("a", 5)},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_invalid_metadata_fails_closed(self):
        for bad in (
            {"mechanic": "not_real"}, {"guardian_class": []},
            {"activity": None}, {"event_kind": []}, {"event_kind": ""},
            {"observation_date": "2026-6-9"}, {"observation_date": None},
            {"manifest_version": ""}, {"manifest_version": 1},
            {"item_hash": True}, {"item_hash": -1},
            {"item_hash": 2**32}, {"artifact_name": ""},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_stable_ids_and_provenance(self):
        ids = {rule["id"] for rule in RULES.values()}
        self.assertEqual(len(ids), len(RULES))
        self.assertTrue(all(x.startswith("d2:patch-rule:") for x in ids))
        r = assess()
        self.assertEqual(r["patch_version"], "9.7.0.2")
        self.assertEqual(r["source_date"], "2026-06-23")
        self.assertEqual(r["source_checked_at"], "2026-11-02")
        self.assertIn("bungie.net", r["source_url"])

    def test_mutation_of_output_does_not_modify_rule(self):
        a = assess()
        a["published_component_change"]["flat_amounts_instead_of_multiplier"] = False
        self.assertTrue(assess()["published_component_change"][
            "flat_amounts_instead_of_multiplier"])


if __name__ == "__main__":
    unittest.main()
