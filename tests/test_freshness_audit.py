import unittest
from simulator.freshness_audit import freshness_report

class FreshnessAuditTests(unittest.TestCase):
    def test_explicit_outdated_is_never_overridden(self):
        rows = freshness_report(as_of="2026-10-29")["sources"]
        self.assertEqual(next(r for r in rows if r["id"] == "clarity_stats")["status"], "blocked_explicitly_outdated")

    def test_partial_dates_require_review(self):
        rows = freshness_report(as_of="2026-10-29")["sources"]
        self.assertEqual(next(r for r in rows if r["id"] == "d2_ttk_cheatsheet_2026_01")["status"], "blocked_explicitly_outdated")

    def test_no_current_certification(self):
        result = freshness_report(as_of="2026-10-29")
        self.assertTrue(all(not r["current_gameplay_verified"] for r in result["sources"]))

if __name__ == "__main__":
    unittest.main()
