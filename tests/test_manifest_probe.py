import io
import unittest
from simulator.manifest_probe import classify_manifest, probe_manifest

class _Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

class ManifestProbeTests(unittest.TestCase):
    def test_changed_requires_review(self):
        self.assertEqual(classify_manifest("new", "old"), "changed_invalidate_dependent_assumptions")
        self.assertEqual(classify_manifest("same", "same"), "unchanged")

    def test_missing_baseline_never_certifies(self):
        self.assertEqual(classify_manifest("new", None), "baseline_unavailable_review_required")

    def test_successful_probe(self):
        def fake_open(req, timeout):
            return _Response(b'{"ErrorCode":1,"Response":{"version":"new"}}')
        result = probe_manifest(opener=fake_open)
        self.assertEqual(result["status"], "changed_invalidate_dependent_assumptions")
        self.assertFalse(result["current_gameplay_verified"])

    def test_failed_network_is_review_required(self):
        def offline(req, timeout): raise OSError("offline")
        self.assertEqual(probe_manifest(opener=offline)["status"], "probe_failed_manual_review_required")

if __name__ == "__main__":
    unittest.main()
