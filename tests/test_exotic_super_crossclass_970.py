import unittest

from simulator.exotic_super_crossclass_970 import (
    RULES, assess_exotic_super_970,
)


def assess(**changes):
    args = {
        "mechanic": "shards_of_galanor",
        "guardian_class": "hunter",
        "activity": "pve",
        "event_kind": "blade_barrage_most_knives_land",
        "observation_date": "2026-11-02",
    }
    args.update(changes)
    return assess_exotic_super_970(**args)


class ExoticSuperCrossclass970Tests(unittest.TestCase):
    def test_hunter_shards_explosion_not_boss_dps(self):
        result = assess()
        self.assertTrue(result["official_historical_rule_applicable"])
        self.assertTrue(result["published_component_change"]["delayed_solar_explosion"])
        self.assertIsNone(result["published_component_change"]["minimum_knives_required"])
        self.assertIsNone(result["pve_boss_dps_measured"])

    def test_titan_pyrogale_explosion_component_not_total_super(self):
        result = assess(mechanic="pyrogale_gauntlets",
                        guardian_class="titan",
                        event_kind="super_cyclone_explosion")
        self.assertEqual(result["published_component_change"][
            "explosion_damage_relative_to_prepatch"], 1.10)
        self.assertIsNone(result["pve_boss_dps_measured"])
        self.assertFalse(result["effect_stacking_verified"])

    def test_titan_ward_core_has_two_relocations_not_three(self):
        args = dict(mechanic="ward_of_dawn_core", guardian_class="titan",
                    event_kind="ward_core_relocation")
        for count in (0, 1, 2):
            result = assess(**args, relocation_count=count)
            self.assertTrue(result["official_historical_rule_applicable"])
            self.assertEqual(result["published_component_change"][
                "maximum_core_relocations"], 2)
        result = assess(**args, relocation_count=3)
        self.assertEqual(result["status"], "exceeds_official_ward_relocation_limit")
        self.assertIsNone(result["published_component_change"])

    def test_warlock_astrocyte_blink_is_not_guardian_ttk(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            result = assess(mechanic="astrocyte_verse",
                            guardian_class="warlock", activity=activity,
                            event_kind="blink_or_dark_blink")
            self.assertTrue(result["official_historical_rule_applicable"])
            self.assertTrue(result["published_component_change"][
                "blink_grants_volatile_rounds"])
            self.assertIsNone(result["pvp_guardian_ttk_measured"])
            self.assertFalse(result["mode_applicability_verified"])
            self.assertEqual(result["artifact_effects_active"],
                             False if activity in ("competitive", "trials") else None)

    def test_all_class_mismatches_fail_closed(self):
        for mechanic, expected_class, event in (
            ("shards_of_galanor", "hunter", "blade_barrage_most_knives_land"),
            ("pyrogale_gauntlets", "titan", "super_cyclone_explosion"),
            ("ward_of_dawn_core", "titan", "ward_core_relocation"),
            ("astrocyte_verse", "warlock", "blink_or_dark_blink"),
        ):
            for cls in {"hunter", "titan", "warlock"} - {expected_class}:
                result = assess(mechanic=mechanic, guardian_class=cls,
                                event_kind=event)
                self.assertEqual(result["status"], "class_not_supported")
                self.assertIsNone(result["published_component_change"])

    def test_wrong_event_cannot_activate(self):
        self.assertEqual(assess(event_kind="weapon_final_blow")["status"],
                         "trigger_not_established")

    def test_prepatch_and_deployment_day_uncertain(self):
        for day, status in (
            ("2026-06-08", "pre_patch"),
            ("2026-06-09", "patch_day_deployment_time_unknown"),
        ):
            result = assess(observation_date=day)
            self.assertEqual(result["status"], status)
            self.assertFalse(result["official_historical_rule_applicable"])

    def test_wrong_source_patch_rejected(self):
        result = assess(source_patch_version="9.7.0.2")
        self.assertEqual(result["status"], "source_patch_version_mismatch")
        self.assertIsNone(result["published_component_change"])

    def test_artifact_constraints_and_competitive_disable(self):
        result = assess(activity="competitive", artifact_name="unverified",
                        artifact_perks=tuple("abcdefg"))
        self.assertFalse(result["artifact_effects_active"])
        self.assertFalse(result["current_artifact_allocation_verified"])
        for bad in (
            {"artifact_perks": ("a",)},
            {"artifact_name": "x", "artifact_perks": ("a", "a")},
            {"artifact_name": "x", "artifact_perks": tuple("abcdefgh")},
            {"artifact_name": "x", "artifact_perks": "abc"},
            {"artifact_name": "x", "artifact_perks": ("a", 2)},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_invalid_metadata_rejected(self):
        for bad in (
            {"mechanic": "missing"}, {"guardian_class": None},
            {"activity": "unknown"}, {"event_kind": []},
            {"observation_date": "2026-6-9"}, {"observation_date": True},
            {"source_patch_version": ""}, {"manifest_version": ""},
            {"item_hash": True}, {"item_hash": -1}, {"item_hash": 2**32},
            {"artifact_name": ""}, {"relocation_count": 1},
            {"mechanic": "ward_of_dawn_core", "relocation_count": True},
            {"mechanic": "ward_of_dawn_core", "relocation_count": -1},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_stable_ids_provenance_and_confidence(self):
        ids = [rule["id"] for rule in RULES.values()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(x.startswith("d2:patch-rule:970:") for x in ids))
        result = assess()
        self.assertEqual(result["patch_version"], "9.7.0")
        self.assertEqual(result["source_date"], "2026-06-09")
        self.assertEqual(result["source_checked_at"], "2026-11-02")
        self.assertIn("bungie.net", result["source_url"])
        self.assertEqual(result["evidence_grade"],
                         "official_historical_patch_not_gameplay_measured")

    def test_output_isolation_and_no_app_certification(self):
        first = assess()
        first["published_component_change"]["delayed_solar_explosion"] = False
        second = assess()
        self.assertTrue(second["published_component_change"]["delayed_solar_explosion"])
        self.assertFalse(second["certified_for_app_build_recommendation"])
        self.assertFalse(second["current_runtime_verified"])
        self.assertFalse(second["exact_item_hash_and_perk_legality_verified"])
        self.assertIsNone(second["pve_damage_resistance_measured"])
        self.assertIsNone(second["ability_cooldown_or_uptime_measured"])


if __name__ == "__main__":
    unittest.main()
