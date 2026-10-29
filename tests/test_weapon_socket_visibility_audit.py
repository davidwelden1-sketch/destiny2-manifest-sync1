"""Synthetic regression tests for definition-level randomized socket visibility audit."""
import unittest

from scripts.audit_weapon_socket_visibility import audit_visibility


class TestWeaponSocketVisibilityAudit(unittest.TestCase):
    def setUp(self):
        self.index = [
            {"item_type": 3, "item_hash": 200, "name": "Hidden weapon",
             "sockets": [
                 {"socket_index": 0, "default_visible": False,
                  "socket_type_hash": 17, "plug_sources": 4,
                  "randomized_candidate_plug_hashes": [8, 3],
                  "currently_rollable_randomized_candidate_plug_hashes": [3],
                  "plugset_references": [{"field": "randomizedPlugSetHash", "hash": 51},
                                         {"field": "reusablePlugSetHash", "hash": 52}]},
                 {"socket_index": 1, "default_visible": True,
                  "randomized_candidate_plug_hashes": [5]}]},
            {"item_type": 3, "item_hash": 100, "name": "Unknown weapon",
             "sockets": [{"socket_index": 0, "default_visible": None,
                          "randomized_candidate_plug_hashes": [6]}]},
            {"item_type": 2, "item_hash": 300, "name": "Not a weapon",
             "sockets": [{"socket_index": 0, "default_visible": False,
                          "randomized_candidate_plug_hashes": [1]}]},
        ]

    def test_counts_only_weapon_randomized_sockets(self):
        r = audit_visibility(self.index, "fixture")
        self.assertEqual(r["randomized_weapon_socket_counts"],
                         {"visible": 1, "hidden": 1, "unknown": 1})
        self.assertEqual([x["item_hash"] for x in r["exceptions"]], [100, 200])

    def test_preserves_exact_hash_and_provenance(self):
        row = audit_visibility(self.index, "fixture")["exceptions"][1]
        self.assertEqual(row["item_hash"], 200)
        self.assertEqual(row["socket_index"], 0)
        self.assertEqual(row["randomized_plug_hashes"], [3, 8])
        self.assertEqual(row["randomized_plugset_hashes"], [51])
        self.assertEqual(row["explicit_current_roll_count"], 1)

    def test_does_not_count_empty_nonrandomized_sockets(self):
        self.index[0]["sockets"].append({
            "socket_index": 2, "default_visible": False,
            "reusable_candidate_plug_hashes": [90]})
        r = audit_visibility(self.index, "fixture")
        self.assertEqual(r["randomized_weapon_socket_counts"]["hidden"], 1)

    def test_unknown_is_not_called_hidden(self):
        row = audit_visibility(self.index, "fixture")["exceptions"][0]
        self.assertIsNone(row["default_visible"])
        self.assertIn("Runtime item socket state", audit_visibility(self.index, "fixture")["interpretation"])


if __name__ == "__main__":
    unittest.main()
