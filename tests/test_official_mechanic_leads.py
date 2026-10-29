"""Regression checks for conservative official-mechanic research leads."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEADS = ROOT / "data" / "official_mechanic_leads_2026_10_29.json"

class OfficialMechanicLeadsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(LEADS.read_text(encoding="utf-8"))

    def test_official_sources_are_dated_and_individually_linked(self):
        self.assertTrue(self.document["checked_at"])
        self.assertTrue(self.document["manifest_version_observed_ci"])
        for lead in self.document["leads"]:
            self.assertTrue(lead["official_patch_date"])
            self.assertTrue(lead["source_url"].startswith("https://www.bungie.net/"))
            self.assertTrue(lead["official_claim"])
            self.assertTrue(lead["unresolved"])

    def test_hypotheses_are_not_misreported_as_current_verified(self):
        self.assertEqual(self.document["current_gameplay_measurements"], 0)
        for lead in self.document["leads"]:
            self.assertIs(lead["current_gameplay_verified"], False)
            self.assertEqual(lead["artifact_legality"], "unknown_current_artifact_perk_selection")
            self.assertTrue(lead["hypothesis"])

    def test_cross_class_candidates_do_not_imply_legal_artifact_builds(self):
        for lead in self.document["leads"]:
            self.assertEqual(set(lead["classes"]), {"Titan", "Hunter", "Warlock"})
            self.assertIn(lead["activity"], {"PvE", "PvP"})
            self.assertNotIn("certified", lead.get("artifact_legality", "").lower())

if __name__ == "__main__":
    unittest.main()
