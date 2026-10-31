"""Synthetic definition joins; not live manifest or gameplay evidence."""
import unittest
from scripts.weapon_plug_set_refs import build_weapon_plug_set_reference_index


class WeaponPlugSetReferenceTests(unittest.TestCase):
    def setUp(self):
        self.weapons = [{"hash": 202, "name": "Example", "sockets": [
            {"socketIndex": 0, "randomizedPlugSetHash": 11,
             "reusablePlugSetHash": 12},
            {"socketIndex": 1, "randomizedPlugSetHash": 13}]}]
        self.plug_sets = {"11": {"reusablePlugItems": [
            {"plugItemHash": 31, "currentlyCanRoll": True},
            {"plugItemHash": 32, "currentlyCanRoll": False},
            {"plugItemHash": 33}]},
            "12": {"isFakePlugSet": True, "reusablePlugItems": [{"plugItemHash": 34}]}}

    def run_join(self, weapons=None, sets=None):
        return build_weapon_plug_set_reference_index(
            self.weapons if weapons is None else weapons,
            self.plug_sets if sets is None else sets)

    def test_exact_socket_and_set_join(self):
        rows = self.run_join()
        self.assertEqual(rows[0]["itemHash"], 202)
        self.assertEqual([(p["socketIndex"], p["kind"], p["plugSetHash"])
                          for p in rows[0]["resolvedPlugSets"]],
                         [(0, "randomized", 11), (0, "reusable", 12), (1, "randomized", 13)])

    def test_preserves_three_state_currently_can_roll(self):
        plugs = self.run_join()[0]["resolvedPlugSets"][0]["plugs"]
        self.assertEqual([p["currentlyCanRoll"] for p in plugs], [True, False, None])

    def test_missing_definition_explicit(self):
        missing = self.run_join()[0]["resolvedPlugSets"][2]
        self.assertFalse(missing["definitionFound"])
        self.assertIsNone(missing["plugs"])

    def test_fake_set_preserved(self):
        fake = self.run_join()[0]["resolvedPlugSets"][1]
        self.assertTrue(fake["isFakePlugSet"])

    def test_no_roll_or_enhancement_certification(self):
        row = self.run_join()[0]
        for field in ("certifiedObtainableRoll", "certifiedEnhancedPerks", "certifiedCrossSocketPair"):
            self.assertFalse(row[field])

    def test_same_name_versions_remain_separate(self):
        rows = self.run_join(weapons=[{"hash": 202, "name": "Same", "sockets": []},
                                      {"hash": 201, "name": "Same", "sockets": []}])
        self.assertEqual([r["itemHash"] for r in rows], [201, 202])

    def test_no_sockets_is_safe(self):
        self.assertEqual(self.run_join(weapons=[{"hash": 2, "sockets": []}])[0]["resolvedPlugSets"], [])

    def test_empty_definition_is_distinct_from_missing(self):
        row = self.run_join(sets={"11": {"reusablePlugItems": []}})[0]["resolvedPlugSets"][0]
        self.assertTrue(row["definitionFound"])
        self.assertEqual(row["plugs"], [])

    def test_bad_hash_rejected(self):
        for bad in (-1, True, 2**32, "11"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.run_join(weapons=[{"hash": 2, "sockets": [
                    {"socketIndex": 0, "randomizedPlugSetHash": bad}]}])

    def test_invalid_roll_flag_rejected(self):
        with self.assertRaises(ValueError):
            self.run_join(sets={"11": {"reusablePlugItems": [
                {"plugItemHash": 2, "currentlyCanRoll": 1}]}})

    def test_invalid_plug_hash_rejected(self):
        with self.assertRaises(ValueError):
            self.run_join(sets={"11": {"reusablePlugItems": [{"plugItemHash": -1}]}})

    def test_malformed_plug_set_rejected(self):
        for bad in ("not object", {"reusablePlugItems": [None]},
                    {"reusablePlugItems": "bad"}, {"redacted": "no"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.run_join(sets={"11": bad})

    def test_names_resolve_only_from_exact_hash_same_manifest(self):
        definitions = {"31": {"displayProperties": {"name": "Example Trait"}},
                       "32": {"displayProperties": {"name": ""}},
                       "33": {"displayProperties": {"name": 123}}}
        rows = build_weapon_plug_set_reference_index(self.weapons, self.plug_sets, definitions)
        plugs = rows[0]["resolvedPlugSets"][0]["plugs"]
        self.assertEqual([p["plugName"] for p in plugs], ["Example Trait", None, None])
        self.assertEqual([p["plugDefinitionFound"] for p in plugs], [True, True, True])
        self.assertFalse(rows[0]["certifiedEnhancedPerks"])
        self.assertFalse(rows[0]["certifiedObtainableRoll"])

    def test_missing_name_and_missing_definition_are_not_conflated(self):
        rows = build_weapon_plug_set_reference_index(self.weapons, self.plug_sets, {})
        plug = rows[0]["resolvedPlugSets"][0]["plugs"][0]
        self.assertIsNone(plug["plugName"])
        self.assertFalse(plug["plugDefinitionFound"])

    def test_malformed_optional_item_definitions_fail_closed(self):
        with self.assertRaises(TypeError):
            build_weapon_plug_set_reference_index(self.weapons, self.plug_sets, [])
        with self.assertRaises(ValueError):
            build_weapon_plug_set_reference_index(self.weapons, self.plug_sets, {"31": "bad"})
        with self.assertRaises(ValueError):
            build_weapon_plug_set_reference_index(self.weapons, self.plug_sets,
                                                   {"31": {"displayProperties": "bad"}})

    def test_invalid_top_level_types(self):
        with self.assertRaises(TypeError):
            build_weapon_plug_set_reference_index({}, {})
        with self.assertRaises(TypeError):
            build_weapon_plug_set_reference_index([], [])


if __name__ == "__main__":
    unittest.main()
