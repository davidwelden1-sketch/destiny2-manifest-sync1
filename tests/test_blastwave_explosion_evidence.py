import unittest

from simulator.blastwave_explosion_evidence import (
    SOURCE_DATE, SOURCE_URL, blastwave_explosion_gate,
)


class BlastwaveExplosionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.base = dict(
            exotic_equipped=True,
            perk_name="Firefly",
            event_kind="on_kill_explosion",
            activity="pve",
            weapon_item_hash=123456789,
        )

    def check(self, **changes):
        return blastwave_explosion_gate(**{**self.base, **changes})

    def test_firefly_kill_explosion_explicitly_excluded(self):
        r = self.check()
        self.assertEqual(r["gate"], "officially_excluded_from_blast_trigger")
        self.assertFalse(r["trigger_certified"])
        self.assertFalse(r["weapon_roll_legality_certified"])

    def test_dragonfly_kill_explosion_explicitly_excluded(self):
        self.assertEqual(
            self.check(perk_name="  dRaGoNfLy  ")["gate"],
            "officially_excluded_from_blast_trigger",
        )

    def test_explosive_payload_passive_not_excluded_but_unverified(self):
        r = self.check(perk_name="Explosive Payload", event_kind="passive_explosion")
        self.assertEqual(r["gate"], "officially_not_excluded_activation_unverified")
        self.assertFalse(r["trigger_certified"])
        self.assertIsNone(r["self_damage"])
        self.assertIsNone(r["charge_threshold"])

    def test_explosive_head_passive_not_excluded(self):
        self.assertEqual(
            self.check(perk_name="Explosive Head", event_kind="passive_explosion")["gate"],
            "officially_not_excluded_activation_unverified",
        )

    def test_unknown_perk_is_not_automatically_eligible(self):
        self.assertEqual(
            self.check(perk_name="Incandescent")["gate"],
            "source_event_pair_not_classified",
        )

    def test_wrong_event_pair_is_not_extrapolated(self):
        for perk, event in (("Firefly", "passive_explosion"),
                            ("Explosive Payload", "on_kill_explosion")):
            with self.subTest(perk=perk):
                self.assertEqual(
                    self.check(perk_name=perk, event_kind=event)["gate"],
                    "source_event_pair_not_classified",
                )

    def test_exotic_absent_overrides_missing_inputs(self):
        self.assertEqual(
            self.check(exotic_equipped=False, perk_name=None, event_kind=None)["gate"],
            "exotic_not_equipped",
        )

    def test_unknown_required_inputs_fail_closed(self):
        for key in ("exotic_equipped", "perk_name", "event_kind", "activity"):
            with self.subTest(key=key):
                self.assertEqual(
                    self.check(**{key: None})["gate"], "insufficient_inputs"
                )

    def test_pvp_does_not_infer_damage_or_ttk(self):
        r = self.check(activity="pvp")
        self.assertEqual(r["gate"], "officially_excluded_from_blast_trigger")
        self.assertIsNone(r["pvp_ttk"])
        self.assertIsNone(r["explosion_damage"])
        self.assertEqual(r["evidence_grade"], "official_patch_text_not_gameplay_measurement")

    def test_pve_does_not_infer_boss_dps_or_roll_legality(self):
        r = self.check(perk_name="Explosive Head", event_kind="passive_explosion")
        self.assertIsNone(r["pve_boss_dps"])
        self.assertFalse(r["enhanced_perk_legality_certified"])
        self.assertFalse(r["artifact_selection_certified"])
        self.assertIsNone(r["kill_attribution"])

    def test_weapon_hash_is_identity_only(self):
        r = self.check(weapon_item_hash=987654321)
        self.assertEqual(r["weapon_item_hash"], 987654321)
        self.assertFalse(r["weapon_roll_legality_certified"])

    def test_bad_values_rejected(self):
        bad = (
            ("exotic_equipped", 1),
            ("perk_name", ""),
            ("event_kind", "precision_kill"),
            ("activity", "trials"),
            ("weapon_item_hash", True),
            ("weapon_item_hash", 0),
        )
        for field, value in bad:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(**{field: value})

    def test_official_source_date_and_url(self):
        self.assertEqual(SOURCE_DATE, "2026-06-09")
        self.assertEqual(
            SOURCE_URL,
            "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0",
        )


if __name__ == "__main__":
    unittest.main()
