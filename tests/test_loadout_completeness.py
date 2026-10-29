import unittest
from simulator.loadout_completeness import loadout_gaps, REQUIRED_LOADOUT

class LoadoutCompletenessTests(unittest.TestCase):
    def test_empty_build_reports_every_gap(self):
        result = loadout_gaps({})
        self.assertEqual(set(result["missing"]), set(REQUIRED_LOADOUT))
        self.assertFalse(result["certified_build"])

    def test_all_fields_present_still_not_certified(self):
        result = loadout_gaps({key: "placeholder" for key in REQUIRED_LOADOUT})
        self.assertTrue(result["complete_fields"])
        self.assertFalse(result["certified_build"])

    def test_empty_fragments_reported(self):
        build = {key: "placeholder" for key in REQUIRED_LOADOUT}
        build["fragments"] = []
        self.assertIn("fragments", loadout_gaps(build)["missing"])

if __name__ == "__main__":
    unittest.main()
