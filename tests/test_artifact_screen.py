import unittest
from simulator.artifact_screen import screen_candidate, screen_one_active_artifact

class ArtifactScreenTests(unittest.TestCase):
    def test_class_coverage(self):
        for character in ("hunter", "titan", "warlock"):
            self.assertTrue(screen_candidate(character, "raid", ["A"], ["A"])["eligible"])

    def test_restricted_activity(self):
        self.assertFalse(screen_candidate("hunter", "Trials", ["A"], ["A"])["eligible"])

    def test_glory_artifact_disabled(self):
        self.assertFalse(screen_candidate("hunter", "Glory", ["A"], ["A"])["eligible"])

    def test_single_artifact_pool(self):
        catalog = {"a": ["A", "B"], "b": ["C", "D"]}
        self.assertFalse(screen_one_active_artifact(
            "titan", "raid", "a", ["A", "C"], catalog)["eligible"])
        result = screen_one_active_artifact("titan", "raid", "a", ["A"], catalog)
        self.assertTrue(result["eligible"])
        self.assertFalse(result["catalog_independently_verified"])

    def test_unknown_perk(self):
        self.assertFalse(screen_candidate("titan", "raid", ["B"], ["A"])["eligible"])

    def test_selection_limit(self):
        selected = [str(i) for i in range(8)]
        self.assertFalse(screen_candidate("warlock", "raid", selected, selected)["eligible"])

if __name__ == "__main__":
    unittest.main()
