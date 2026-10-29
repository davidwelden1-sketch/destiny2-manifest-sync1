import unittest
from simulator.stacking import combine_multipliers, apply_damage
from simulator.survivability import effective_resistance, effective_health
from simulator.cooldowns import recharge_seconds, uptime_fraction
from simulator.rotations import simulate_rotation
from simulator.provenance import validate_measurement
from simulator.burst import time_to_kill_sequence
from simulator.falloff import linear_falloff

class TestModels(unittest.TestCase):
    def test_stacking(self):
        self.assertAlmostEqual(combine_multipliers([1.2, 1.3]), 1.56)
        self.assertEqual(combine_multipliers([1.2, 1.3], "highest"), 1.3)
        self.assertAlmostEqual(apply_damage(100, [{"multipliers":[1.2,1.3],"policy":"multiply"}]),156)
    def test_survivability(self):
        self.assertAlmostEqual(effective_resistance([0.2,0.3]),0.44)
        self.assertAlmostEqual(effective_health(100,0,[0.5]),200)
    def test_cooldown(self):
        self.assertEqual(recharge_seconds(100,2,10),40)
        self.assertEqual(uptime_fraction(5,20),0.25)
    def test_rotation(self):
        self.assertEqual(simulate_rotation([{"time":0,"damage":100},{"time":10,"damage":200}],10)["total_damage"],100)
    def test_evidence(self):
        with self.assertRaises(ValueError):
            validate_measurement({"value":1})
    def test_burst(self):
        self.assertEqual(time_to_kill_sequence(100,[(0,40),(0.1,60)]),0.1)
    def test_falloff(self):
        self.assertEqual(linear_falloff(20,10,30,0.5),0.75)
