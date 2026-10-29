import unittest

from scripts.audit_weapon_variants import audit_variants, randomized_signature


def weapon(h, name, sockets):
    return {"item_hash": h, "name": name, "item_type": 3, "sockets": sockets}


def socket(index, plugs, socket_type=7):
    return {"socket_index": index, "socket_type_hash": socket_type,
            "randomized_candidate_plug_hashes": plugs}


class TestWeaponVariantCatalogAudit(unittest.TestCase):
    def test_separates_divergent_and_identical_names(self):
        items = [weapon(1, "  Lotus ", [socket(3, [10, 20])]),
                 weapon(2, "lotus", [socket(3, [10, 30])]),
                 weapon(3, "Same", [socket(3, [40, 50])]),
                 weapon(4, "SAME", [socket(3, [50, 40])]),
                 weapon(5, "Single", [socket(3, [60])]),
                 {"item_hash": 6, "name": "Lotus", "item_type": 2, "sockets": []}]
        result = audit_variants(items, "test-version")
        self.assertEqual(result["indexed_weapon_definitions"], 5)
        self.assertEqual(result["same_name_variant_groups"], 2)
        self.assertEqual(result["divergent_variant_groups"], 1)
        self.assertEqual(result["identical_signature_variant_groups"], 1)
        self.assertEqual(result["groups"][0]["item_hashes"], [1, 2])
        self.assertIn("do not certify", result["interpretation"])

    def test_same_socket_index_but_different_type_is_divergent(self):
        report = audit_variants([weapon(1, "A", [socket(3, [10], 8)]),
                                 weapon(2, "A", [socket(3, [10], 9)])], "x")
        self.assertEqual(report["divergent_variant_groups"], 1)

    def test_empty_randomized_socket_distinguished(self):
        report = audit_variants([weapon(1, "A", []), weapon(2, "A", [socket(3, [10])])], "x")
        self.assertTrue(report["groups"][0]["contains_no_randomized_sockets"])
        self.assertEqual(report["divergent_variant_groups"], 1)

    def test_reordered_and_duplicate_plugs_do_not_fake_divergence(self):
        self.assertEqual(randomized_signature(weapon(1, "A", [socket(3, [2, 1, 1])])),
                         randomized_signature(weapon(2, "A", [socket(3, [1, 2])])))

    def test_duplicate_or_invalid_hash_fails_closed(self):
        for invalid in [0, True, -1]:
            with self.assertRaises(ValueError):
                audit_variants([weapon(invalid, "A", [])], "x")
        with self.assertRaises(ValueError):
            audit_variants([weapon(1, "A", []), weapon(1, "B", [])], "x")


if __name__ == "__main__":
    unittest.main()
