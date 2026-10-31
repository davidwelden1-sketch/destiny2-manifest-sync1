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

    def correction(self, **changes):
        c = {
            "correction_id": "patch-1",
            "item_hash": 100, "perk_a_hash": 201, "perk_b_hash": 202,
            "a_socket_index": 3, "b_socket_index": 4,
            "effective_at_utc": "2026-10-30T12:00:00Z",
            "source_url": "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2",
            "correction_action": "perk_replaced",
        }
        c.update(changes)
        return c

    def test_patch_correction_flags_prior_capture_without_certifying_roll(self):
        result = audit_roll_observations(
            self.report, [self.observation()], self.checked,
            corrections=[self.correction()])
        first, second = result["per_exact_socket_path"]
        self.assertTrue(first["post_patch_revalidation_required"])
        self.assertEqual(first["observations_predating_patch_correction"], ["capture-1"])
        self.assertEqual(first["roll_legality"], "unverified")
        self.assertFalse(second["post_patch_revalidation_required"])

    def test_correction_does_not_cross_weapon_hash_or_reverse_socket(self):
        result = audit_roll_observations(
            self.report, [self.observation()], self.checked,
            corrections=[self.correction(a_socket_index=4, b_socket_index=3)])
        self.assertFalse(result["per_exact_socket_path"][0]
                         ["post_patch_revalidation_required"])
        self.assertEqual(result["unmatched_correction_ids"], ["patch-1"])

    def test_capture_after_correction_is_not_predating_evidence(self):
        result = audit_roll_observations(
            self.report, [self.observation(observed_at_utc="2026-10-30T14:00:00Z")],
            self.checked, corrections=[self.correction()])
        first = result["per_exact_socket_path"][0]
        self.assertTrue(first["post_patch_revalidation_required"])
        self.assertEqual(first["observations_predating_patch_correction"], [])
        self.assertEqual(first["current_acquisition"], "unverified")

    def test_patch_claim_requires_valid_metadata_and_no_future_effective_date(self):
        for changes in (
            {"correction_id": ""},
            {"source_url": "https://example.org/fake-patch"},
            {"correction_action": "buffed"},
            {"effective_at_utc": "2026-11-01T00:00:00Z"},
            {"item_hash": True},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                audit_roll_observations(self.report, [], self.checked,
                                        corrections=[self.correction(**changes)])

    def test_duplicate_patch_ids_rejected_and_no_claims_is_backward_compatible(self):
        with self.assertRaisesRegex(ValueError, "duplicate correction_id"):
            audit_roll_observations(self.report, [], self.checked,
                                    corrections=[self.correction(), self.correction()])
        result = audit_roll_observations(self.report, [], self.checked)
        self.assertEqual(result["unmatched_correction_ids"], [])
        self.assertFalse(result["per_exact_socket_path"][0]
                         ["post_patch_revalidation_required"])



    def loot_claim(self, **changes):
        claim = {
            "item_hash": 100, "source_kind": "raid",
            "pre_edge_of_fate": True, "craftable": True,
            "observation_date": "2026-06-08",
            "observed_manifest_version": "manifest-old",
            "source_url": "https://example.org/raid-observation",
            "activity": "pve",
        }
        claim.update(changes)
        return claim

    def test_exact_hash_raid_freshness_not_shared_by_same_name(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim()])
        first, second = result["per_exact_socket_path"]
        self.assertTrue(first["loot_source_freshness"]["perk_pool_revalidation_required"])
        self.assertIsNone(second["loot_source_freshness"])
        self.assertEqual(first["roll_legality"], "unverified")

    def test_loot_source_manifest_mismatch_is_explicit(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim()])
        row = result["per_exact_socket_path"][0]
        self.assertEqual(row["loot_source_freshness"]["manifest_version_status"],
                         "version_mismatch_revalidate")
        self.assertFalse(row["loot_source_freshness"]["claim_authenticated"])

    def test_dungeon_origin_trait_freshness_is_distinct(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim(source_kind="dungeon",
                                                craftable=False)])
        row = result["per_exact_socket_path"][0]["loot_source_freshness"]
        self.assertTrue(row["origin_trait_revalidation_required"])
        self.assertFalse(row["perk_pool_revalidation_required"])

    def test_post_patch_claim_does_not_certify_enhancement(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim(
                observation_date="2026-10-29",
                observed_manifest_version="manifest-new")])
        row = result["per_exact_socket_path"][0]
        self.assertFalse(row["loot_source_freshness"]["perk_pool_revalidation_required"])
        self.assertFalse(row["loot_source_freshness"]["enhanced_perk_legality_verified"])
        self.assertEqual(row["enhanced_perk_legality"], "unverified")

    def test_unknown_raid_age_fails_closed_without_inferred_legality(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim(pre_edge_of_fate=None)])
        row = result["per_exact_socket_path"][0]["loot_source_freshness"]
        self.assertEqual(row["official_source_level_changes"], [])
        self.assertFalse(row["current_exact_perk_pair_verified"])

    def test_unmatched_source_hash_reported_without_cross_match(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim(item_hash=999)])
        self.assertEqual(result["unmatched_loot_source_item_hashes"], [999])
        self.assertTrue(all(row["loot_source_freshness"] is None
                            for row in result["per_exact_socket_path"]))

    def test_duplicate_source_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate loot source"):
            audit_roll_observations(
                self.report, [], self.checked,
                loot_source_claims=[self.loot_claim(), self.loot_claim(
                    observation_date="2026-06-10")])

    def test_future_source_observation_rejected(self):
        with self.assertRaisesRegex(ValueError, "Future loot source"):
            audit_roll_observations(
                self.report, [], self.checked,
                loot_source_claims=[self.loot_claim(observation_date="2026-11-01")])

    def test_invalid_source_metadata_rejected(self):
        for changes in (
            {"item_hash": True}, {"source_url": "http://example.org"},
            {"source_kind": "unsupported"}, {"observation_date": "2026-02-30"},
            {"activity": "unknown"}, {"pre_edge_of_fate": "yes"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                audit_roll_observations(
                    self.report, [], self.checked,
                    loot_source_claims=[self.loot_claim(**changes)])

    def test_optional_source_claims_backward_compatible(self):
        result = audit_roll_observations(self.report, [], self.checked)
        self.assertEqual(result["unmatched_loot_source_item_hashes"], [])
        self.assertTrue(all(row["loot_source_freshness"] is None
                            for row in result["per_exact_socket_path"]))

    def test_source_claim_does_not_override_pvp_artifact_constraint(self):
        result = audit_roll_observations(
            self.report, [], self.checked,
            loot_source_claims=[self.loot_claim(activity="trials")])
        row = result["per_exact_socket_path"][0]["loot_source_freshness"]
        self.assertIs(row["artifact_enabled"], False)
        self.assertFalse(row["current_artifact_selection_verified"])



if __name__ == "__main__":
    unittest.main()
