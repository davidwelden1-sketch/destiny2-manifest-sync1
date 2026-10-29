import unittest
from simulator.artifact_screen import screen_candidate

class ArtifactScreenTests(unittest.TestCase):
    def test_class_coverage(self):
        for character in ("hunter", "titan", "warlock"):
            self.assertTrue(screen_candidate(character, "raid", ["A"], ["A"])["eligible"])

    def test_restricted_activity(self):
        self.assertFalse(screen_candidate("hunter", "Trials", ["A"], ["A"])["eligible"])

    def test_unknown_perk(self):
        self.assertFalse(screen_candidate("titan", "raid", ["B"], ["A"])["eligible"])

    def test_selection_limit(self):
        selected = [str(i) for i in range(8)]
        self.assertFalse(screen_candidate("warlock", "raid", selected, selected)["eligible"])

if __name__ == "__main__":
    unittest.main()
