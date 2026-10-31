"""Synthetic checks for Bungie's published 9.7.0 perk parameters, not gameplay."""
from decimal import Decimal
import unittest

from scripts.collective_action_evidence import (
    published_bonus, duration_upper_bound, published_single_hit,
    SOURCE_URL, PATCH, PUBLISHED_DATE, MAX_DURATION_SECONDS,
)


class CollectiveActionEvidenceTests(unittest.TestCase):
    def test_official_source_version(self):
        self.assertEqual(PATCH, "9.7.0")
        self.assertEqual(PUBLISHED_DATE, "2026-06-09")
        self.assertIn("bungie.net", SOURCE_URL)

    def test_pve_base_bonus(self):
        self.assertEqual(published_bonus("pve"), Decimal("1.30"))

    def test_pve_enhanced_bonus(self):
        self.assertEqual(published_bonus("pve", True), Decimal("1.33"))

    def test_pvp_base_bonus(self):
        self.assertEqual(published_bonus("pvp"), Decimal("1.10"))

    def test_pvp_enhanced_bonus(self):
        self.assertEqual(published_bonus("pvp", True), Decimal("1.11"))

    def test_modes_not_interchanged(self):
        self.assertNotEqual(published_bonus("pve"), published_bonus("pvp"))
        with self.assertRaises(ValueError):
            published_bonus("competitive")

    def test_enhanced_is_explicit_boolean(self):
        for bad in (1, None, "yes"):
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                published_bonus("pve", bad)

    def test_duration_sources_and_cap(self):
        self.assertEqual(duration_upper_bound(["firesprite"]), Decimal("8"))
        self.assertEqual(duration_upper_bound(["void_breach"]), Decimal("8"))
        self.assertEqual(duration_upper_bound(["ionic_trace"]), Decimal("4"))
        self.assertEqual(duration_upper_bound(["stasis_shard"]), Decimal("4"))
        self.assertEqual(duration_upper_bound(["tangle_detonation"]), Decimal("4"))
        self.assertEqual(duration_upper_bound(["tangle_throw"]), Decimal("4"))
        self.assertEqual(duration_upper_bound(["firesprite"] * 4), MAX_DURATION_SECONDS)

    def test_artifact_orb_grant_not_invented(self):
        with self.assertRaises(ValueError):
            duration_upper_bound(["artifact_arc_orb"])

    def test_no_double_proc_assumption(self):
        self.assertEqual(duration_upper_bound(["tangle_throw"]), Decimal("4"))

    def test_invalid_duration_input(self):
        for bad in (None, "firesprite", {"firesprite"}):
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                duration_upper_bound(bad)

    def test_published_hit_scenario_not_measured(self):
        self.assertEqual(published_single_hit(100, "pve"), Decimal("130.00"))
        self.assertEqual(published_single_hit(100, "pvp", True), Decimal("111.00"))

    def test_invalid_hit_values(self):
        for bad in (True, -1, "NaN", "Infinity"):
            with self.subTest(bad=bad), self.assertRaises((TypeError, ValueError)):
                published_single_hit(bad, "pve")


if __name__ == "__main__":
    unittest.main()
