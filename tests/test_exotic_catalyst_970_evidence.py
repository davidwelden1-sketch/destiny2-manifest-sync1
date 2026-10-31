"""Synthetic provenance/legality screens, never live-game tests."""
import unittest

from simulator.exotic_catalyst_970_evidence import screen_exotic_catalyst_trait


class ExoticCatalyst970EvidenceTests(unittest.TestCase):
    def screen(self, weapon, trait, **kwargs):
        return screen_exotic_catalyst_trait(weapon, trait, activity="pve", **kwargs)

    def test_official_added_catalyst_traits(self):
        cases = {
            "Crimson": ("To the Pain",),
            "Coldheart": ("Supercharged Magazine",),
            "Merciless": ("Heal Clip",),
            "Sunshot": ("Loose Change",),
            "Skyburner's Oath": ("Incandescent", "Burning Ambition"),
            "Riskrunner": ("Chain Reaction",),
            "The Prospector": ("Danger Zone",),
            "Borealis": ("Shield Disorient",),
            "Touch of Malice": ("Precision Instrument",),
            "Heirloom": ("Incandescent",),
        }
        for weapon, traits in cases.items():
            for trait in traits:
                with self.subTest(weapon=weapon, trait=trait):
                    r = self.screen(weapon, trait)
                    self.assertEqual(r["status"], "official_historical_catalyst_trait_added")
                    self.assertFalse(r["current_catalyst_equipped_verified"])
                    self.assertFalse(r["gameplay_measured"])
                    self.assertIsNone(r["pve_boss_dps"])

    def test_touch_of_malice_old_rapid_hit_is_replaced(self):
        r = self.screen("Touch of Malice", "Rapid Hit")
        self.assertEqual(r["status"], "official_historical_catalyst_trait_replaced")
        self.assertEqual(r["socket_kind"], "exotic_catalyst_not_randomized_legendary_trait_column")

    def test_hard_light_redaction_is_not_inferred(self):
        for trait in ("Incandescent", "Unknown", "[REDACTED]"):
            with self.subTest(trait=trait):
                self.assertEqual(self.screen("Hard Light", trait)["status"],
                                 "official_catalyst_trait_name_redacted")

    def test_no_legendary_roll_or_wrong_exotic_assignment(self):
        self.assertEqual(self.screen("Riskrunner", "Heal Clip")["status"],
                         "trait_not_listed_for_weapon_in_patch")
        self.assertEqual(self.screen("Imaginary Exotic", "Chain Reaction")["status"],
                         "weapon_not_in_this_catalyst_patch_index")

    def test_case_and_whitespace_normalization(self):
        self.assertEqual(self.screen(" riskRUNNER ", "  chain reaction ")["status"],
                         "official_historical_catalyst_trait_added")

    def test_pve_and_pvp_independent_measurements(self):
        for activity in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                r = screen_exotic_catalyst_trait("Riskrunner", "Chain Reaction", activity=activity)
                self.assertEqual(r["status"], "official_historical_catalyst_trait_added")
                self.assertIsNone(r["damage_multiplier"])
                self.assertIsNone(r["pvp_guardian_ttk"])
                self.assertIsNone(r["kill_attribution"])
                self.assertFalse(r["artifact_legality_certified"])

    def test_enhanced_catalyst_not_assumed(self):
        self.assertEqual(self.screen("Riskrunner", "Chain Reaction", enhanced=True)["status"],
                         "enhanced_catalyst_trait_not_sourced")

    def test_patch_mismatch_fails_closed(self):
        self.assertEqual(self.screen("Riskrunner", "Chain Reaction", source_patch_version="9.7.0.6")["status"],
                         "source_patch_version_mismatch")

    def test_invalid_inputs_rejected(self):
        for weapon, trait in (("", "Chain Reaction"), ("Riskrunner", " "), (None, "Chain Reaction")):
            with self.assertRaises(ValueError):
                self.screen(weapon, trait)
        with self.assertRaises(ValueError):
            self.screen("Riskrunner", "Chain Reaction", enhanced=1)
        with self.assertRaises(ValueError):
            self.screen("Riskrunner", "Chain Reaction", source_patch_version="")
        with self.assertRaises(ValueError):
            screen_exotic_catalyst_trait("Riskrunner", "Chain Reaction", activity="gambit")

    def test_source_provenance_and_certification_limits(self):
        r = self.screen("Merciless", "Heal Clip")
        self.assertEqual(r["source_date"], "2026-06-09")
        self.assertEqual(r["source_patch_version"], "9.7.0")
        self.assertIn("bungie.net", r["source_url"])
        self.assertFalse(r["current_catalyst_acquisition_verified"])
        self.assertFalse(r["enhanced_roll_certified"])
        self.assertFalse(r["current_game_verified"])
        self.assertIsNone(r["perk_activation"])
        self.assertIsNone(r["perk_uptime"])


if __name__ == "__main__":
    unittest.main()
