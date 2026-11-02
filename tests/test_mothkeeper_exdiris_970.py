"""Synthetic source-gating tests, not in-game Mothkeeper measurements."""
import unittest
from simulator.mothkeeper_exdiris_970 import assess_mothkeeper

BASE = dict(activity="pve", final_blows=[], observation_date="2026-11-02",
            mothkeepers_equipped=True, ex_diris_equipped=True)

def run(**kwargs):
    return assess_mothkeeper(**(BASE | kwargs))

class MothkeeperExDiris970Tests(unittest.TestCase):
    def test_six_red_bar_final_blows(self):
        r = run(final_blows=["red_bar"] * 6)
        self.assertTrue(r["two_moth_grenade_override_threshold_reached"])
        self.assertEqual(r["counted_final_blows_to_first_override"], 6)

    def test_three_orange_bar_final_blows(self):
        self.assertTrue(run(final_blows=["orange_bar"] * 3)["two_moth_grenade_override_threshold_reached"])

    def test_two_miniboss_final_blows(self):
        self.assertTrue(run(final_blows=["miniboss"] * 2)["two_moth_grenade_override_threshold_reached"])

    def test_pvp_two_guardian_final_blows(self):
        self.assertTrue(run(activity="pvp", final_blows=["guardian", "guardian"])["two_moth_grenade_override_threshold_reached"])

    def test_one_guardian_only_halfway(self):
        r = run(activity="pvp", final_blows=["guardian"])
        self.assertEqual(r["remaining_units"], 3)
        self.assertFalse(r["two_moth_grenade_override_threshold_reached"])

    def test_exdiris_fix_does_not_require_grenade_charge(self):
        r = run(final_blows=[])
        self.assertTrue(r["ex_diris_charge_gate_fix_applicable"])
        self.assertFalse(r["two_moth_grenade_override_threshold_reached"])

    def test_before_june_23_fix_not_claimed(self):
        self.assertFalse(run(observation_date="2026-06-22")["ex_diris_charge_gate_fix_applicable"])

    def test_unequipped_armor_disables_both(self):
        r = run(final_blows=["red_bar"] * 6, mothkeepers_equipped=False)
        self.assertFalse(r["two_moth_grenade_override_threshold_reached"])
        self.assertFalse(r["ex_diris_charge_gate_fix_applicable"])

    def test_wrong_target_type_fails_closed(self):
        with self.assertRaises(ValueError):
            run(activity="pvp", final_blows=["red_bar"])

    def test_competitive_and_trials_reject_artifact(self):
        for activity in ("competitive", "trials"):
            with self.subTest(activity=activity):
                with self.assertRaises(ValueError):
                    run(activity=activity, artifact_perks=["unknown perk"])

    def test_seven_artifact_cap(self):
        with self.assertRaises(ValueError):
            run(artifact_perks=["x"] * 8)

    def test_unverified_measurements_not_promoted(self):
        r = run(final_blows=["boss"] * 2)
        self.assertFalse(r["damage_dps_ttk_dr_cooldowns_measured"])
        self.assertFalse(r["current_gameplay_certified"])
        self.assertFalse(r["exact_weapon_perk_legality_certified"])

    def test_stop_at_first_threshold_without_overflow_inference(self):
        r = run(final_blows=["red_bar"] * 20)
        self.assertEqual(r["charge_units_to_first_override"], 6)
        self.assertEqual(r["counted_final_blows_to_first_override"], 6)

    def test_invalid_date_fails_closed(self):
        for value in ("2026-06-08", "2026-11-2", "tomorrow"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                run(observation_date=value)

if __name__ == "__main__":
    unittest.main()
