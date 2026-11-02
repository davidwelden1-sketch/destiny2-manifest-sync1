import unittest

from simulator.survivability_leads_970 import assess_survivability_lead


def assess(**changes):
    args = dict(mechanic="rope_dart_catch", guardian_class="hunter",
                activity="pve", observation_date="2026-11-02",
                event_kind="dart_catch", dart_defeats=2)
    args.update(changes)
    return assess_survivability_lead(**args)


class SurvivabilityLeads970Tests(unittest.TestCase):
    def test_rope_dart_requires_catch_and_defeats_for_candidate(self):
        self.assertTrue(assess()["source_supported_candidate"])
        self.assertFalse(assess(event_kind="weapon_final_blow")["source_supported_candidate"])
        self.assertFalse(assess(dart_defeats=0)["source_supported_candidate"])
        self.assertFalse(assess(dart_defeats=None)["source_supported_candidate"])

    def test_rope_dart_not_assumed_to_grant_measured_dr(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            with self.subTest(mode=mode):
                result = assess(activity=mode)
                self.assertIsNone(result["measured_pve_damage_resistance"])
                self.assertFalse(result["runtime_activation_verified"])
                self.assertFalse(result["specific_exotic_proc_verified"])

    def test_shieldburst_requires_ally_and_supported_weapon_element(self):
        args = dict(mechanic="shieldburst_rally", guardian_class="titan",
                    event_kind="rally_cover", dart_defeats=None,
                    ally_target=True, weapon_element="solar")
        self.assertTrue(assess(**args)["source_supported_candidate"])
        self.assertTrue(assess(**{**args, "weapon_element": "kinetic"})["source_supported_candidate"])
        for change in ({"ally_target": False}, {"weapon_element": "void"},
                       {"event_kind": "weapon_final_blow"}):
            self.assertFalse(assess(**{**args, **change})["source_supported_candidate"])

    def test_shieldburst_does_not_prove_self_buff_or_roll_legality(self):
        result = assess(mechanic="shieldburst_rally", guardian_class="titan",
                        event_kind="rally_cover", dart_defeats=None,
                        ally_target=True, weapon_element="solar")
        self.assertFalse(result["exact_weapon_hash_and_roll_verified"])
        self.assertIsNone(result["measured_pve_dps"])

    def test_heat_rises_only_claims_combatant_accuracy(self):
        args = dict(mechanic="heat_rises_accuracy", guardian_class="warlock",
                    event_kind="heat_rises_active", dart_defeats=None)
        self.assertTrue(assess(**args)["source_supported_candidate"])
        for mode in ("pvp", "competitive", "trials"):
            self.assertFalse(assess(**{**args, "activity": mode})["source_supported_candidate"])
        self.assertEqual(assess(**args)["pvp_scope"], "no_guardian_accuracy_claim_in_source")

    def test_wrong_class_and_prepatch_fail_closed(self):
        self.assertFalse(assess(guardian_class="titan")["source_supported_candidate"])
        self.assertFalse(assess(observation_date="2026-06-08")["source_supported_candidate"])
        self.assertTrue(assess(observation_date="2026-06-09")["source_supported_candidate"])

    def test_artifact_modes_never_assumed_active(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            r = assess(activity=mode, artifact_name="Example", artifact_perks=("A",))
            self.assertIs(r["artifact_effects_active"],
                          False if mode in ("competitive", "trials") else None)
            self.assertFalse(r["current_artifact_allocation_verified"])

    def test_reject_invalid_artifact_allocations(self):
        bad = ({"artifact_perks": ("A",)},
               {"artifact_name": "A", "artifact_perks": ("A", "A")},
               {"artifact_name": "A", "artifact_perks": tuple(str(i) for i in range(8))},
               {"artifact_name": "A", "artifact_perks": "A"})
        for kw in bad:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                assess(**kw)

    def test_reject_invalid_metadata(self):
        bad = ({"mechanic": "fake"}, {"guardian_class": "all"},
               {"activity": "raid"}, {"event_kind": "other"},
               {"observation_date": "2026-6-9"},
               {"observation_date": "2026-02-30"},
               {"dart_defeats": True}, {"dart_defeats": -1},
               {"ally_target": 1}, {"weapon_element": "unknown"},
               {"manifest_version": ""}, {"artifact_name": ""})
        for kw in bad:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                assess(**kw)

    def test_provenance_and_app_contract(self):
        r = assess(manifest_version="test-manifest")
        self.assertEqual(r["id"], "d2:patch-rule:970:survival-lead:rope_dart_catch")
        self.assertEqual(r["patch_version"], "9.7.0")
        self.assertEqual(r["patch_date"], "2026-06-09")
        self.assertEqual(r["manifest_version"], "test-manifest")
        self.assertIn("bungie.net", r["source_url"])
        self.assertEqual(r["source_checked_at"], "2026-11-02")
        self.assertIsNone(r["measured_pvp_ttk"])
        self.assertIsNone(r["measured_cooldown_or_uptime"])


if __name__ == "__main__":
    unittest.main()
