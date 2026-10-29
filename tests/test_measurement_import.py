import csv
import tempfile
import unittest
from pathlib import Path
from simulator.measurement_import import import_measurements, REQUIRED

class MeasurementImportTests(unittest.TestCase):
    def write_csv(self, rows):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "observations.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(temp.cleanup)
        return path

    def samples(self):
        return [
            {"metric": "precision_damage", "game_version": "9.7.0.5",
             "activity": "pvp_private", "scenario": "weapon=123;target=baseline;buff=none",
             "unit": "damage_per_hit", "value": str(v),
             "source_url": "https://example.org/measurement",
             "measured_on": "2026-10-20", "method": "repeated controlled test",
             "sample_id": str(i)}
            for i, v in enumerate((70, 71, 72), 1)
        ]

    def test_aggregates_three_samples(self):
        result = import_measurements(self.write_csv(self.samples()))
        self.assertEqual(result["total_rows"], 3)
        self.assertEqual(result["groups"][0]["mean"], 71)
        self.assertFalse(result["verified_in_game"])

    def test_insufficient_samples_not_promoted(self):
        result = import_measurements(self.write_csv(self.samples()[:2]))
        self.assertEqual(result["groups"][0]["status"], "insufficient_samples")

    def test_rejects_duplicate_samples(self):
        rows = self.samples()
        rows[1]["sample_id"] = rows[0]["sample_id"]
        with self.assertRaises(ValueError):
            import_measurements(self.write_csv(rows))

    def test_rejects_mixed_context_without_merging(self):
        rows = self.samples()
        rows[2]["scenario"] = "different"
        result = import_measurements(self.write_csv(rows))
        self.assertEqual(len(result["groups"]), 2)

    def test_rejects_nan(self):
        rows = self.samples()
        rows[0]["value"] = "nan"
        with self.assertRaises(ValueError):
            import_measurements(self.write_csv(rows))

    def test_rejects_non_https(self):
        rows = self.samples()
        rows[0]["source_url"] = "http://example.org"
        with self.assertRaises(ValueError):
            import_measurements(self.write_csv(rows))

if __name__ == "__main__":
    unittest.main()
