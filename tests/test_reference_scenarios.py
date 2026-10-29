import unittest
from simulator.reference_scenarios import evaluate_pvp_reference

class ReferenceScenarioTests(unittest.TestCase):
    def setUp(self):
        self.reference = {
            "weapon": "test archetype", "rpm": 140,
            "precision_damage": 80, "body_damage": 50,
            "source_url": "https://example.org/test",
            "game_version": "test", "activity": "pvp",
            "scenario": "unbuffed_baseline"
        }

    def test_ttk_and_provenance(self):
        result = evaluate_pvp_reference(self.reference, target_health=230)
        self.assertEqual(result["optimal"]["shots"], 3)
        self.assertAlmostEqual(result["optimal"]["ttk_seconds"], 120 / 140)
        self.assertFalse(result["certified_current"])
        self.assertFalse(result["measurement_imported"])

    def test_outdated_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_pvp_reference({**self.reference, "explicitly_outdated": True},
                                   target_health=230)

    def test_missing_source_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_pvp_reference({**self.reference, "source_url": ""},
                                   target_health=230)

    def test_wrong_activity_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_pvp_reference({**self.reference, "activity": "pve"},
                                   target_health=230)

if __name__ == "__main__":
    unittest.main()
