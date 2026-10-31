"""Synthetic tests for source-gated weapon perk evidence, not game tests."""
import unittest

from simulator.weapon_perk_970_evidence import (
    patch_weapon_perk_parameter, attrition_orbs_patch_hit_count,
)


class WeaponPerk970EvidenceTests(unittest.TestCase):
    def perk(self, name, **kw):
        return patch_weapon_perk_parameter(name, activity="pve", **kw)

    def orb(self, family, **kw):
        return attrition_orbs_patch_hit_count(family, activity="pve", **kw)

    def test_focused_fury_conditional_bonus_and_hit_fraction(self):
        r = self.perk("Focused Fury")
        self.assertEqual(r["bonus_fraction"], 0.25)
        self.assertEqual(r["prior_bonus_fraction"], 0.20)
        self.assertEqual(r["activation"]["magazine_hit_fraction"], 0.35)
        self.assertNotIn("rounded_hits", r["activation"])

    def test_full_court_only_maximum_explosive_component(self):
        r = self.perk("Full Court")
        self.assertEqual(r["bonus_fraction"], 0.35)
        self.assertEqual(r["bonus_scope"], "maximum_explosive_component_only")
        self.assertIsNone(r["activation"]["distance_curve"])

    def test_lasting_impression_explosion_not_impact(self):
        r = self.perk("Lasting Impression")
        self.assertEqual(r["bonus_fraction"], 0.35)
        self.assertEqual(r["bonus_scope"], "explosive_component_only")
        self.assertIsNone(r["activation"]["detonation_timing"])

    def test_reservoir_burst_standard_and_enhanced(self):
        standard = self.perk("Reservoir Burst")
        enhanced = self.perk("Reservoir Burst", enhanced=True)
        self.assertEqual((standard["bonus_fraction"],
                          standard["prior_bonus_fraction"]), (0.30, 0.25))
        self.assertEqual((enhanced["bonus_fraction"],
                          enhanced["prior_bonus_fraction"]), (0.33, 0.275))
        self.assertIsNone(enhanced["activation"]["trigger_requirements"])
        self.assertFalse(enhanced["enhanced_roll_certified"])

    def test_unsourced_enhanced_full_court_is_not_guessed(self):
        r = self.perk("Full Court", enhanced=True)
        self.assertEqual(r["status"], "enhanced_variant_not_sourced")
        self.assertIsNone(r["bonus_fraction"])

    def test_pvp_has_no_borrowed_pve_damage(self):
        for activity in ("pvp", "competitive", "trials"):
            with self.subTest(activity=activity):
                r = patch_weapon_perk_parameter("Reservoir Burst",
                                                activity=activity, enhanced=True)
                self.assertEqual(r["status"], "pvp_not_independently_calibrated")
                self.assertIsNone(r["bonus_fraction"])
                self.assertIsNone(r["guardian_ttk"])

    def test_patch_mismatch_invalidates_parameter(self):
        r = self.perk("Focused Fury", source_patch_version="9.7.0.6")
        self.assertEqual(r["status"], "source_patch_version_mismatch")
        self.assertIsNone(r["bonus_fraction"])

    def test_unknown_perk_fails_closed(self):
        r = self.perk("Not A Real Perk")
        self.assertEqual(r["status"], "unsupported_perk")
        self.assertIsNone(r["bonus_fraction"])

    def test_no_damage_roll_or_artifact_certification(self):
        r = self.perk("Reservoir Burst", enhanced=True)
        for flag in ("gameplay_measured", "current_game_verified",
                     "current_roll_certified", "enhanced_roll_certified",
                     "artifact_legality_certified"):
            self.assertFalse(r[flag])
        for field in ("absolute_damage", "boss_dps", "guardian_ttk"):
            self.assertIsNone(r[field])
        self.assertIn("bungie.net", r["source_url"])

    def test_wave_frame_attrition_orbs_reduced_hit_gate(self):
        r = self.orb("wave_frame_grenade_launcher")
        self.assertEqual((r["hits_to_activate"],
                          r["prior_hits_to_activate"]), (4, 10))
        self.assertIsNone(r["orb_rate_measured"])

    def test_rocket_launcher_attrition_orbs_reduced_hit_gate(self):
        r = self.orb("rocket_launcher")
        self.assertEqual((r["hits_to_activate"],
                          r["prior_hits_to_activate"]), (3, 6))

    def test_orb_pvp_unverified(self):
        r = attrition_orbs_patch_hit_count("rocket_launcher", activity="pvp")
        self.assertEqual(r["status"], "pvp_not_independently_calibrated")
        self.assertIsNone(r["hits_to_activate"])

    def test_orb_unknown_family_fails_closed(self):
        r = self.orb("sniper_rifle")
        self.assertEqual(r["status"], "unsupported_family")
        self.assertIsNone(r["hits_to_activate"])

    def test_orb_patch_mismatch(self):
        r = self.orb("rocket_launcher", source_patch_version="9.7.0.5")
        self.assertEqual(r["status"], "source_patch_version_mismatch")
        self.assertIsNone(r["hits_to_activate"])

    def test_invalid_inputs(self):
        for name in ("", "   ", None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.perk(name)
        with self.assertRaises(ValueError):
            self.perk("Reservoir Burst", enhanced=1)
        with self.assertRaises(ValueError):
            self.perk("Focused Fury", source_patch_version="")
        with self.assertRaises(ValueError):
            patch_weapon_perk_parameter("Focused Fury", activity="gambit")
        with self.assertRaises(ValueError):
            self.orb("")
        with self.assertRaises(ValueError):
            attrition_orbs_patch_hit_count("rocket_launcher", activity="gambit")

    def test_published_source_date_and_evidence_grade(self):
        r = self.perk("Full Court")
        self.assertEqual(r["source_date"], "2026-06-09")
        self.assertEqual(r["source_patch_version"], "9.7.0")
        self.assertEqual(r["evidence_grade"], "official_historical_patch_parameter")


if __name__ == "__main__":
    unittest.main()
