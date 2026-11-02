"""Synthetic regression tests, not measured Destiny 2 gameplay."""
import unittest
from simulator.measurement_evidence_gate import evaluate_observation


def fixture(mode="pvp_ttk"):
    data = {"observation_id": "synthetic-control", "mode": mode,
            "patch_version": "9.7.0.6", "manifest_version": "synthetic-manifest",
            "recorded_at_utc": "2026-11-02T12:20:00Z", "sample_count": 3,
            "scenario": "Synthetic equal-range target; no buffs or damage falloff",
            "source": {"url": "https://example.org/test", "published_at_utc": "2026-11-02T12:00:00Z"},
            "inputs": {"precision_damage": "115", "body_damage": "70",
                       "target_health": "230", "rpm": 120, "hit_sequence": "PP"}}
    if mode == "pve_dps":
        data["inputs"] = {"total_damage": 120000, "duration_seconds": 10}
    if mode == "pve_dr":
        data["inputs"] = {"baseline_hit": 100, "mitigated_hit": 65}
    return data


class MeasurementEvidenceGateTests(unittest.TestCase):
    def test_pvp_exact_threshold(self):
        result = evaluate_observation(fixture())
        self.assertEqual(result["derived"]["conditional_ttk_seconds"], "0.5")
        self.assertEqual(result["derived"]["lethal_shots"], 2)
        self.assertFalse(result["certified_for_app_build_recommendation"])

    def test_pvp_nonlethal_shortfall_rejected(self):
        data = fixture()
        data["inputs"]["precision_damage"] = "114.9999999997"
        with self.assertRaises(ValueError):
            evaluate_observation(data)

    def test_pvp_post_lethal_sequence_rejected(self):
        data = fixture()
        data["inputs"]["hit_sequence"] = "PPP"
        with self.assertRaises(ValueError):
            evaluate_observation(data)

    def test_pvp_valid_mixed_sequence(self):
        data = fixture()
        data["inputs"].update(precision_damage="90", body_damage="50", hit_sequence="PPB")
        self.assertEqual(evaluate_observation(data)["derived"]["lethal_shots"], 3)

    def test_pve_dps_derived_only(self):
        result = evaluate_observation(fixture("pve_dps"))
        self.assertEqual(result["derived"]["conditional_dps"], "12000")
        self.assertFalse(result["gameplay_measurement_independently_verified"])

    def test_pve_dr_derived_only(self):
        result = evaluate_observation(fixture("pve_dr"))
        self.assertEqual(result["derived"]["conditional_dr_fraction"], "0.35")
        self.assertFalse(result["stacking_verified"])

    def test_zero_mitigated_hit_not_infinite_ehp(self):
        data = fixture("pve_dr")
        data["inputs"]["mitigated_hit"] = 0
        self.assertEqual(evaluate_observation(data)["derived"]["conditional_dr_fraction"], "1")
        self.assertFalse(evaluate_observation(data)["certified_for_app_build_recommendation"])

    def test_pve_dr_control_must_not_be_smaller(self):
        data = fixture("pve_dr")
        data["inputs"]["mitigated_hit"] = 101
        with self.assertRaises(ValueError):
            evaluate_observation(data)

    def test_reject_bad_numbers(self):
        for mode, key in (("pve_dps", "total_damage"), ("pve_dr", "baseline_hit"),
                          ("pvp_ttk", "target_health")):
            for value in (True, "NaN", "Infinity", 0, -1, None):
                with self.subTest(mode=mode, value=value), self.assertRaises(ValueError):
                    data = fixture(mode)
                    data["inputs"][key] = value
                    evaluate_observation(data)

    def test_reject_invalid_source(self):
        for url in ("http://example.org", "https://localhost/test",
                    "https://user:pass@example.org/test", "https://evil.local/x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                data = fixture()
                data["source"]["url"] = url
                evaluate_observation(data)

    def test_reject_future_publication(self):
        data = fixture()
        data["source"]["published_at_utc"] = "2026-11-03T00:00:00Z"
        with self.assertRaises(ValueError):
            evaluate_observation(data)

    def test_reject_non_utc_dates(self):
        for value in ("2026-11-02T12:20:00", "2026-11-02T13:20:00+01:00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                data = fixture()
                data["recorded_at_utc"] = value
                evaluate_observation(data)

    def test_reject_boolean_sample_count(self):
        data = fixture()
        data["sample_count"] = True
        with self.assertRaises(ValueError):
            evaluate_observation(data)

    def test_reject_invalid_id(self):
        for oid in ("../etc", "UPPER", "a b", ""):
            with self.subTest(oid=oid), self.assertRaises(ValueError):
                data = fixture()
                data["observation_id"] = oid
                evaluate_observation(data)

    def test_mode_specific_fields(self):
        for mode in ("pve_dps", "pve_dr", "pvp_ttk"):
            result = evaluate_observation(fixture(mode))
            self.assertEqual(result["id"], f"d2:observation:{mode}:synthetic-control")
            self.assertFalse(result["artifact_legality_verified"])
            self.assertFalse(result["exact_weapon_roll_legality_verified"])

    def test_bad_hit_sequence(self):
        for sequence in ("", "PPX", "P P", True):
            with self.subTest(sequence=sequence), self.assertRaises(ValueError):
                data = fixture()
                data["inputs"]["hit_sequence"] = sequence
                evaluate_observation(data)

    def test_extreme_precision_pvp_shortfall_never_rounds_to_lethal(self):
        data = fixture()
        data["inputs"]["precision_damage"] = "114.9999999999999999999999999999999999999999999"
        with self.assertRaises(ValueError):
            evaluate_observation(data)

    def test_pvp_exact_rational_ttk_140rpm(self):
        data = fixture()
        data["inputs"]["rpm"] = 140
        result = evaluate_observation(data)
        self.assertEqual(result["derived"]["conditional_ttk_exact_ratio"],
                         {"numerator": "3", "denominator": "7"})
        self.assertTrue(result["derived"]["conditional_ttk_seconds"].startswith("0.428571"))

    def test_pve_dr_extreme_near_full_not_rounded_to_one(self):
        data = fixture("pve_dr")
        data["inputs"]["baseline_hit"] = "1000000000000000000000000000000000000000000000"
        data["inputs"]["mitigated_hit"] = "1"
        result = evaluate_observation(data)
        self.assertNotEqual(result["derived"]["conditional_dr_fraction"], "1")
        self.assertEqual(result["derived"]["conditional_dr_exact_ratio"]["denominator"],
                         "1000000000000000000000000000000000000000000000")
        self.assertFalse(result["certified_for_app_build_recommendation"])

    def test_pve_dps_exact_rational_repeating(self):
        data = fixture("pve_dps")
        data["inputs"]["total_damage"] = 1
        data["inputs"]["duration_seconds"] = 3
        result = evaluate_observation(data)
        self.assertEqual(result["derived"]["conditional_dps_exact_ratio"],
                         {"numerator": "1", "denominator": "3"})
        self.assertTrue(result["derived"]["conditional_dps"].startswith("0.333333"))

    def test_pve_dr_exact_zero_and_full_controls(self):
        data = fixture("pve_dr")
        data["inputs"]["mitigated_hit"] = 100
        self.assertEqual(evaluate_observation(data)["derived"]["conditional_dr_exact_ratio"],
                         {"numerator": "0", "denominator": "1"})
        data["inputs"]["mitigated_hit"] = 0
        self.assertEqual(evaluate_observation(data)["derived"]["conditional_dr_exact_ratio"],
                         {"numerator": "1", "denominator": "1"})
