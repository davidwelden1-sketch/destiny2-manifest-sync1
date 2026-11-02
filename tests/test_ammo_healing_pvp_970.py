import unittest

from simulator.ammo_healing_pvp_970 import RULES, RULE_IDS, assess_ammo_healing_pvp_970


EVENTS = {
    "heavy_precision_linear_base_brick": "heavy_precision_linear_brick",
    "heavy_precision_linear_enhanced_brick": "heavy_precision_linear_brick",
    "special_precision_linear_base_brick": "special_precision_linear_brick",
    "special_precision_linear_enhanced_brick": "special_precision_linear_brick",
    "rapid_fire_machine_gun_crate": "rapid_fire_machine_gun_crate_pickup",
    "deimosuffusion_player_tick": "deimosuffusion_damage_tick_against_player",
    "superluminal_motion_moving_heal": "wayward_psyche_four_piece_moving",
    "superluminal_motion_pvp_unchanged": "wayward_psyche_four_piece_moving",
}


def assess(mechanic="heavy_precision_linear_base_brick", **changes):
    args = dict(mechanic=mechanic, guardian_class="hunter",
                activity="pvp" if mechanic in (
                    "rapid_fire_machine_gun_crate", "deimosuffusion_player_tick",
                    "superluminal_motion_pvp_unchanged") else "pve",
                event_kind=EVENTS[mechanic], observation_date="2026-11-02")
    args.update(changes)
    return assess_ammo_healing_pvp_970(**args)


class AmmoHealingPvp970Tests(unittest.TestCase):
    def test_pve_heavy_precision_linear_bricks(self):
        self.assertEqual(assess()["published_component_change"],
                         {"ammo_before": 3, "ammo_after": 5, "brick_type": "base"})
        self.assertEqual(assess("heavy_precision_linear_enhanced_brick")[
            "published_component_change"], {"ammo_before": 4, "ammo_after": 6, "brick_type": "enhanced"})

    def test_pve_special_precision_linear_bricks(self):
        self.assertEqual(assess("special_precision_linear_base_brick")[
            "published_component_change"]["ammo_after"], 5)
        self.assertEqual(assess("special_precision_linear_enhanced_brick")[
            "published_component_change"], {"ammo_before": 6, "ammo_after": 10, "brick_type": "enhanced"})

    def test_pvp_machine_gun_ammo_is_maximum_not_guarantee(self):
        r = assess("rapid_fire_machine_gun_crate")
        self.assertEqual(r["published_component_change"]["maximum_ammo_after"], 62)
        self.assertTrue(r["published_component_change"]["magazine_dependent"])
        self.assertIsNone(r["ammo_drop_rate_measured"])
        self.assertIsNone(r["pvp_guardian_ttk_measured"])

    def test_pvp_deimosuffusion_spacing_not_ttk(self):
        r = assess("deimosuffusion_player_tick")
        self.assertEqual(r["published_component_change"], {
            "seconds_between_ticks_before": 0.1, "seconds_between_ticks_after": 0.3})
        self.assertIsNone(r["pvp_damage_per_tick_measured"])
        self.assertIsNone(r["pvp_guardian_ttk_measured"])

    def test_pve_wayward_psyche_heal_component_not_uptime(self):
        r = assess("superluminal_motion_moving_heal")
        self.assertEqual(r["published_component_change"]["health_per_second_after"], 30)
        self.assertIsNone(r["pve_healing_uptime_measured"])
        self.assertIsNone(r["pve_damage_resistance_measured"])

    def test_pvp_wayward_psyche_unchanged_not_numeric(self):
        r = assess("superluminal_motion_pvp_unchanged")
        self.assertEqual(r["published_component_change"], {"pvp_performance_unchanged": True})
        self.assertNotIn("health_per_second_after", r["published_component_change"])

    def test_activity_isolation(self):
        self.assertFalse(assess("deimosuffusion_player_tick", activity="pve")[
            "official_historical_rule_applicable"])
        self.assertFalse(assess("superluminal_motion_moving_heal", activity="pvp")[
            "official_historical_rule_applicable"])
        self.assertFalse(assess("heavy_precision_linear_base_brick", activity="trials")[
            "official_historical_rule_applicable"])

    def test_all_classes_and_artifact_disabled_modes(self):
        for cls in ("hunter", "titan", "warlock"):
            for mode in ("pvp", "competitive", "trials"):
                r = assess("rapid_fire_machine_gun_crate", guardian_class=cls, activity=mode)
                self.assertTrue(r["official_historical_rule_applicable"])
                self.assertEqual(r["artifact_effects_active"],
                                 False if mode != "pvp" else None)
                self.assertFalse(r["current_artifact_allocation_verified"])

    def test_prepatch_and_patch_day_fail_closed(self):
        for day in ("2026-06-08", "2026-06-09"):
            self.assertFalse(assess(observation_date=day)[
                "official_historical_rule_applicable"])

    def test_mismatched_patch_and_event_fail_closed(self):
        self.assertEqual(assess(source_patch_version="9.7.0.2")["status"],
                         "source_patch_version_mismatch")
        self.assertFalse(assess(event_kind="weapon_final_blow")[
            "official_historical_rule_applicable"])

    def test_artifact_limits(self):
        r = assess(artifact_name="unknown", artifact_perks=tuple("abcdefg"))
        self.assertEqual(len(r["selected_artifact_perks"]), 7)
        for bad in (
            {"artifact_perks": ("x",)},
            {"artifact_name": "x", "artifact_perks": tuple("abcdefgh")},
            {"artifact_name": "x", "artifact_perks": ("a", "a")},
            {"artifact_name": "x", "artifact_perks": "a"},
            {"artifact_name": "x", "artifact_perks": ("a", 1)},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_invalid_metadata_fails_closed(self):
        for bad in (
            {"guardian_class": "not_a_class"}, {"activity": "gambit"},
            {"event_kind": ""}, {"observation_date": "2026-6-9"},
            {"manifest_version": ""}, {"item_hash": True}, {"item_hash": -1},
            {"item_hash": 2**32}, {"source_patch_version": None},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess(**bad)

    def test_stable_provenance_and_no_gameplay_certification(self):
        self.assertEqual(len(RULE_IDS), len(set(RULE_IDS.values())))
        self.assertEqual(set(RULE_IDS), set(RULES))
        r = assess()
        self.assertEqual(r["source_date"], "2026-06-09")
        self.assertEqual(r["source_checked_at"], "2026-11-02")
        self.assertIn("bungie.net", r["source_url"])
        self.assertFalse(r["exact_item_hash_and_enhanced_perk_legality_verified"])
        self.assertIsNone(r["pve_boss_dps_measured"])

    def test_returned_payload_is_independent(self):
        a = assess()
        a["published_component_change"]["ammo_after"] = 999
        self.assertEqual(assess()["published_component_change"]["ammo_after"], 5)


if __name__ == "__main__":
    unittest.main()
