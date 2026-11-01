"""Synthetic integrity tests for exact-hash game-wide pair query inputs."""
import unittest

from scripts.query_weapon_pairs import find_pair_candidates


class GameWidePairIntegrityTests(unittest.TestCase):
    @staticmethod
    def item(left, right, *, left_index=2, right_index=3):
        return [{
            "item_type": 3, "item_hash": 100, "name": "Synthetic Weapon",
            "sockets": [
                {"socket_index": left_index,
                 "randomized_candidate_plug_hashes": left,
                 "currently_rollable_randomized_candidate_plug_hashes": left,
                 "default_visible": True, "plugset_references": []},
                {"socket_index": right_index,
                 "randomized_candidate_plug_hashes": right,
                 "currently_rollable_randomized_candidate_plug_hashes": right,
                 "default_visible": True, "plugset_references": []},
            ],
        }]

    def test_valid_exact_hash_pair_survives(self):
        matches = find_pair_candidates(self.item([11], [22]), 11, 22)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["item_hash"], 100)
        self.assertEqual(matches[0]["roll_legality"], "unverified")

    def test_boolean_plug_cannot_alias_integer_hash(self):
        # True == 1 in Python, but True is not a Bungie plug hash.
        for candidate, query in ((True, 1), (False, 0)):
            with self.subTest(candidate=candidate):
                if query == 0:
                    with self.assertRaises(ValueError):
                        find_pair_candidates(self.item([candidate], [22]), query, 22)
                else:
                    self.assertEqual(find_pair_candidates(
                        self.item([candidate], [22]), query, 22), [])

    def test_malformed_mixed_socket_rejected_entirely(self):
        for bad in (True, "11", None, -2, 11.0):
            with self.subTest(bad=repr(bad)):
                self.assertEqual(find_pair_candidates(
                    self.item([11, bad], [22]), 11, 22), [])

    def test_bad_socket_index_does_not_produce_structural_pair(self):
        for index in (True, -1, "2", 2.0, None):
            with self.subTest(index=repr(index)):
                self.assertEqual(find_pair_candidates(
                    self.item([11], [22], left_index=index), 11, 22), [])

    def test_current_roll_and_visibility_filters_preserve_integrity(self):
        good = self.item([11], [22])
        self.assertEqual(len(find_pair_candidates(
            good, 11, 22, current_roll_only=True, default_visible_only=True)), 1)
        bad = self.item([11, False], [22])
        self.assertEqual(find_pair_candidates(
            bad, 11, 22, current_roll_only=True, default_visible_only=True), [])

    def test_malformed_plug_container_is_not_evidence(self):
        for plugs in (None, "11", 11, {"plug": 11}):
            with self.subTest(plugs=repr(plugs)):
                self.assertEqual(find_pair_candidates(
                    self.item(plugs, [22]), 11, 22), [])


if __name__ == "__main__":
    unittest.main()
