"""Synthetic regression tests for documented ammo-brick location gating."""
import unittest
from simulator.deferred_ammo_brick_rules import project_ammo_brick_events


def kill(over_pit, meter_completed):
    return {"over_pit": over_pit, "meter_completed": meter_completed}


class DeferredAmmoBrickRulesTests(unittest.TestCase):
    def test_over_pit_meter_completion_defers_brick(self):
        result = project_ammo_brick_events([kill(True, True)])
        self.assertEqual(result["events"][0]["event"], "meter_completed_brick_deferred")
        self.assertTrue(result["owed_brick_pending"])
        self.assertIsNone(result["ammo_brick_count"])

    def test_next_non_pit_kill_releases_owed_brick_without_new_completion(self):
        result = project_ammo_brick_events([kill(True, True), kill(False, False)])
        self.assertEqual(result["events"][-1]["event"], "owed_brick_due")
        self.assertFalse(result["owed_brick_pending"])

    def test_intermediate_pit_kills_do_not_release_owed_brick(self):
        result = project_ammo_brick_events([kill(True, True), kill(True, False), kill(False, False)])
        self.assertEqual(result["events"][1]["event"], "no_brick_from_pit_kill")
        self.assertEqual(result["events"][2]["event"], "owed_brick_due")

    def test_over_pit_kill_without_completion_does_not_create_debt(self):
        result = project_ammo_brick_events([kill(True, False), kill(False, False)])
        self.assertEqual(result["events"][-1]["event"], "no_brick_trigger")
        self.assertFalse(result["owed_brick_pending"])

    def test_multiple_completions_do_not_invent_brick_count(self):
        result = project_ammo_brick_events([kill(True, True), kill(True, True)])
        self.assertEqual(result["events"][-1]["event"], "multiple_meter_completions_unresolved")
        self.assertTrue(result["multiple_brick_count_unresolved"])
        self.assertIsNone(result["ammo_brick_count"])

    def test_new_completion_while_releasing_owed_brick_is_unresolved(self):
        result = project_ammo_brick_events([kill(True, True), kill(False, True)])
        self.assertEqual(result["events"][-1]["event"], "owed_brick_due_new_completion_unresolved")
        self.assertTrue(result["multiple_brick_count_unresolved"])

    def test_non_pit_meter_completion_is_only_candidate_not_measured(self):
        result = project_ammo_brick_events([kill(False, True)])
        self.assertEqual(result["events"][0]["event"], "meter_completion_spawn_candidate")
        self.assertIsNone(result["ammo_brick_count"])

    def test_reject_non_boolean_or_extra_fields(self):
        for bad in ([kill(1, True)], [{"over_pit": False, "meter_completed": True, "ammo": 5}], [None]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                project_ammo_brick_events(bad)

    def test_reject_non_sequence(self):
        with self.assertRaises(ValueError):
            project_ammo_brick_events(None)


if __name__ == "__main__":
    unittest.main()
