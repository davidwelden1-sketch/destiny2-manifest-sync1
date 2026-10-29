import unittest
from simulator.weapon_legality import check_pair, check_socket_membership

class WeaponLegalityTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {100: {"sockets": {2: (11,), 3: (22,)}},
                          101: {"sockets": {2: (22,), 3: (11,)}}}

    def test_exact_hash_pair(self):
        self.assertTrue(check_pair(100, 2, 11, 3, 22, self.inventory)["possible"])
        self.assertFalse(check_pair(100, 2, 11, 3, 22, self.inventory)["certified_roll"])

    def test_no_cross_variant_merge(self):
        self.assertFalse(check_pair(100, 2, 22, 3, 11, self.inventory)["possible"])

    def test_missing_hash(self):
        self.assertFalse(check_socket_membership(999, 2, 11, self.inventory)["possible"])

    def test_boolean_hash_rejected(self):
        with self.assertRaises(ValueError):
            check_socket_membership(True, 2, 11, self.inventory)

    def test_malformed_socket_fails_closed(self):
        bad = {100: {"sockets": {2: "not-a-plug-list"}}}
        self.assertFalse(check_socket_membership(100, 2, 11, bad)["possible"])

    def test_same_socket(self):
        self.assertFalse(check_pair(100, 2, 11, 2, 11, self.inventory)["possible"])

if __name__ == "__main__":
    unittest.main()
