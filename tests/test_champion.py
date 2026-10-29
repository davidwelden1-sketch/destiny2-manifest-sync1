import unittest
from simulator.champion import intrinsic_champion_rule, SPECIFIC, BASE, SOURCE


class TestIntrinsicChampionRules(unittest.TestCase):
    def test_all_official_specific_frame_rules(self):
        self.assertEqual(len(SPECIFIC), 18)
        for (frame, weapon_type), effect in SPECIFIC.items():
            with self.subTest(frame=frame, weapon_type=weapon_type):
                row = intrinsic_champion_rule("adaptive", frame, weapon_type)
                self.assertEqual(row["effect"], effect)
                self.assertEqual(row["evidence"], "official_specific_frame_rule")
                self.assertFalse(row["weapon_verified"])

    def test_specific_overrides_base(self):
        row = intrinsic_champion_rule("adaptive", "vortex", "sword")
        self.assertEqual(row["effect"], "overload")
        self.assertNotEqual(row["effect"], BASE["adaptive"])

    def test_base_rules_provisional_without_verified_frame(self):
        for archetype, effect in BASE.items():
            with self.subTest(archetype=archetype):
                row = intrinsic_champion_rule(archetype)
                self.assertEqual(row["effect"], effect)
                self.assertEqual(row["evidence"], "provisional_base_rule")

    def test_unknown_frame_does_not_falsely_fall_back(self):
        row = intrinsic_champion_rule("precision", "unverified future frame", "sword")
        self.assertIsNone(row["effect"])
        self.assertEqual(row["evidence"], "unverified_frame")

    def test_known_frame_wrong_weapon_type_fails_closed(self):
        row = intrinsic_champion_rule("adaptive", "caster", "hand cannon")
        self.assertIsNone(row["effect"])
        self.assertEqual(row["evidence"], "frame_weapon_type_mismatch")

    def test_weapon_type_required_for_specific_frame(self):
        self.assertIsNone(intrinsic_champion_rule(frame="caster")["effect"])

    def test_heat_weapon_rules(self):
        for frame in ("dynamic heat weapons", "balanced heat weapons"):
            self.assertEqual(intrinsic_champion_rule(frame=frame)["effect"], "overload")

    def test_alias_and_hyphen_normalization(self):
        self.assertEqual(intrinsic_champion_rule(frame="rocket-assisted", weapon_type="pulse")["effect"],
                         "unstoppable")

    def test_invalid_labels_rejected(self):
        for value in (True, 3, "", []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                intrinsic_champion_rule(frame=value)

    def test_unknowns_never_imply_artifact_or_measured_data(self):
        row = intrinsic_champion_rule()
        self.assertIsNone(row["effect"])
        self.assertFalse(row["weapon_verified"])
        self.assertEqual(row["source"], SOURCE)


if __name__ == "__main__":
    unittest.main()
