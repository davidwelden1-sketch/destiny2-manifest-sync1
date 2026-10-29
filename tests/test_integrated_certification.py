import unittest
from simulator.certification_gate import REQUIRED, build_certified_with_sources

class IntegratedCertificationTests(unittest.TestCase):
    def test_empty_records_fail(self):
        self.assertFalse(build_certified_with_sources({}, "raid"))

    def test_unsourced_status_strings_fail(self):
        phases = {p: {k: "verified" for k in fields} for p, fields in REQUIRED.items()}
        self.assertFalse(build_certified_with_sources(phases, "strike"))

    def test_restricted_activity_fails(self):
        self.assertFalse(build_certified_with_sources({}, "Trials", artifact_selected=True))

    def test_invalid_activity_rejected(self):
        with self.assertRaises(ValueError):
            build_certified_with_sources({}, "")

if __name__ == "__main__":
    unittest.main()
