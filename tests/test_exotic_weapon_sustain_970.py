import unittest

from simulator.exotic_weapon_sustain_970 import (
    assess_exotic_weapon_970, official_prometheus_stack_delta,
)


def assess(**kwargs):
    args = {
        "weapon": "prometheus_lens",
        "guardian_class": "hunter",
        "activity": "pve",
        "event_kind": "scorch_trigger",
        "observation_date": "2026-11-02",
    }
    args.update(kwargs)
    return assess_exotic_weapon_970(**args)


class ExoticWeaponSustain970Tests(unittest.TestCase):
    def test_prometheus_official_maxima_not_ignitions(self):
        r = assess()
        self.assertTrue(r["official_historical_rule_applicable"])
        self.assertEqual(r["prepatch_parameters"], {
            "max_base_scorch_stacks": 10, "conditional_extra_stacks": 10})
        self.assertEqual(r["postpatch_parameters"], {
            "max_base_scorch_stacks": 20, "conditional_extra_stacks": 10})
        self.assertFalse(r["scorch_to_ignition_threshold_verified"])

    def test_prometheus_delta_is_not_a_damage_prediction(self):
        r = official_prometheus_stack_delta()
        self.assertEqual(r["published_max_base_stack_delta"], 10)
        self.assertEqual(r["published_max_if_conditional_applies_before"], 20)
        self.assertEqual(r["published_max_if_conditional_applies_after"], 30)
        self.assertTrue(r["published_conditional_extra_stacks_unchanged"])
        self.assertIsNone(r["measured_pve_dps"])
        self.assertIsNone(r["measured_pvp_ttk"])

    def test_slayer_ammo_deltas_and_unknown_reload_rate(self):
        r = assess(weapon="slayers_fang", event_kind="buff_active")
        self.assertEqual(r["postpatch_parameters"]["magazine_size_delta"], 2)
        self.assertEqual(r["postpatch_parameters"]["reserve_ammo_delta"], 10)
        self.assertTrue(r["postpatch_parameters"]["slow_self_reload_while_buff_active"])
        self.assertFalse(r["self_reload_rate_verified"])
        self.assertFalse(r["self_reload_while_stowed_verified"])

    def test_slayer_weapon_kill_does_not_prove_buff(self):
        r = assess(weapon="slayers_fang", event_kind="weapon_final_blow")
        self.assertFalse(r["official_historical_rule_applicable"])
        self.assertIsNone(r["postpatch_parameters"])

    def test_all_classes_and_modes_separate_pve_pvp_unknowns(self):
        for guardian_class in ("hunter", "titan", "warlock"):
            for activity in ("pve", "pvp", "competitive", "trials"):
                with self.subTest(guardian_class=guardian_class, activity=activity):
                    r = assess(guardian_class=guardian_class, activity=activity)
                    self.assertIsNone(r["measured_pve_boss_dps"])
                    self.assertIsNone(r["measured_pvp_guardian_ttk"])
                    self.assertIsNone(r["measured_pve_damage_resistance"])
                    self.assertEqual(r["artifact_effects_active"],
                                     False if activity in ("competitive", "trials") else None)

    def test_patch_day_and_prepatch_are_not_certified(self):
        for day in ("2026-06-08", "2026-06-09"):
            r = assess(observation_date=day)
            self.assertFalse(r["official_historical_rule_applicable"])
            self.assertIsNone(r["postpatch_parameters"])
        self.assertTrue(assess(observation_date="2026-06-10")[
            "official_historical_rule_applicable"])

    def test_unrelated_event_does_not_prove_trigger(self):
        for event in ("weapon_hit", "weapon_final_blow", "buff_active"):
            self.assertFalse(assess(event_kind=event)[
                "official_historical_rule_applicable"])

    def test_invalid_metadata_fails_closed(self):
        for change in (
            {"weapon": "unknown"}, {"guardian_class": []}, {"activity": []},
            {"event_kind": []}, {"event_kind": "other"},
            {"observation_date": "2026-6-9"}, {"observation_date": None},
            {"manifest_version": ""}, {"manifest_version": 2},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                assess(**change)

    def test_item_hash_is_input_not_legal_certification(self):
        r = assess(item_hash=2573900604, manifest_version="example-version")
        self.assertEqual(r["item_hash_input_unverified"], 2573900604)
        self.assertFalse(r["exact_item_hash_and_perk_legality_verified"])
        self.assertEqual(r["manifest_version"], "example-version")
        for value in (-1, True, 2**32, "123", 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                assess(item_hash=value)

    def test_artifact_allocation_restrictions(self):
        r = assess(artifact_name="candidate-unverified",
                   artifact_perks=tuple("abcdefg"))
        self.assertEqual(len(r["selected_artifact_perks"]), 7)
        self.assertFalse(r["current_artifact_allocation_verified"])
        for change in (
            {"artifact_perks": ("a",)},
            {"artifact_name": "candidate", "artifact_perks": ("a", "a")},
            {"artifact_name": "candidate", "artifact_perks": tuple("abcdefgh")},
            {"artifact_name": ""},
            {"artifact_name": "candidate", "artifact_perks": ["a", 1]},
            {"artifact_name": "candidate", "artifact_perks": "a"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                assess(**change)

    def test_provenance_and_stable_ids(self):
        a = assess()
        b = assess(weapon="slayers_fang", event_kind="buff_active")
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(a["patch_version"], "9.7.0")
        self.assertEqual(a["source_date"], "2026-06-09")
        self.assertIn("bungie.net", b["source_url"])
        self.assertEqual(a["evidence_grade"],
                         "official_historical_patch_not_gameplay_measured")

    def test_returned_dict_cannot_mutate_shared_rule(self):
        first = assess()
        first["postpatch_parameters"]["max_base_scorch_stacks"] = 999
        self.assertEqual(assess()["postpatch_parameters"]["max_base_scorch_stacks"], 20)


if __name__ == "__main__":
    unittest.main()
