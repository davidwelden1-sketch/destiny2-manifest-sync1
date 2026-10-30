import unittest

from scripts.audit_roll_observations import audit_roll_observations


class ExactRollObservationAuditTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "manifest_version": "manifest-new",
            "per_exact_socket_path": [
                {"item_hash": 100, "weapon_name": "Variant A",
                 "perk_a_hash": 201, "perk_b_hash": 202,
                 "a_socket_index": 3, "b_socket_index": 4},
                {"item_hash": 101, "weapon_name": "Variant A",
                 "perk_a_hash": 201, "perk_b_hash": 202,
                 "a_socket_index": 4, "b_socket_index": 3},
            ],
        }
        self.checked = "2026-10-30T16:20:00Z"

    def observation(self, **changes):
        o = {
            "evidence_id": "capture-1",
            "item_hash": 100, "perk_a_hash": 201, "perk_b_hash": 202,
            "a_socket_index": 3, "b_socket_index": 4,
            "source_kind": "gameplay_drop_capture",
            "source_url": "https://example.org/capture/1",
            "observed_at_utc": "2026-10-29T10:00:00Z",
            "manifest_version": "manifest-new",
        }
        o.update(changes)
        return o

    def test_empty_observations_do_not_certify_manifest_membership(self):
        result = audit_roll_observations(self.report, [], self.checked)
        self.assertEqual(result["manifest_exact_socket_paths"], 2)
        self.assertEqual(result["historically_observed_paths"], 0)
        self.assertTrue(all(row["roll_legality"] == "unverified"
                            and row["current_acquisition"] == "unverified"
                            for row in result["per_exact_socket_path"]))

    def test_exact_variant_and_socket_order_only(self):
        result = audit_roll_observations(self.report, [self.observation()], self.checked)
        self.assertEqual(result["historically_observed_paths"], 1)
        self.assertEqual([row["historical_exact_path_observation"]
                          for row in result["per_exact_socket_path"]], [True, False])
        self.assertEqual(result["per_exact_socket_path"][0]["observations"][0]
                         ["evidence_grade"], "unverified_external_capture")
        self.assertEqual(result["per_exact_socket_path"][0]["enhanced_perk_legality"],
                         "unverified")

    def test_reverse_orientation_does_not_cross_match(self):
        result = audit_roll_observations(self.report, [
            self.observation(a_socket_index=4, b_socket_index=3)], self.checked)
        self.assertEqual(result["historically_observed_paths"], 0)
        self.assertEqual(result["unmatched_evidence_ids"], ["capture-1"])

    def test_same_name_other_item_hash_does_not_cross_match(self):
        result = audit_roll_observations(self.report, [
            self.observation(item_hash=999)], self.checked)
        self.assertEqual(result["historically_observed_paths"], 0)

    def test_old_manifest_capture_is_historical_only(self):
        result = audit_roll_observations(self.report, [
            self.observation(manifest_version="manifest-old")], self.checked)
        e = result["per_exact_socket_path"][0]["observations"][0]
        self.assertFalse(e["same_manifest_version"])
        self.assertEqual(result["per_exact_socket_path"][0]["roll_legality"],
                         "unverified")

    def test_future_capture_rejected(self):
        with self.assertRaisesRegex(ValueError, "Future observation"):
            audit_roll_observations(self.report, [
                self.observation(observed_at_utc="2026-10-31T00:00:00Z")],
                self.checked)

    def test_duplicate_evidence_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate evidence_id"):
            audit_roll_observations(self.report, [
                self.observation(), self.observation(item_hash=101)], self.checked)

    def test_malformed_or_untrusted_capture_rejected(self):
        for changes in (
            {"item_hash": True},
            {"a_socket_index": 3, "b_socket_index": 3},
            {"source_url": "http://example.org/capture"},
            {"source_kind": "random_website"},
            {"observed_at_utc": "yesterday"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                audit_roll_observations(self.report, [self.observation(**changes)],
                                        self.checked)

    def test_duplicate_manifest_path_rejected(self):
        report = {**self.report,
                  "per_exact_socket_path": [self.report["per_exact_socket_path"][0]] * 2}
        with self.assertRaisesRegex(ValueError, "Duplicate exact socket path"):
            audit_roll_observations(report, [], self.checked)


if __name__ == "__main__":
    unittest.main()
