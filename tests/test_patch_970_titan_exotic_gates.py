import json,unittest
from decimal import Decimal
from pathlib import Path
from simulator.patch_970_titan_exotic_gates import (
 MAX_POINT_CONTACT_LIGHTNING_CHARGE_MULTIPLIER,
 point_contact_charge_lightning_multiplier,acd0_pvp_melee_damage_resistance_claim_allowed,
)
ROOT=Path(__file__).resolve().parents[1]
class TitanExotic970GatesTest(unittest.TestCase):
 def test_published_lightning_strike_max_is_two(self):
  self.assertEqual(MAX_POINT_CONTACT_LIGHTNING_CHARGE_MULTIPLIER,Decimal("2"))
 def test_charge_multiplier_accepts_boundaries(self):
  self.assertEqual(point_contact_charge_lightning_multiplier("1"),Decimal("1"))
  self.assertEqual(point_contact_charge_lightning_multiplier("2"),Decimal("2"))
 def test_charge_multiplier_rejects_unverified_values(self):
  for bad in (-1,0,2.01,"nan","Infinity",True,"unmeasured"):
   with self.subTest(value=bad),self.assertRaises(ValueError):point_contact_charge_lightning_multiplier(bad)
 def test_pvp_removed_melee_dr_is_never_certified(self):
  self.assertIs(acd0_pvp_melee_damage_resistance_claim_allowed(True),False)
 def test_pve_dr_is_not_inferred_from_pvp_patch(self):
  self.assertIsNone(acd0_pvp_melee_damage_resistance_claim_allowed(False))
 def test_mode_gate_rejects_non_boolean(self):
  with self.assertRaises(TypeError):acd0_pvp_melee_damage_resistance_claim_allowed("PvP")
 def test_records_preserve_measurement_unknowns(self):
  d=json.loads((ROOT/"data/patch_970_titan_exotic_gates_20261103.json").read_text())
  self.assertEqual(len(d["records"]),2)
  for r in d["records"]:
   self.assertEqual(r["evidence"],"official_historical")
   self.assertFalse(r["runtime_verified"])
   self.assertFalse(r["certified_for_live_build"])
   self.assertIsNone(r["unknown_measurements"]["pvp_ttk"])
   self.assertIsNone(r["unknown_measurements"]["pve_boss_dps"])
 def test_strike_multiplier_is_not_a_melee_or_boss_dps_multiplier(self):
  d=json.loads((ROOT/"data/patch_970_titan_exotic_gates_20261103.json").read_text())
  point=d["records"][0]
  self.assertIn("lightning",point["id"])
  self.assertIsNone(point["unknown_measurements"]["pve_boss_dps"])
  self.assertFalse(point["runtime_verified"])
 def test_player_guides_exist_without_false_measurements(self):
  d=json.loads((ROOT/"data/player_discoveries.json").read_text())
  ids={r["id"]:r for r in d["records"]}
  for key in ("player:point-contact-thunderclap-charge-970","player:acd0-no-pvp-melee-dr-970"):
   self.assertIn(key,ids)
   self.assertFalse(ids[key]["runtime_verified"])
   self.assertEqual(ids[key]["player"]["version"],1)
if __name__=="__main__":unittest.main()
