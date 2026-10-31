"""Synthetic plug coverage checks; no live catalog or gameplay certification."""
import unittest
from scripts.plug_coverage_audit import summarize_resolved_plug_coverage


class PlugCoverageAuditTests(unittest.TestCase):
    def sample(self):
        return [{"itemHash": 123, "resolvedPlugSets": [
            {"kind": "randomized", "definitionFound": True,
             "isFakePlugSet": False, "redacted": False, "plugs": [
                {"plugItemHash": 31, "plugName": "Perk", "plugDefinitionFound": True,
                 "currentlyCanRoll": True},
                {"plugItemHash": 32, "plugName": None, "plugDefinitionFound": False,
                 "currentlyCanRoll": None}]},
            {"kind": "reusable", "definitionFound": True, "isFakePlugSet": True,
             "redacted": False, "plugs": [
                {"plugItemHash": 33, "plugName": "Component", "plugDefinitionFound": True,
                 "currentlyCanRoll": False}]},
            {"kind": "randomized", "definitionFound": False, "plugs": None},
        ]}]

    def test_counts_distinguish_sources_and_unknowns(self):
        report = summarize_resolved_plug_coverage(self.sample())
        c = report["counts"]
        self.assertEqual(c["weaponDefinitions"], 1)
        self.assertEqual(c["plugSetReferences"], 3)
        self.assertEqual(c["missingPlugSetDefinitions"], 1)
        self.assertEqual(c["fakePlugSetReferences"], 1)
        self.assertEqual(c["plugOccurrences"], 3)
        self.assertEqual(c["randomizedPlugOccurrences"], 2)
        self.assertEqual(c["reusablePlugOccurrences"], 1)
        self.assertEqual(c["namedPlugOccurrences"], 2)
        self.assertEqual(c["missingPlugItemDefinitions"], 1)
        self.assertEqual((c["currentlyCanRoll_true"], c["currentlyCanRoll_false"],
                          c["currentlyCanRoll_unknown"]), (1, 1, 1))
        self.assertEqual(c["explicitTrueRandomizedOccurrences"], 1)
        self.assertIsNone(report["certifiedObtainableRollCount"])

    def test_empty_and_no_socket_cases(self):
        c = summarize_resolved_plug_coverage([
            {"itemHash": 1, "resolvedPlugSets": []},
            {"itemHash": 2, "resolvedPlugSets": [
                {"kind": "randomized", "definitionFound": True, "plugs": []}]}])["counts"]
        self.assertEqual(c["weaponsWithoutResolvedPlugSets"], 1)
        self.assertEqual(c["emptyPlugSetReferences"], 1)
        self.assertEqual(c["plugOccurrences"], 0)

    def test_fake_or_redacted_randomized_not_counted_as_clear_flag(self):
        rows = self.sample()
        rows[0]["resolvedPlugSets"][0]["isFakePlugSet"] = True
        c = summarize_resolved_plug_coverage(rows)["counts"]
        self.assertEqual(c["currentlyCanRoll_true"], 1)
        self.assertEqual(c["explicitTrueRandomizedOccurrences"], 0)
        rows[0]["resolvedPlugSets"][0]["isFakePlugSet"] = False
        rows[0]["resolvedPlugSets"][0]["redacted"] = True
        c = summarize_resolved_plug_coverage(rows)["counts"]
        self.assertEqual(c["explicitTrueRandomizedOccurrences"], 0)

    def test_rejects_duplicate_weapon_hash(self):
        row = {"itemHash": 2, "resolvedPlugSets": []}
        with self.assertRaises(ValueError):
            summarize_resolved_plug_coverage([row, row])

    def test_rejects_bad_flags(self):
        for field, value in (("currentlyCanRoll", 1), ("plugDefinitionFound", None)):
            rows = self.sample()
            rows[0]["resolvedPlugSets"][0]["plugs"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                summarize_resolved_plug_coverage(rows)

    def test_rejects_malformed_set(self):
        rows = self.sample()
        rows[0]["resolvedPlugSets"][0]["definitionFound"] = False
        with self.assertRaises(ValueError):
            summarize_resolved_plug_coverage(rows)

    def test_never_certifies_rolls_or_gameplay(self):
        r = summarize_resolved_plug_coverage(self.sample())
        self.assertTrue(r["manifestJoinOnly"])
        self.assertIsNone(r["certifiedEnhancedPerkCount"])
        self.assertFalse(r["certifiedPvEOrPvPPerformance"])


if __name__ == "__main__":
    unittest.main()
