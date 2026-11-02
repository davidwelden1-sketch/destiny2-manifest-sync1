"""Synthetic exact-hash pair evidence tests; no Destiny gameplay measurement."""
import copy
import unittest

from simulator.weapon_pair_evidence_index import query_pair


def socket(slot, *, current=(), retired=(), unknown=()):
    all_plugs = list(current) + list(retired) + list(unknown)
    return {
        "socket_index": slot,
        "randomized_plug_hashes": all_plugs,
        "explicit_current_flag_plug_hashes": list(current),
        "explicit_noncurrent_flag_plug_hashes": list(retired),
        "unknown_current_flag_plug_hashes": list(unknown),
        "randomized_plug_set_hash": 500 + slot,
    }


def fixture():
    source = {"url": "https://www.bungie.net/common/destiny2_content/json/en/example.json",
              "sha256": "a" * 64}
    return {
        "schema_version": "1.0.0",
        "dataset_id": "vaeltrion:weapon-structural-evidence",
        "manifest_version": "synthetic-v1",
        "retrieved_at_utc": "2026-11-02T10:20:00Z",
        "provenance": {
            "publisher": "Bungie",
            "inventory_definition": source,
            "plug_set_definition": source,
            "evidence_grade": "official_manifest_structural_only",
        },
        "weapon_count": 2,
        "weapons": [
            {"id": "d2:weapon:100", "item_hash": 100, "display_name": "Variant",
             "sockets": [socket(2, current=(11,), retired=(33,)),
                         socket(3, current=(22,), unknown=(44,))]},
            {"id": "d2:weapon:101", "item_hash": 101, "display_name": "Variant",
             "sockets": [socket(2, current=(22,)), socket(3, current=(11,))]},
        ],
    }


def run(index=None, **changes):
    args = dict(item_hash=100, plug_a=11, plug_b=22,
                expected_manifest_version="synthetic-v1")
    args.update(changes)
    return query_pair(fixture() if index is None else index, **args)


class WeaponPairEvidenceTests(unittest.TestCase):
    def test_current_flags_are_not_roll_certification(self):
        result = run()
        self.assertTrue(result["structural_candidate"])
        self.assertTrue(result["both_explicit_current_flags"])
        self.assertFalse(result["certified_for_app_build_recommendation"])
        self.assertIsNone(result["current_obtainable_roll"])
        self.assertIsNone(result["enhanced_perk_legal"])
        self.assertIsNone(result["patch_version"])
        self.assertFalse(result["patch_version_verified"])
        self.assertEqual(result["provenance"]["publisher"], "Bungie")
        self.assertEqual(result["provenance"]["inventory_definition"]["sha256"], "a" * 64)
        self.assertIsNone(result["pve_boss_dps_measured"])
        self.assertIsNone(result["pvp_guardian_ttk_measured"])

    def test_exact_variant_not_name_merge(self):
        result = run(plug_a=11, plug_b=22, item_hash=101)
        self.assertTrue(result["structural_candidate"])
        self.assertEqual(result["candidate_socket_pairs"][0]["plug_a_socket_index"], 3)
        self.assertEqual(result["candidate_socket_pairs"][0]["plug_b_socket_index"], 2)

    def test_no_cross_variant_false_positive(self):
        index = fixture()
        index["weapons"][0]["sockets"][1] = socket(3, current=(77,))
        self.assertFalse(run(index)["structural_candidate"])

    def test_same_socket_not_pair(self):
        index = fixture()
        index["weapons"][0]["sockets"][0] = socket(2, current=(11, 22))
        index["weapons"][0]["sockets"][1] = socket(3, current=(77,))
        self.assertEqual(run(index)["status"], "no_distinct_socket_membership")

    def test_unknown_flag_never_treated_as_current(self):
        result = run(plug_b=44)
        self.assertTrue(result["structural_candidate"])
        self.assertFalse(result["both_explicit_current_flags"])
        self.assertEqual(result["candidate_socket_pairs"][0]["plug_b_state"], "unknown_current_flag")

    def test_noncurrent_flag_never_treated_as_current(self):
        result = run(plug_a=33)
        self.assertTrue(result["structural_candidate"])
        self.assertFalse(result["both_explicit_current_flags"])

    def test_version_mismatch_fails_closed(self):
        result = run(expected_manifest_version="newer-version")
        self.assertEqual(result["status"], "manifest_version_mismatch")
        self.assertFalse(result["structural_candidate"])

    def test_missing_item_fails_closed(self):
        self.assertEqual(run(item_hash=999)["status"], "item_hash_not_in_index")

    def test_reject_boolean_hashes(self):
        for key in ("item_hash", "plug_a", "plug_b"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                run(**{key: True})

    def test_reject_duplicate_weapon_hash(self):
        index = fixture()
        index["weapons"][1]["item_hash"] = 100
        index["weapons"][1]["id"] = "d2:weapon:100"
        with self.assertRaises(ValueError):
            run(index)

    def test_reject_bad_stable_id(self):
        index = fixture()
        index["weapons"][0]["id"] = "d2:weapon:101"
        with self.assertRaises(ValueError):
            run(index)

    def test_reject_bad_source_digest_and_host(self):
        for field, value in (("sha256", "no-digest"), ("url", "https://evil.example/manifest")):
            index = fixture()
            index["provenance"]["inventory_definition"] = dict(index["provenance"]["inventory_definition"])
            index["provenance"]["inventory_definition"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                run(index)

    def test_reject_duplicate_socket_index(self):
        index = fixture()
        index["weapons"][0]["sockets"][1]["socket_index"] = 2
        with self.assertRaises(ValueError):
            run(index)

    def test_reject_incomplete_and_overlapping_partitions(self):
        for mode in ("missing", "overlap"):
            index = fixture()
            slot = index["weapons"][0]["sockets"][0]
            if mode == "missing":
                slot["randomized_plug_hashes"].append(999)
            else:
                slot["explicit_noncurrent_flag_plug_hashes"].append(11)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                run(index)

    def test_reject_boolean_plug_and_missing_plugset(self):
        for mode in ("boolean", "missing_plugset"):
            index = fixture()
            slot = index["weapons"][0]["sockets"][0]
            if mode == "boolean":
                slot["explicit_current_flag_plug_hashes"][0] = True
            else:
                slot["randomized_plug_set_hash"] = None
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                run(index)

    def test_reject_bad_timestamp_and_catalog_count(self):
        for mode in ("naive", "count"):
            index = fixture()
            if mode == "naive":
                index["retrieved_at_utc"] = "2026-11-02T10:20:00"
            else:
                index["weapon_count"] = 3
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                run(index)

    def test_reject_identical_query_plugs(self):
        with self.assertRaises(ValueError):
            run(plug_b=11)

    def test_multiple_socket_candidates_are_deterministic(self):
        index = fixture()
        index["weapons"][0]["sockets"].append(socket(4, current=(11,)))
        index["weapons"][0]["sockets"].append(socket(5, current=(22,)))
        result = run(index)
        self.assertEqual(
            [(row["plug_a_socket_index"], row["plug_b_socket_index"])
             for row in result["candidate_socket_pairs"]],
            [(2, 3), (2, 5), (4, 3), (4, 5)],
        )


    def test_full_snapshot_flag_counts_are_exposed(self):
        result = run()
        diagnostic = result["current_flag_filter_diagnostic"]
        self.assertEqual(diagnostic["randomized_memberships"], 6)
        self.assertEqual(diagnostic["explicit_current_flag_memberships"], 4)
        self.assertEqual(diagnostic["explicit_noncurrent_flag_memberships"], 1)
        self.assertEqual(diagnostic["unknown_current_flag_memberships"], 1)
        self.assertTrue(diagnostic["current_flag_filter_discriminates_retired_memberships"])
        self.assertFalse(diagnostic["current_obtainability_certified"])
        self.assertFalse(diagnostic["enhanced_perk_legality_certified"])

    def test_all_current_flags_are_non_discriminating(self):
        index = fixture()
        index["weapons"][0]["sockets"] = [
            socket(2, current=(11, 33)), socket(3, current=(22, 44))]
        result = run(index)
        diagnostic = result["current_flag_filter_diagnostic"]
        self.assertEqual(diagnostic["randomized_memberships"], 6)
        self.assertTrue(diagnostic["all_randomized_memberships_flagged_current"])
        self.assertFalse(diagnostic["current_flag_filter_discriminates_retired_memberships"])
        self.assertTrue(result["both_explicit_current_flags"])
        self.assertIsNone(result["current_obtainable_roll"])

    def test_unknown_without_retired_does_not_discriminate_retired(self):
        index = fixture()
        index["weapons"][0]["sockets"][0] = socket(
            2, current=(11,), unknown=(33,))
        diagnostic = run(index)["current_flag_filter_diagnostic"]
        self.assertFalse(diagnostic["current_flag_filter_discriminates_retired_memberships"])
        self.assertFalse(diagnostic["all_randomized_memberships_flagged_current"])

    def test_empty_snapshot_is_not_all_current(self):
        index = fixture()
        index["weapons"][0]["sockets"] = [socket(2), socket(3)]
        index["weapons"][1]["sockets"] = [socket(2), socket(3)]
        result = run(index)
        diagnostic = result["current_flag_filter_diagnostic"]
        self.assertEqual(diagnostic["randomized_memberships"], 0)
        self.assertFalse(diagnostic["all_randomized_memberships_flagged_current"])
        self.assertFalse(diagnostic["current_flag_filter_discriminates_retired_memberships"])

    def test_corrupt_unqueried_variant_fails_closed(self):
        index = fixture()
        index["weapons"][1]["sockets"][0][
            "explicit_noncurrent_flag_plug_hashes"].append(22)
        with self.assertRaises(ValueError):
            run(index)

    def test_version_mismatch_and_missing_hash_have_no_diagnostic(self):
        self.assertIsNone(run(expected_manifest_version="wrong")[
            "current_flag_filter_diagnostic"])
        self.assertIsNone(run(item_hash=999)[
            "current_flag_filter_diagnostic"])


if __name__ == "__main__":
    unittest.main()
