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

    def test_duplicate_socket_index_fails_even_when_second_is_not_randomized(self):
        with self.assertRaisesRegex(ValueError, "duplicate socket index"):
            audit_variants([weapon(1, "A", [socket(3, [10]), socket(3, [])]),
                            weapon(2, "A", [socket(3, [20])])], "v")

    def test_duplicate_socket_index_with_distinct_plugs_fails(self):
        with self.assertRaises(ValueError):
            randomized_signature(weapon(1, "A", [socket(3, [10]),
                                                  socket(3, [20])]))

    def test_non_dictionary_socket_row_fails_whole_variant_audit(self):
        with self.assertRaisesRegex(ValueError, "Malformed socket"):
            audit_variants([weapon(1, "A", [socket(3, [10]), None]),
                            weapon(2, "A", [socket(3, [20])])], "v")

    def test_malformed_plug_containers_fail_closed(self):
        for bad in (None, "10", {"10": True}, 10):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                randomized_signature(weapon(1, "A", [socket(3, bad)]))

    def test_nonpositive_and_boolean_plug_hashes_fail_closed(self):
        for bad in (True, False, 0, -1, "10", 1.5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                randomized_signature(weapon(1, "A", [socket(3, [10, bad])]))

    def test_invalid_socket_index_fails_closed(self):
        for bad in (True, -1, None, "3", 1.5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                randomized_signature(weapon(1, "A", [socket(bad, [10])]))

    def test_invalid_randomized_socket_type_fails_closed(self):
        for bad in (True, -1, 0, "7", 1.5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                randomized_signature(weapon(1, "A", [socket(3, [10], bad)]))

    def test_valid_nonrandomized_sockets_remain_supported(self):
        result = audit_variants([
            weapon(1, "A", [socket(1, []), socket(3, [10, 20])]),
            weapon(2, "A", [socket(1, []), socket(3, [20, 10])]),
        ], "v")
        self.assertEqual(result["identical_signature_variant_groups"], 1)
        self.assertEqual(result["divergent_variant_groups"], 0)

    def test_duplicate_or_invalid_hash_fails_closed(self):
        for invalid in [0, True, -1]:
            with self.assertRaises(ValueError):
                audit_variants([weapon(invalid, "A", [])], "x")
        with self.assertRaises(ValueError):
            audit_variants([weapon(1, "A", []), weapon(1, "B", [])], "x")


    def test_singleton_weapon_malformed_socket_fails_game_wide_audit(self):
        # A singleton has no same-name variants but still needs valid sockets.
        with self.assertRaisesRegex(ValueError, "duplicate socket index"):
            audit_variants([weapon(1, "Unique", [socket(3, [10]),
                                                 socket(3, [20])])], "v")

    def test_singleton_weapon_invalid_plug_fails_game_wide_audit(self):
        with self.assertRaisesRegex(ValueError, "Malformed randomized plug"):
            audit_variants([weapon(1, "Unique", [socket(3, [10, True])])], "v")

    def test_singleton_weapon_valid_socket_stays_counted(self):
        report = audit_variants([weapon(1, "Unique", [socket(3, [10])])], "v")
        self.assertEqual(report["indexed_weapon_definitions"], 1)
        self.assertEqual(report["same_name_variant_groups"], 0)

    def test_malformed_item_row_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Malformed item row"):
            audit_variants([None, weapon(1, "Unique", [socket(3, [10])])], "v")

    def test_invalid_index_container_fails_closed(self):
        for invalid in (None, {"item": 1}, "not an index"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                audit_variants(invalid, "v")


if __name__ == "__main__":
    unittest.main()
