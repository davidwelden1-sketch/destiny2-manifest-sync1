"""Synthetic structural tests; never gameplay or official Artifact roll certification."""
import unittest

from simulator.artifact_allocation_guard import audit_artifact_allocation


def audit(perks=None, **overrides):
    data = dict(artifact_id="Slayer Baron Apothecary Satchel",
                perk_ids=["Wind Chill", "Hail the Storm"] if perks is None else perks,
                activity="pve")
    data.update(overrides)
    return audit_artifact_allocation(**data)


class ArtifactAllocationGuardTests(unittest.TestCase):
    def test_two_selected_perks_are_structural_only(self):
        r = audit()
        self.assertTrue(r["structural_selection_valid"])
        self.assertEqual(r["status"], "structural_only_current_pool_unknown")
        self.assertFalse(r["current_artifact_rotation_verified"])

    def test_seven_distinct_perks_at_cap(self):
        r = audit(perks=[f"perk{i}" for i in range(7)])
        self.assertTrue(r["within_seven_perks"])
        self.assertEqual(r["selected_perk_count"], 7)

    def test_eight_perks_rejected(self):
        r = audit(perks=[f"perk{i}" for i in range(8)])
        self.assertFalse(r["within_seven_perks"])
        self.assertFalse(r["structural_selection_valid"])
        self.assertEqual(r["status"], "over_seven_perks")

    def test_duplicates_rejected_even_when_case_differs(self):
        r = audit(perks=["Wind Chill", "wind chill"])
        self.assertFalse(r["no_duplicates"])
        self.assertFalse(r["structural_selection_valid"])
        self.assertEqual(r["status"], "duplicate_perks_rejected")

    def test_empty_selection_not_a_build(self):
        r = audit(perks=[])
        self.assertFalse(r["structural_selection_valid"])
        self.assertEqual(r["status"], "empty_selection")

    def test_competitive_and_trials_disable_artifact(self):
        for mode in ("competitive", "trials"):
            with self.subTest(mode=mode):
                r = audit(activity=mode)
                self.assertFalse(r["artifact_mode_eligible"])
                self.assertIs(r["artifact_effects_active"], False)
                self.assertEqual(r["status"], "artifact_effects_disabled_in_activity")

    def test_ordinary_pvp_not_assumed_disabled(self):
        r = audit(activity="pvp")
        self.assertTrue(r["artifact_mode_eligible"])
        self.assertIsNone(r["artifact_effects_active"])
        self.assertFalse(r["current_artifact_rotation_verified"])

    def test_supplied_pool_is_not_official_certification(self):
        r = audit(candidate_perk_pool=["Wind Chill", "Hail the Storm"])
        self.assertTrue(r["candidate_pool_membership"])
        self.assertEqual(r["status"], "structural_only_supplied_pool_not_certified")
        self.assertFalse(r["single_active_artifact_verified_in_game"])

    def test_supplied_pool_missing_perk_fails(self):
        r = audit(candidate_perk_pool=["Wind Chill"])
        self.assertFalse(r["candidate_pool_membership"])
        self.assertEqual(r["status"], "not_in_supplied_candidate_pool")

    def test_no_cross_artifact_list_identity(self):
        for invalid in (["Artifact A", "Artifact B"], "", " Artifact A ", None, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                audit(artifact_id=invalid)

    def test_reject_invalid_perk_inputs(self):
        for invalid in ("Wind Chill", {1, 2}, [1], [True], [" Wind Chill"], [""]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                audit(perks=invalid)

    def test_reject_invalid_candidate_pool(self):
        for invalid in ("Wind Chill", [None], [" perk"], [True]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                audit(candidate_perk_pool=invalid)

    def test_reject_invalid_activity_without_typeerror(self):
        for invalid in ([], {}, None, True, "gambit"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                audit(activity=invalid)

    def test_no_damage_or_roll_claims(self):
        r = audit()
        self.assertFalse(r["enhanced_weapon_roll_verified"])
        self.assertFalse(r["gameplay_measured"])
        self.assertEqual(r["evidence_grade"], "structural_guard_not_current_manifest")


if __name__ == "__main__":
    unittest.main()
