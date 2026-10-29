import unittest
from simulator.sourced_candidate_search import evaluate_sourced_candidates

W = {"damage": 1, "survivability": 1, "uptime": 1}
def candidate():
    return {"id": "hunter_a", "class": "hunter", "artifact_perks": ["sample"],
            "artifact_reviewed": True, "metrics": {
                k: {"low": .3, "high": .6, "source_ids": ["reviewed"]}
                for k in W}}
def doc(review):
    return {"game_version": "test-version", "source_reviews": {"reviewed": review},
            "candidates": [candidate()]}
class SourcedCandidateTests(unittest.TestCase):
    def test_unreviewed_blocked(self):
        result = evaluate_sourced_candidates(doc({}), W, "test-version")
        self.assertEqual(result["ranked"], [])
        self.assertEqual(result["rejected"][0]["reason"], "unapproved_metric_source")

    def test_reviewed_still_not_certified(self):
        review = {"game_version": "test-version", "independent_review_complete": True,
                  "reuse_permission_confirmed": True}
        result = evaluate_sourced_candidates(doc(review), W, "test-version")
        self.assertEqual(len(result["ranked"]), 1)
        self.assertEqual(result["certified_builds"], 0)

    def test_wrong_version_blocked(self):
        result = evaluate_sourced_candidates(doc({}), W, "other-version")
        self.assertEqual(result["ranked"], [])
        self.assertEqual(result["rejected"][0]["reason"], "version_mismatch")

    def test_artifact_unreviewed_blocked(self):
        c = candidate()
        c["artifact_reviewed"] = False
        result = evaluate_sourced_candidates(
            {"game_version": "test-version", "candidates": [c]}, W, "test-version")
        self.assertEqual(result["rejected"][0]["reason"], "artifact_evidence_missing")

if __name__ == "__main__":
    unittest.main()
