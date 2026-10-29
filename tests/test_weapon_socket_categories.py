import unittest

from scripts.audit_weapon_socket_categories import audit_categories


class TestWeaponSocketCategoryAudit(unittest.TestCase):
    def setUp(self):
        self.index = [{
            "item_hash": 10, "name": "Example", "item_type": 3,
            "sockets": [{
                "socket_index": 2, "socket_type_hash": 99,
                "default_visible": False,
                "randomized_candidate_plug_hashes": [20, 21],
            }],
        }]
        self.items = [
            {"hash": 20, "name": "Trait", "plugCategoryHash": 123,
             "plugCategoryIdentifier": "weapon.perk"},
            {"hash": 21, "name": "Element", "plugCategoryHash": 456,
             "plugCategoryIdentifier": "weapon.element"},
        ]
        self.types = {"99": {"plugWhitelist": [{"categoryHash": 123}]}}

    def test_whitelist_match_and_mismatch_are_separate(self):
        report = audit_categories(self.index, self.items, self.types, "v")
        counts = report["weapon_randomized_plug_memberships_by_category_compatibility"]
        self.assertEqual(counts["compatible_whitelist"], 1)
        self.assertEqual(counts["category_not_whitelisted"], 1)
        self.assertEqual(len(report["hidden_default_socket_examples"]), 2)

    def test_empty_whitelist_allows_both(self):
        report = audit_categories(self.index, self.items,
                                  {"99": {"plugWhitelist": []}}, "v")
        self.assertEqual(report["weapon_randomized_plug_memberships_by_category_compatibility"],
                         {"compatible_empty_whitelist": 2})

    def test_missing_socket_type_is_unknown(self):
        report = audit_categories(self.index, self.items, {}, "v")
        self.assertEqual(report["weapon_randomized_plug_memberships_by_category_compatibility"],
                         {"unknown_socket_type_or_whitelist": 2})

    def test_malformed_whitelist_is_unknown_not_compatible(self):
        report = audit_categories(self.index, self.items,
                                  {"99": {"plugWhitelist": [{"categoryHash": True}]}}, "v")
        self.assertEqual(report["weapon_randomized_plug_memberships_by_category_compatibility"],
                         {"unknown_socket_type_or_whitelist": 2})

    def test_missing_plug_category_is_unknown(self):
        self.items[0].pop("plugCategoryHash")
        report = audit_categories(self.index, self.items, self.types, "v")
        self.assertEqual(report["weapon_randomized_plug_memberships_by_category_compatibility"]
                         ["unknown_plug_category"], 1)

    def test_missing_plug_definition_is_not_whitelisted(self):
        self.items.pop()
        report = audit_categories(self.index, self.items, self.types, "v")
        self.assertEqual(report["weapon_randomized_plug_memberships_by_category_compatibility"]
                         ["missing_plug_definition"], 1)

    def test_armor_excluded(self):
        self.index[0]["item_type"] = 2
        report = audit_categories(self.index, self.items, self.types, "v")
        self.assertEqual(report["weapon_randomized_plug_memberships_by_category_compatibility"], {})


if __name__ == "__main__":
    unittest.main()
