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


    def test_duplicate_socket_index_fails_closed_for_entire_weapon(self):
        rows = self.item([11], [22])
        rows[0]["sockets"].append({
            "socket_index": 2,
            "randomized_candidate_plug_hashes": [99],
            "currently_rollable_randomized_candidate_plug_hashes": [99],
            "default_visible": True,
            "plugset_references": [],
        })
        # A second definition for socket 2 cannot be merged into a legal roll.
        for current, visible in ((False, False), (True, True)):
            with self.subTest(current=current, visible=visible):
                self.assertEqual(find_pair_candidates(
                    rows, 11, 22, current_roll_only=current,
                    default_visible_only=visible), [])

    def test_distinct_socket_indices_still_produce_one_pair(self):
        rows = self.item([11], [22], left_index=1, right_index=5)
        result = find_pair_candidates(rows, 11, 22)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["socket_pairs"][0]["a_socket_index"], 1)
        self.assertEqual(result[0]["socket_pairs"][0]["b_socket_index"], 5)

    def test_duplicate_item_hash_rejected_even_if_socket_data_disagree(self):
        rows = self.item([11], [22])
        duplicate = self.item([11], [99])[0]
        self.assertEqual(find_pair_candidates(rows + [duplicate], 11, 22), [])

    def test_invalid_item_identity_and_shape_cannot_create_matches(self):
        for invalid in (True, 0, -1, "100", 100.0, None):
            with self.subTest(identity=repr(invalid)):
                rows = self.item([11], [22])
                rows[0]["item_hash"] = invalid
                self.assertEqual(find_pair_candidates(rows, 11, 22), [])
        self.assertEqual(find_pair_candidates([None, "invalid"], 11, 22), [])
        with self.assertRaises(ValueError):
            find_pair_candidates({"item_hash": 100}, 11, 22)

    def test_bad_socket_container_is_not_a_roll(self):
        for invalid in (None, {}, "socket", 12):
            with self.subTest(container=repr(invalid)):
                rows = self.item([11], [22])
                rows[0]["sockets"] = invalid
                self.assertEqual(find_pair_candidates(rows, 11, 22), [])

    def test_malformed_provenance_rejected_not_silently_ignored(self):
        for invalid in (None, "randomized", {"field": "randomizedPlugSetHash"},
                        [None], [{"field": "randomizedPlugSetHash", "hash": True}],
                        [{"field": "randomizedPlugSetHash", "hash": -1}],
                        [{"field": "fake", "hash": 123}]):
            with self.subTest(provenance=repr(invalid)):
                rows = self.item([11], [22])
                rows[0]["sockets"][0]["plugset_references"] = invalid
                self.assertEqual(find_pair_candidates(rows, 11, 22), [])

    def test_valid_randomized_source_hash_survives(self):
        rows = self.item([11], [22])
        rows[0]["sockets"][0]["plugset_references"] = [
            {"field": "randomizedPlugSetHash", "hash": 10001}]
        rows[0]["sockets"][1]["plugset_references"] = [
            {"field": "randomizedPlugSetHash", "hash": 10002}]
        matches = find_pair_candidates(rows, 11, 22)
        self.assertEqual(len(matches), 1)
        pair = matches[0]["socket_pairs"][0]
        self.assertEqual(pair["a_randomized_set_hashes"], [10001])
        self.assertEqual(pair["b_randomized_set_hashes"], [10002])


    def test_nondictionary_socket_row_invalidates_entire_weapon(self):
        # Do not silently ignore corrupt extraction rows and promote the
        # two surviving sockets into a falsely trustworthy pair.
        for invalid in (None, True, 3, "bad socket", [11, 22]):
            with self.subTest(invalid=repr(invalid)):
                rows = self.item([11], [22])
                rows[0]["sockets"].append(invalid)
                self.assertEqual(find_pair_candidates(rows, 11, 22), [])
                self.assertEqual(find_pair_candidates(
                    rows, 11, 22, current_roll_only=True,
                    default_visible_only=True), [])

    def test_valid_extra_nonmatching_socket_remains_allowed(self):
        rows = self.item([11], [22])
        rows[0]["sockets"].append({
            "socket_index": 4,
            "randomized_candidate_plug_hashes": [33],
            "currently_rollable_randomized_candidate_plug_hashes": [33],
            "default_visible": True,
            "plugset_references": [],
        })
        self.assertEqual(len(find_pair_candidates(rows, 11, 22)), 1)

    def test_corrupt_unrelated_socket_invalidates_whole_item(self):
        # A malformed third socket cannot be ignored while reporting the
        # first two as a trustworthy structural weapon pair.
        for bad_field, bad_value in (
            ("randomized_candidate_plug_hashes", [33, True]),
            ("randomized_candidate_plug_hashes", "33"),
            ("plugset_references", [{"field": "randomizedPlugSetHash", "hash": False}]),
            ("plugset_references", None),
        ):
            with self.subTest(field=bad_field, value=repr(bad_value)):
                rows = self.item([11], [22])
                rows[0]["sockets"].append({
                    "socket_index": 4,
                    "randomized_candidate_plug_hashes": [33],
                    "currently_rollable_randomized_candidate_plug_hashes": [33],
                    "default_visible": True,
                    "plugset_references": [],
                    bad_field: bad_value,
                })
                self.assertEqual(find_pair_candidates(rows, 11, 22), [])

    def test_corrupt_unrelated_socket_fails_closed_with_current_filters(self):
        rows = self.item([11], [22])
        rows[0]["sockets"].append({
            "socket_index": 4,
            "randomized_candidate_plug_hashes": [33],
            "currently_rollable_randomized_candidate_plug_hashes": [33, False],
            "default_visible": False,
            "plugset_references": [],
        })
        self.assertEqual(find_pair_candidates(
            rows, 11, 22, current_roll_only=True, default_visible_only=True), [])



    def test_current_roll_membership_cannot_exceed_randomized_source(self):
        rows = self.item([11], [22])
        rows[0]["sockets"][0]["currently_rollable_randomized_candidate_plug_hashes"] = [11, 99]
        # A plug flagged current but absent from its randomized source is
        # contradictory manifest evidence, not a legitimate extra roll.
        self.assertEqual(find_pair_candidates(rows, 11, 22), [])
        self.assertEqual(find_pair_candidates(rows, 11, 22, current_roll_only=True), [])

    def test_invalid_current_roll_column_fails_even_without_current_filter(self):
        for bad in (None, "11", [11, True], [11, -1], {"hash": 11}):
            with self.subTest(value=repr(bad)):
                rows = self.item([11], [22])
                rows[0]["sockets"][0]["currently_rollable_randomized_candidate_plug_hashes"] = bad
                self.assertEqual(find_pair_candidates(rows, 11, 22), [])

    def test_corrupt_unrelated_current_roll_column_invalidates_weapon(self):
        rows = self.item([11], [22])
        rows[0]["sockets"].append({
            "socket_index": 4,
            "randomized_candidate_plug_hashes": [33],
            "currently_rollable_randomized_candidate_plug_hashes": [44],
            "plugset_references": [],
        })
        self.assertEqual(find_pair_candidates(rows, 11, 22), [])

    def test_missing_current_roll_field_is_not_false_current_evidence(self):
        rows = self.item([11], [22])
        for socket in rows[0]["sockets"]:
            socket.pop("currently_rollable_randomized_candidate_plug_hashes")
        self.assertEqual(len(find_pair_candidates(rows, 11, 22)), 1)
        self.assertEqual(find_pair_candidates(rows, 11, 22, current_roll_only=True), [])


if __name__ == "__main__":
    unittest.main()
