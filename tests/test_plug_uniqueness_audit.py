"""Synthetic unique plug membership audit, no live roll or damage claims."""
import unittest
from scripts.plug_uniqueness_audit import audit_unique_weapon_plugs

def entry(socket, kind, plugs, fake=False, redacted=False):
    return {"socketIndex": socket, "kind": kind, "definitionFound": True,
            "isFakePlugSet": fake, "redacted": redacted,
            "plugs": [{"plugItemHash": h, "currentlyCanRoll": flag}
                      for h, flag in plugs]}

class UniquePlugAuditTests(unittest.TestCase):
    def test_deduplicates_same_weapon_across_sockets_and_sources(self):
        rows = [{"itemHash": 10, "resolvedPlugSets": [
            entry(0, "randomized", [(1, True), (2, True), (2, True)]),
            entry(1, "randomized", [(2, True), (3, True)]),
            entry(1, "reusable", [(2, True), (4, True)])]},
            {"itemHash": 11, "resolvedPlugSets": [
                entry(0, "randomized", [(1, True)])]}]
        c = audit_unique_weapon_plugs(rows)["counts"]
        self.assertEqual(c["plugOccurrences"], 8)
        self.assertEqual(c["distinctWeaponPlugMemberships"], 5)
        self.assertEqual(c["distinctWeaponRandomizedMemberships"], 4)
        self.assertEqual(c["distinctWeaponClearRandomizedMemberships"], 4)
        self.assertEqual(c["uniquePlugHashesAllSources"], 4)
        self.assertEqual(c["uniquePlugHashesRandomized"], 3)
        self.assertEqual(c["repeatedSocketOccurrencesBeyondWeaponPlugMemberships"], 3)
        self.assertEqual(c["weaponsWithTwoClearRandomizedSocketPositions"], 1)

    def test_fake_redacted_and_unknown_fail_closed(self):
        rows = [{"itemHash": 10, "resolvedPlugSets": [
            entry(0, "randomized", [(1, True)], fake=True),
            entry(1, "randomized", [(2, True)], redacted=True),
            entry(2, "randomized", [(3, True)], fake=None),
            entry(3, "randomized", [(4, True)], redacted=None),
            entry(4, "randomized", [(5, False)]),
            entry(5, "randomized", [(6, None)]),
            entry(6, "randomized", [(7, True)])]}]
        c = audit_unique_weapon_plugs(rows)["counts"]
        self.assertEqual(c["distinctWeaponRandomizedMemberships"], 7)
        self.assertEqual(c["distinctWeaponClearRandomizedMemberships"], 1)
        self.assertEqual(c["excludedFakeOrRedactedRandomizedOccurrences"], 2)
        self.assertEqual(c["unknownFakeOrRedactedRandomizedOccurrences"], 2)
        self.assertEqual(c["weaponsWithTwoClearRandomizedSocketPositions"], 0)

    def test_missing_set_has_no_memberships(self):
        r = audit_unique_weapon_plugs([{"itemHash": 10, "resolvedPlugSets": [
            {"socketIndex": 0, "kind": "randomized",
             "definitionFound": False, "plugs": None}]}])
        self.assertEqual(r["counts"]["plugOccurrences"], 0)
        self.assertIsNone(r["certifiedObtainableRollCount"])
        self.assertFalse(r["certifiedPvEOrPvPPerformance"])

    def test_two_sockets_not_a_certified_pair(self):
        r = audit_unique_weapon_plugs([{"itemHash": 10, "resolvedPlugSets": [
            entry(0, "randomized", [(1, True)]),
            entry(1, "randomized", [(2, True)])]}])
        self.assertEqual(r["counts"]["weaponsWithTwoClearRandomizedSocketPositions"], 1)
        self.assertIsNone(r["certifiedEnhancedPerkCount"])

    def test_invalid_data_fails_closed(self):
        sample = {"itemHash": 10, "resolvedPlugSets": [
            entry(0, "randomized", [(1, True)])]}
        for rows in ([sample, sample], [{"itemHash": True, "resolvedPlugSets": []}],
                     [{"itemHash": 10, "resolvedPlugSets": [
                         entry(0, "randomized", [(1, "yes")])]}],
                     [{"itemHash": 10, "resolvedPlugSets": [
                         {"socketIndex": 0, "kind": "randomized",
                          "definitionFound": False, "plugs": []}]}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                audit_unique_weapon_plugs(rows)

    def test_empty_catalog(self):
        c = audit_unique_weapon_plugs([])["counts"]
        self.assertEqual(c["weaponDefinitions"], 0)
        self.assertEqual(c["uniquePlugHashesAllSources"], 0)

if __name__ == "__main__":
    unittest.main()
