import unittest

from simulator.shieldburst_rally_evidence import (
    SOURCE_DATE, SOURCE_URL, rally_scorching_rounds_eligibility,
)


class ShieldburstRallyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.inputs = dict(
            class_name="Titan", subclass="Sunbreaker", aspect_equipped=True,
            barricade_type="Rally", barricade_deployed=True,
            actor_is_ally=True, ally_behind_barricade=True,
            weapon_damage_type="Solar",
        )

    def check(self, **changes):
        return rally_scorching_rounds_eligibility(**{**self.inputs, **changes})

    def test_official_solar_ally_condition_is_not_damage_certification(self):
        result = self.check()
        self.assertEqual(result["status"], "official_text_conditions_met_not_gameplay_verified")
        self.assertFalse(result["activation_measured"])
        self.assertIsNone(result["damage_multiplier"])
        self.assertIsNone(result["scorch_stacks"])
        self.assertIsNone(result["scorch_source_ownership"])
        self.assertIsNone(result["pvp_breakpoint"])
        self.assertFalse(result["artifact_synergy_certified"])
        self.assertFalse(result["weapon_roll_legality_certified"])

    def test_kinetic_damage_type_is_eligible(self):
        self.assertEqual(self.check(weapon_damage_type="  KINETIC ")["status"],
                         "official_text_conditions_met_not_gameplay_verified")

    def test_kinetic_slot_stasis_and_strand_not_misidentified(self):
        for damage_type in ("Stasis", "Strand"):
            with self.subTest(damage_type=damage_type):
                result = self.check(weapon_damage_type=damage_type)
                self.assertEqual(result["status"], "official_conditions_not_met")

    def test_other_elemental_damage_types_not_certified(self):
        for damage_type in ("Arc", "Void"):
            with self.subTest(damage_type=damage_type):
                self.assertEqual(self.check(weapon_damage_type=damage_type)["status"],
                                 "official_conditions_not_met")

    def test_towering_barricade_not_rally(self):
        self.assertEqual(self.check(barricade_type="Towering")["status"],
                         "official_conditions_not_met")

    def test_requires_deployed_barricade_and_position(self):
        for field in ("barricade_deployed", "ally_behind_barricade"):
            with self.subTest(field=field):
                self.assertEqual(self.check(**{field: False})["status"],
                                 "official_conditions_not_met")

    def test_requires_titan_sunbreaker_shieldburst(self):
        for field, value in (("class_name", "Hunter"), ("subclass", "Prismatic"),
                             ("aspect_equipped", False)):
            with self.subTest(field=field):
                self.assertEqual(self.check(**{field: value})["status"],
                                 "official_conditions_not_met")

    def test_owner_not_automatically_classed_as_ally(self):
        self.assertEqual(self.check(actor_is_ally=False)["status"],
                         "official_conditions_not_met")

    def test_unknown_conditions_fail_closed(self):
        for field in self.inputs:
            with self.subTest(field=field):
                self.assertEqual(self.check(**{field: None})["status"],
                                 "insufficient_inputs")

    def test_explicit_contradiction_overrides_unknown(self):
        self.assertEqual(self.check(weapon_damage_type=None, barricade_deployed=False)["status"],
                         "official_conditions_not_met")

    def test_invalid_values_rejected(self):
        for field, value in (("aspect_equipped", 1), ("actor_is_ally", "yes"),
                             ("weapon_damage_type", "kinetic slot"),
                             ("class_name", "")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(**{field: value})

    def test_official_source_metadata(self):
        self.assertEqual(SOURCE_DATE, "2026-06-09")
        self.assertEqual(SOURCE_URL,
                         "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0")


if __name__ == "__main__":
    unittest.main()
