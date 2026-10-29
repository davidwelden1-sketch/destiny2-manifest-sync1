import unittest

from scripts.audit_weapon_socket_roles import audit_roles


class TestWeaponSocketRoleEvidence(unittest.TestCase):
    def setUp(self):
        self.index = [{
            "item_hash": 100, "name": "Synthetic Weapon", "item_type": 3,
            "sockets": [
                {"socket_index": 0, "default_visible": True,
                 "randomized_candidate_plug_hashes": [10, 11]},
                {"socket_index": 1, "default_visible": True,
                 "randomized_candidate_plug_hashes": [12]},
                {"socket_index": 2, "default_visible": False,
                 "randomized_candidate_plug_hashes": [13]},
            ],
        }]
        self.items = [
            {"hash": 10, "plugCategoryIdentifier": "barrels"},
            {"hash": 11, "plugCategoryIdentifier": "barrels"},
            {"hash": 12, "plugCategoryIdentifier": "frames"},
            {"hash": 13, "plugCategoryIdentifier": "v300.weapon.damage_type.energy"},
        ]

    def test_explicit_component_labels_do_not_certify_traits(self):
        report = audit_roles(self.index, self.items, "test")
        self.assertEqual(
            report["randomized_weapon_socket_role_evidence_counts"],
            {"explicit_component_labels_only": 2, "unclassified_or_mixed_role": 1})
        self.assertEqual(report["unclassified_memberships_by_identifier"], {"frames": 1})
        self.assertEqual(report["randomized_weapon_plug_memberships_by_identifier"]["barrels"], 2)

    def test_elemental_socket_remains_component_even_when_hidden(self):
        report = audit_roles(self.index, self.items, "test")
        self.assertTrue(any(row["socket_index"] == 2 and
                            row["role_evidence_state"] == "explicit_component_labels_only"
                            for row in report["investigation_examples"]))

    def test_unknown_category_fails_closed(self):
        self.items[0].pop("plugCategoryIdentifier")
        report = audit_roles(self.index, self.items, "test")
        self.assertEqual(
            report["randomized_weapon_socket_role_evidence_counts"]
            ["unknown_missing_category"], 1)
        self.assertEqual(report["unclassified_memberships_by_identifier"]["<missing>"], 1)

    def test_mixed_component_and_ambiguous_not_certified(self):
        self.items[1]["plugCategoryIdentifier"] = "frames"
        report = audit_roles(self.index, self.items, "test")
        self.assertEqual(
            report["randomized_weapon_socket_role_evidence_counts"]
            ["unclassified_or_mixed_role"], 2)

    def test_nonweapons_excluded(self):
        self.index[0]["item_type"] = 2
        report = audit_roles(self.index, self.items, "test")
        self.assertEqual(report["randomized_weapon_socket_role_evidence_counts"], {})

    def test_boolean_hash_not_accepted_as_item_definition(self):
        self.index[0]["sockets"][0]["randomized_candidate_plug_hashes"] = [True]
        report = audit_roles(self.index, self.items, "test")
        self.assertEqual(
            report["randomized_weapon_socket_role_evidence_counts"]
            ["unknown_missing_category"], 1)

    def test_no_randomized_candidates_ignored(self):
        self.index[0]["sockets"][0]["randomized_candidate_plug_hashes"] = []
        report = audit_roles(self.index, self.items, "test")
        self.assertEqual(sum(report["randomized_weapon_socket_role_evidence_counts"].values()), 2)


if __name__ == "__main__":
    unittest.main()
