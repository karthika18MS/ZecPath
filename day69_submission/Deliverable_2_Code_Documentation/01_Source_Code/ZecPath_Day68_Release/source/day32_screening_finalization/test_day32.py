import json
import sys
import unittest
from pathlib import Path


# ==========================================================
# PATH SETUP
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DAY32_DIR = Path(__file__).resolve().parent
RESULTS_DIR = DAY32_DIR / "results"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from day32_screening_finalization.final_screening_pipeline import (
    FinalScreeningPipeline
)


# ==========================================================
# TEST DATA
# ==========================================================

CANDIDATE_ID = "candidate_006"
JOB_ID = "JOB_BACKEND_001"


QUESTIONS = [
    {
        "question_id": "BACKEND_EXP_001",
        "question": (
            "How many years of backend development experience "
            "do you have?"
        ),
        "question_category": "experience",
        "answer": (
            "I have three years of backend development experience. "
            "I have worked with Python and Django."
        ),
        "duration_seconds": 8,
        "audio_quality": 1.0,
        "background_noise": 0.0
    },
    {
        "question_id": "BACKEND_SKILLS_001",
        "question": "What technical skills do you have?",
        "question_category": "skills",
        "answer": (
            "I have experience with Python, Django, Docker "
            "and PostgreSQL."
        ),
        "duration_seconds": 9,
        "audio_quality": 1.0,
        "background_noise": 0.0
    },
    {
        "question_id": "BACKEND_AVAILABILITY_001",
        "question": "When would you be available to join?",
        "question_category": "availability",
        "answer": "I can join immediately.",
        "duration_seconds": 5,
        "audio_quality": 1.0,
        "background_noise": 0.0
    },
    {
        "question_id": "BACKEND_SALARY_001",
        "question": "What is your expected salary?",
        "question_category": "salary",
        "answer": "I expect 6 lakhs per year.",
        "duration_seconds": 5,
        "audio_quality": 1.0,
        "background_noise": 0.0
    }
]


# ==========================================================
# TEST CLASS
# ==========================================================

class TestDay32(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = FinalScreeningPipeline()

        cls.result = cls.pipeline.process_screening_session(
            candidate_id=CANDIDATE_ID,
            job_id=JOB_ID,
            questions=QUESTIONS
        )

        cls.summary = cls.result.get(
            "screening_summary",
            {}
        )

        cls.responses = cls.result.get(
            "responses",
            []
        )

    # ======================================================
    # DELIVERABLE 1 — FINAL PIPELINE
    # ======================================================

    def test_pipeline_returns_result(self):
        self.assertIsInstance(
            self.result,
            dict
        )

    def test_candidate_id(self):
        self.assertEqual(
            self.result.get("candidate_id"),
            CANDIDATE_ID
        )

    def test_job_id(self):
        self.assertEqual(
            self.result.get("job_id"),
            JOB_ID
        )

    def test_total_questions(self):
        self.assertEqual(
            self.summary.get("total_questions"),
            4
        )

    def test_successfully_processed(self):
        self.assertEqual(
            self.summary.get("successfully_processed"),
            4
        )

    def test_edge_cases_handled(self):
        self.assertEqual(
            self.summary.get("edge_cases_handled"),
            0
        )

    def test_final_screening_score(self):
        self.assertEqual(
            self.summary.get("final_screening_score"),
            95.0
        )

    # ======================================================
    # COMMUNICATION VALIDATION
    # ======================================================

    def test_average_communication_exists(self):
        communication = self.summary.get(
            "average_communication"
        )

        self.assertIsInstance(
            communication,
            dict
        )

    def test_confidence_score(self):
        communication = self.summary[
            "average_communication"
        ]

        self.assertEqual(
            communication.get("confidence"),
            96.25
        )

    def test_clarity_score(self):
        communication = self.summary[
            "average_communication"
        ]

        self.assertEqual(
            communication.get("clarity"),
            100.0
        )

    def test_engagement_score(self):
        communication = self.summary[
            "average_communication"
        ]

        self.assertEqual(
            communication.get("engagement"),
            73.75
        )

    def test_consistency_score(self):
        communication = self.summary[
            "average_communication"
        ]

        self.assertEqual(
            communication.get("consistency"),
            100.0
        )

    def test_communication_strength(self):
        communication = self.summary[
            "average_communication"
        ]

        self.assertEqual(
            communication.get("communication_strength"),
            92.5
        )

    # ======================================================
    # QUESTION RESULT VALIDATION
    # ======================================================

    def test_four_response_results(self):
        self.assertEqual(
            len(self.responses),
            4
        )

    def test_question_scores(self):

        expected_question_ids = [
            "BACKEND_EXP_001",
            "BACKEND_SKILLS_001",
            "BACKEND_AVAILABILITY_001",
            "BACKEND_SALARY_001"
        ]

        actual_question_ids = []

        for response in self.responses:

            question = response.get(
                "question",
                {}
            )

            actual_question_ids.append(
                question.get("question_id")
            )

        self.assertEqual(
            actual_question_ids,
            expected_question_ids
        )

    def test_all_question_scores_are_95(self):

        for response in self.responses:

            scoring = response.get(
                "screening_scoring",
                {}
            )

            self.assertEqual(
                scoring.get("normalized_score"),
                95.0
            )

    def test_all_conversation_actions(self):

        for response in self.responses:

            conversation = response.get(
                "conversation_flow",
                {}
            )

            self.assertEqual(
                conversation.get("action"),
                "next_question"
            )

    # ======================================================
    # ANSWER UNDERSTANDING VALIDATION
    # ======================================================

    def test_experience_extraction(self):

        response = self.responses[0]

        semantic = response[
            "answer_understanding"
        ][
            "semantic_object"
        ]

        experience = semantic.get(
            "experience",
            {}
        )

        self.assertEqual(
            experience.get("years"),
            3
        )

        self.assertEqual(
            experience.get("domain"),
            "backend development"
        )

    def test_skills_extraction(self):

        response = self.responses[1]

        semantic = response[
            "answer_understanding"
        ][
            "semantic_object"
        ]

        skills = semantic.get(
            "skills",
            []
        )

        self.assertIn(
            "Python",
            skills
        )

        self.assertIn(
            "Django",
            skills
        )

        self.assertIn(
            "Docker",
            skills
        )

        self.assertIn(
            "PostgreSQL",
            skills
        )

    def test_availability_extraction(self):

        response = self.responses[2]

        semantic = response[
            "answer_understanding"
        ][
            "semantic_object"
        ]

        availability = semantic.get(
            "availability",
            {}
        )

        self.assertEqual(
            availability.get("status"),
            "immediate"
        )

        self.assertEqual(
            availability.get("days"),
            0
        )

    def test_salary_extraction(self):

        response = self.responses[3]

        semantic = response[
            "answer_understanding"
        ][
            "semantic_object"
        ]

        salary = semantic.get(
            "salary_expectation",
            {}
        )

        self.assertEqual(
            salary.get("amount"),
            600000
        )

        self.assertEqual(
            salary.get("currency"),
            "INR"
        )

        self.assertEqual(
            salary.get("period"),
            "annual"
        )

    # ======================================================
    # EDGE CASE VALIDATION
    # ======================================================

    def test_no_edge_cases_in_demo(self):

        for response in self.responses:

            self.assertNotEqual(
                response.get("status"),
                "edge_case"
            )

    # ======================================================
    # DELIVERABLE 2 — DOCUMENTATION
    # ======================================================

    def test_technical_documentation_exists(self):

        documentation_file = (
            DAY32_DIR /
            "technical_documentation.md"
        )

        self.assertTrue(
            documentation_file.exists()
        )

        self.assertGreater(
            documentation_file.stat().st_size,
            0
        )

    def test_documentation_contains_required_sections(self):

        documentation_file = (
            DAY32_DIR /
            "technical_documentation.md"
        )

        content = documentation_file.read_text(
            encoding="utf-8"
        ).lower()

        required_terms = [
            "system architecture",
            "answer understanding",
            "intent classification",
            "screening scoring",
            "confidence analysis",
            "sentiment analysis",
            "behavioral indicators",
            "conversation flow",
            "edge case",
            "error handling",
            "final screening pipeline"
        ]

        for term in required_terms:

            self.assertIn(
                term,
                content
            )

    # ======================================================
    # DELIVERABLE 3 — LIVE DEMO OUTPUT
    # ======================================================

    def test_live_demo_output_exists(self):

        demo_file = (
            RESULTS_DIR /
            "live_demo_output.txt"
        )

        self.assertTrue(
            demo_file.exists()
        )

        self.assertGreater(
            demo_file.stat().st_size,
            0
        )

    def test_live_demo_output_contains_final_score(self):

        demo_file = (
            RESULTS_DIR /
            "live_demo_output.txt"
        )

        content = demo_file.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "Final Screening Score: 95.0/100",
            content
        )

    def test_live_demo_output_contains_all_questions(self):

        demo_file = (
            RESULTS_DIR /
            "live_demo_output.txt"
        )

        content = demo_file.read_text(
            encoding="utf-8"
        )

        required_question_ids = [
            "BACKEND_EXP_001",
            "BACKEND_SKILLS_001",
            "BACKEND_AVAILABILITY_001",
            "BACKEND_SALARY_001"
        ]

        for question_id in required_question_ids:

            self.assertIn(
                question_id,
                content
            )

    # ======================================================
    # RESULT JSON VALIDATION
    # ======================================================

    def test_final_pipeline_result_file_exists(self):

        result_file = (
            RESULTS_DIR /
            "final_screening_pipeline_result.json"
        )

        self.assertTrue(
            result_file.exists()
        )

        self.assertGreater(
            result_file.stat().st_size,
            0
        )

    def test_final_pipeline_result_is_valid_json(self):

        result_file = (
            RESULTS_DIR /
            "final_screening_pipeline_result.json"
        )

        with open(
            result_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.assertIsInstance(
            data,
            dict
        )

    def test_final_pipeline_json_matches_score(self):

        result_file = (
            RESULTS_DIR /
            "final_screening_pipeline_result.json"
        )

        with open(
            result_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        summary = data.get(
            "screening_summary",
            {}
        )

        self.assertEqual(
            summary.get("final_screening_score"),
            95.0
        )


# ==========================================================
# TEST RUNNER
# ==========================================================

if __name__ == "__main__":

    print()
    print("=" * 75)
    print("DAY 32 — FINAL SCREENING SYSTEM VALIDATION")
    print("=" * 75)
    print()
    print("Testing:")
    print("1. Complete AI Screening System")
    print("2. Technical Documentation")
    print("3. Live Demo Output")
    print("4. Final Result JSON")
    print()
    print("Running tests...")
    print()

    unittest.main(verbosity=2)
