
import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

API_RESPONSE_FILE = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
    / "recruiter_api_response_preview.json"
)

EXPECTED_CANDIDATES = {
    "CAND001", "CAND002", "CAND003", "CAND004", "CAND005",
    "CAND006", "CAND007", "CAND008", "CAND009", "CAND010"
}

REQUIRED_DATA_FIELDS = {
    "candidate",
    "overview",
    "assessments",
    "evaluation",
    "decision",
    "recruiter_action",
    "data_provenance",
    "warnings"
}


class TestRecruiterAPIResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not API_RESPONSE_FILE.exists():
            raise FileNotFoundError(
                f"API response file not found: {API_RESPONSE_FILE}"
            )

        with API_RESPONSE_FILE.open("r", encoding="utf-8") as file:
            cls.response = json.load(file)

    def test_response_is_valid_json_object(self):
        self.assertIsInstance(self.response, dict)

    def test_success_status(self):
        self.assertTrue(self.response.get("success"))

    def test_response_count(self):
        self.assertEqual(self.response.get("count"), 10)

    def test_results_is_list(self):
        self.assertIsInstance(self.response.get("results"), list)

    def test_all_candidates_are_present(self):
        actual = {
            item["candidate"]["candidate_id"]
            for item in self.response["results"]
        }
        self.assertEqual(actual, EXPECTED_CANDIDATES)

    def test_candidate_ids_are_unique(self):
        ids = [
            item["candidate"]["candidate_id"]
            for item in self.response["results"]
        ]
        self.assertEqual(len(ids), len(set(ids)))

    def test_required_response_fields(self):
        for item in self.response["results"]:
            self.assertTrue(REQUIRED_DATA_FIELDS.issubset(item.keys()))

    def test_assessment_rounds(self):
        expected_rounds = {
            "ats", "hr", "aptitude", "technical", "machine_test"
        }

        for item in self.response["results"]:
            actual_rounds = {
                assessment["round"]
                for assessment in item["assessments"]
            }
            self.assertEqual(actual_rounds, expected_rounds)

    def test_scores_are_valid_or_missing(self):
        for item in self.response["results"]:
            for assessment in item["assessments"]:
                score = assessment.get("score")

                if score is not None:
                    self.assertIsInstance(score, (int, float))
                    self.assertGreaterEqual(score, 0)
                    self.assertLessEqual(score, 100)

    def test_candidate_007_missing_ats(self):
        candidate = next(
            item for item in self.response["results"]
            if item["candidate"]["candidate_id"] == "CAND007"
        )

        ats = next(
            item for item in candidate["assessments"]
            if item["round"] == "ats"
        )

        self.assertIsNone(ats["score"])
        self.assertEqual(
            candidate["overview"]["final_decision"],
            "BLOCKED_PENDING_ATS"
        )

    def test_candidate_010_has_no_scores(self):
        candidate = next(
            item for item in self.response["results"]
            if item["candidate"]["candidate_id"] == "CAND010"
        )

        self.assertIsNone(candidate["overview"]["unified_score"])

        for assessment in candidate["assessments"]:
            self.assertIsNone(assessment["score"])

    def test_simulated_assessments_are_identified(self):
        for item in self.response["results"]:
            for assessment in item["assessments"]:
                if assessment.get("is_simulated") is True:
                    self.assertTrue(assessment.get("score_source"))

    def test_human_review_is_required(self):
        for item in self.response["results"]:
            self.assertTrue(
                item["recruiter_action"]["requires_human_review"]
            )

    def test_demo_dataset_warning_is_present(self):
        for item in self.response["results"]:
            warnings = item["warnings"]

            self.assertTrue(
                any("demo dataset" in warning.lower() for warning in warnings)
            )

    def test_no_response_errors(self):
        self.assertEqual(self.response.get("errors"), [])


if __name__ == "__main__":
    print("=" * 65)
    print("ZECPath DAY 65 - RECRUITER API RESPONSE TESTS")
    print("=" * 65)

    unittest.main(verbosity=2)
