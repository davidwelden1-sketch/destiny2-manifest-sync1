import io
import unittest
from urllib.error import HTTPError
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


    def test_transient_transport_error_retries_and_recovers(self):
        calls = []
        def flaky(req, timeout):
            calls.append(timeout)
            if len(calls) == 1:
                raise OSError("temporary outage")
            return _Response(b'{"ErrorCode":1,"Response":{"version":"new"}}')
        result = probe_manifest(opener=flaky)
        self.assertEqual(result["status"], "changed_invalidate_dependent_assumptions")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(calls, [20, 20])
        self.assertFalse(result["current_gameplay_verified"])

    def test_rate_limit_does_not_retry(self):
        calls = []
        def rate_limited(req, timeout):
            calls.append(1)
            raise HTTPError(req.full_url, 429, "rate limited", {}, None)
        result = probe_manifest(opener=rate_limited)
        self.assertEqual(result["status"], "probe_failed_manual_review_required")
        self.assertEqual(result["http_status"], 429)
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(len(calls), 1)

    def test_server_503_retries_but_still_fails_closed(self):
        calls = []
        def unavailable(req, timeout):
            calls.append(1)
            raise HTTPError(req.full_url, 503, "unavailable", {}, None)
        result = probe_manifest(opener=unavailable)
        self.assertEqual(result["status"], "probe_failed_manual_review_required")
        self.assertEqual(result["http_status"], 503)
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(calls), 2)

    def test_invalid_api_payload_never_retried(self):
        calls = []
        def bad_payload(req, timeout):
            calls.append(1)
            return _Response(b'{"ErrorCode":5}')
        result = probe_manifest(opener=bad_payload)
        self.assertEqual(result["error_type"], "ValueError")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(len(calls), 1)

    def test_retry_budget_rejects_bool_and_unbounded_values(self):
        for invalid in (True, 0, 4, 1.5):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    probe_manifest(max_attempts=invalid)

if __name__ == "__main__":
    unittest.main()
