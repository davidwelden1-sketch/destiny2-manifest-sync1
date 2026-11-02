import unittest
from simulator.grapple_boss_stat_970 import (
    assess_grapple_boss_scaling, illustrative_max_stat_bonus_math,
)


def assess(**kw):
    args = dict(observation_date="2026-11-02", guardian_class="hunter",
                activity="pve", target_rank="boss", event_kind="grapple_melee")
    args.update(kw)
    return assess_grapple_boss_scaling(**args)


class GrappleBossStat970Tests(unittest.TestCase):
    def test_all_three_classes_official_boss_scope(self):
        for c in ("hunter", "titan", "warlock"):
            r = assess(guardian_class=c)
            self.assertTrue(r["official_historical_rule_applicable"])
            self.assertEqual(r["postpatch_grenade_and_melee_stat_bonuses"], "additive")
            self.assertEqual(r["maximum_grenade_stat_bonus_relative_reduction"], 0.5)

    def test_pvp_and_nonboss_do_not_inherit_boss_math(self):
        for activity, rank in (("pvp", "guardian"), ("competitive", "guardian"),
                               ("trials", "guardian"), ("pve", "nonboss_combatant")):
            self.assertFalse(assess(activity=activity, target_rank=rank)[
                "official_historical_rule_applicable"])

    def test_only_grapple_melee_qualifies(self):
        for event in ("weapon_final_blow", "other_melee"):
            self.assertFalse(assess(event_kind=event)["official_historical_rule_applicable"])

    def test_patch_day_and_prepatch_fail_closed(self):
        for day in ("2026-06-08", "2026-06-09"):
            self.assertFalse(assess(observation_date=day)["official_historical_rule_applicable"])
        self.assertTrue(assess(observation_date="2026-06-10")["official_historical_rule_applicable"])

    def test_hypothetical_math_is_not_gameplay(self):
        r = illustrative_max_stat_bonus_math(prepatch_grenade_bonus_fraction=0.4,
                                             melee_bonus_fraction=0.2)
        self.assertAlmostEqual(r["prepatch_multiplier_illustrative"], 1.68)
        self.assertAlmostEqual(r["postpatch_multiplier_illustrative"], 1.4)
        self.assertTrue(r["hypothetical_only"])
        self.assertIsNone(r["measured_pve_dps"])

    def test_reject_bad_hypothetical_inputs(self):
        for x in (-1, True, float("nan"), float("inf"), "0.4"):
            with self.assertRaises(ValueError):
                illustrative_max_stat_bonus_math(prepatch_grenade_bonus_fraction=x,
                                                 melee_bonus_fraction=0.2)

    def test_artifact_and_measurement_gates(self):
        for mode in ("pve", "pvp", "competitive", "trials"):
            r = assess(activity=mode, artifact_name="unverified",
                       artifact_perks=("A", "B"))
            self.assertEqual(r["artifact_effects_active"],
                             False if mode in ("competitive", "trials") else None)
            self.assertIsNone(r["measured_pve_boss_dps"])
            self.assertIsNone(r["measured_pvp_guardian_ttk"])
            self.assertFalse(r["current_artifact_allocation_verified"])

    def test_invalid_metadata_and_artifact_rejected(self):
        for kw in ({"observation_date": "2026-6-9"},
                   {"guardian_class": "all"}, {"target_rank": "champion"},
                   {"event_kind": "weapon_kill"}, {"manifest_version": ""},
                   {"artifact_perks": ("A",)},
                   {"artifact_name": "A", "artifact_perks": ("A", "A")},
                   {"artifact_name": "A", "artifact_perks": tuple(str(i) for i in range(8))}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                assess(**kw)

    def test_stable_provenance(self):
        r = assess(manifest_version="test-snapshot")
        self.assertEqual(r["id"], "d2:patch-rule:970:grapple-melee:boss-stat-bonus")
        self.assertEqual(r["patch_version"], "9.7.0")
        self.assertEqual(r["manifest_version"], "test-snapshot")
        self.assertIn("bungie.net", r["source_url"])


if __name__ == "__main__":
    unittest.main()
