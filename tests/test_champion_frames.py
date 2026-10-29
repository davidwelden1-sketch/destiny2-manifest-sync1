"""Historical Bungie frame table and mode policy regression tests."""
import unittest
from simulator.champion_frames import champion_effect, artifact_policy, SPECIAL_FRAMES

class ChampionFramesTest(unittest.TestCase):
    def test_all_specific_frame_rows(self):
        self.assertEqual(len(SPECIAL_FRAMES), 20)
        for (weapon_type, frame), effect in SPECIAL_FRAMES.items():
            with self.subTest(weapon_type=weapon_type, frame=frame):
                result = champion_effect(weapon_type, frame, metadata_reviewed=True)
                self.assertEqual(result["effect"], effect)
                self.assertFalse(result["certified_weapon"])
                self.assertFalse(result["current_manifest_verified"])

    def test_generic_frame_effects(self):
        for frame, effect in [("Aggressive", "unstoppable"), ("High Impact", "unstoppable"),
                              ("Precision", "barrier"), ("Adaptive", "barrier"),
                              ("Lightweight", "overload"), ("Rapid-Fire", "overload")]:
            with self.subTest(frame=frame):
                self.assertEqual(champion_effect("AR", frame, metadata_reviewed=True)["effect"], effect)

    def test_special_does_not_leak_to_other_weapon_types(self):
        self.assertIsNone(champion_effect("AR", "heavy burst", metadata_reviewed=True)["effect"])
        self.assertIsNone(champion_effect("Sword", "support", metadata_reviewed=True)["effect"])
        self.assertEqual(champion_effect("Pulse", "heavy burst", metadata_reviewed=True)["effect"], "unstoppable")

    def test_unreviewed_frame_fails_closed(self):
        result = champion_effect("Sword", "vortex")
        self.assertIsNone(result["effect"])
        self.assertEqual(result["status"], "weapon_frame_unreviewed")

    def test_unknown_frame_fails_closed(self):
        self.assertEqual(champion_effect("HC", "not a real frame", metadata_reviewed=True)["status"],
                         "unknown_frame_requires_review")

    def test_heat_weapon_rule(self):
        self.assertEqual(champion_effect("Various", "Dynamic Heat Weapons", metadata_reviewed=True)["effect"], "overload")
        self.assertEqual(champion_effect("Various", "Balanced Heat Weapons", metadata_reviewed=True)["effect"], "overload")

    def test_input_validation(self):
        for args in [("", "adaptive"), ("ar", ""), (None, "adaptive")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                champion_effect(*args)

    def test_trials_and_competitive_disable_artifacts(self):
        for mode in ("Trials", "Trials of Osiris", "Competitive", "Competitive Crucible"):
            self.assertIs(artifact_policy(mode)["artifact_enabled"], False)

    def test_other_modes_not_automatically_certified(self):
        for mode in ("PvE", "6v6", "Raid"):
            self.assertIsNone(artifact_policy(mode)["artifact_enabled"])

if __name__ == "__main__":
    unittest.main()
