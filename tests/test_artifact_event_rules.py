"""Synthetic historical rules tests; not in-game measurements."""
import unittest

from simulator.artifact_event_rules import (
    ARTIFACT_ID, kinetic_impacts_gl_screen, curative_orbs_tangle_screen,
)


class ArtifactEventRulesTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {ARTIFACT_ID: ["Kinetic Impacts", "Curative Orbs"]}

    def test_kinetic_impacts_gl_ammo_types_do_not_invent_damage(self):
        for ammo in ("primary", "special", "heavy"):
            with self.subTest(ammo=ammo):
                result = kinetic_impacts_gl_screen(
                    ammo, "grandmaster nightfall", ARTIFACT_ID,
                    ["Kinetic Impacts"], self.catalog)
                self.assertEqual(result["status"], "official_historical_gl_ammo_eligibility")
                self.assertIsNone(result["damage_multiplier"])
                self.assertFalse(result["certified"])
                self.assertFalse(result["current_artifact_verified"])
                self.assertEqual(
                    result["relative_shockwave_damage"],
                    "heavy_gl_reference" if ammo == "heavy" else "lower_than_heavy_gl")

    def test_pvp_trails_and_competitive_artifact_block(self):
        for mode in ("Trials of Osiris", "Competitive Crucible"):
            result = kinetic_impacts_gl_screen(
                "special", mode, ARTIFACT_ID, ["Kinetic Impacts"], self.catalog)
            self.assertEqual(result["status"], "artifact_selection_blocked")
            self.assertEqual(result["reason"], "artifact_disabled_activity")

    def test_single_artifact_and_selected_perk_required(self):
        self.assertEqual(
            kinetic_impacts_gl_screen("heavy", "control", "Other",
                                      ["Kinetic Impacts"], {"Other": ["Kinetic Impacts"]})["status"],
            "artifact_identity_mismatch")
        self.assertEqual(
            kinetic_impacts_gl_screen("heavy", "control", ARTIFACT_ID,
                                      ["Curative Orbs"], self.catalog)["status"],
            "perk_not_selected")
        self.assertEqual(
            kinetic_impacts_gl_screen("heavy", "control", ARTIFACT_ID,
                                      ["Kinetic Impacts", "Other"], self.catalog)["reason"],
            "perk_not_in_active_artifact")

    def test_curative_orbs_tangle_event_ownership(self):
        cases = {"tangle_pickup": "explicitly_not_a_trigger",
                 "tangle_destroy_shot": "official_historical_trigger",
                 "tangle_destroy_impact": "official_historical_trigger",
                 "unknown": "event_not_established"}
        for event, status in cases.items():
            result = curative_orbs_tangle_screen(
                event, "grandmaster nightfall", ARTIFACT_ID,
                ["Curative Orbs"], self.catalog)
            self.assertEqual(result["status"], status)
            self.assertIsNone(result["healing_amount"])
            self.assertFalse(result["certified"])

    def test_all_three_classes_use_same_single_artifact_gate(self):
        for character_class in ("hunter", "titan", "warlock"):
            with self.subTest(character_class=character_class):
                report = kinetic_impacts_gl_screen(
                    "primary", "grandmaster nightfall", ARTIFACT_ID,
                    ["Kinetic Impacts"], self.catalog,
                    character_class=character_class)
                self.assertEqual(report["status"], "official_historical_gl_ammo_eligibility")
                self.assertFalse(report["certified"])
        for character_class in ("hunter", "titan", "warlock"):
            with self.subTest(curative_class=character_class):
                report = curative_orbs_tangle_screen(
                    "tangle_destroy_shot", "grandmaster nightfall", ARTIFACT_ID,
                    ["Curative Orbs"], self.catalog,
                    character_class=character_class)
                self.assertEqual(report["status"], "official_historical_trigger")
                self.assertFalse(report["certified"])
        with self.assertRaises(ValueError):
            kinetic_impacts_gl_screen(
                "primary", "control", ARTIFACT_ID,
                ["Kinetic Impacts"], self.catalog, character_class="invalid")

    def test_invalid_ammo_and_event_fail_closed(self):
        for ammo in (None, "", "infinite", 1):
            with self.assertRaises(ValueError):
                kinetic_impacts_gl_screen(ammo, "control", ARTIFACT_ID,
                                          ["Kinetic Impacts"], self.catalog)
        for event in (None, "", 4):
            with self.assertRaises(ValueError):
                curative_orbs_tangle_screen(event, "control", ARTIFACT_ID,
                                            ["Curative Orbs"], self.catalog)


if __name__ == "__main__":
    unittest.main()
