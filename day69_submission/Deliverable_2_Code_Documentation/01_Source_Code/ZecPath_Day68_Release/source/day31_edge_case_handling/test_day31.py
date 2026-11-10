import json
import unittest
from pathlib import Path

from edge_case_detector import EdgeCaseDetector
from error_handling_framework import ErrorHandlingFramework
from robust_ai_flow import RobustAIFlow


BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"


class TestEdgeCaseDetector(unittest.TestCase):

    def setUp(self):
        self.detector = EdgeCaseDetector()

    def test_normal_input(self):
        result = self.detector.detect(
            transcript="I have three years of Python experience.",
            audio_quality=0.95,
            background_noise=0.10
        )

        self.assertEqual(
            result["status"],
            "normal"
        )

        self.assertIsNone(
            result["primary_error"]
        )

    def test_poor_audio(self):
        result = self.detector.detect(
            transcript="I have three years of Python experience.",
            audio_quality=0.30,
            background_noise=0.10
        )

        self.assertEqual(
            result["status"],
            "edge_case"
        )

        self.assertEqual(
            result["primary_error"],
            "poor_audio"
        )

        self.assertIn(
            "poor_audio",
            result["detected_errors"]
        )

    def test_missing_answer(self):
        result = self.detector.detect(
            transcript="",
            audio_quality=0.95,
            background_noise=0.10
        )

        self.assertEqual(
            result["status"],
            "edge_case"
        )

        self.assertEqual(
            result["primary_error"],
            "missing_answer"
        )

        self.assertIn(
            "missing_answer",
            result["detected_errors"]
        )

    def test_background_noise(self):
        result = self.detector.detect(
            transcript="I have three years of Python experience.",
            audio_quality=0.90,
            background_noise=0.85
        )

        self.assertEqual(
            result["status"],
            "edge_case"
        )

        self.assertEqual(
            result["primary_error"],
            "background_noise"
        )

        self.assertIn(
            "background_noise",
            result["detected_errors"]
        )

    def test_language_mixing(self):
        result = self.detector.detect(
            transcript=(
                "I have three years experience, "
                "njan Python use cheythittundu."
            ),
            audio_quality=0.90,
            background_noise=0.10
        )

        self.assertEqual(
            result["status"],
            "edge_case"
        )

        self.assertEqual(
            result["primary_error"],
            "language_mixing"
        )

        self.assertIn(
            "language_mixing",
            result["detected_errors"]
        )


class TestErrorHandlingFramework(unittest.TestCase):

    def setUp(self):
        self.framework = ErrorHandlingFramework()

    def test_poor_audio_retry(self):
        result = self.framework.handle_error(
            "poor_audio",
            retry_count=0
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

        self.assertEqual(
            result["retry_count"],
            1
        )

    def test_missing_answer_retry(self):
        result = self.framework.handle_error(
            "missing_answer",
            retry_count=0
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

    def test_background_noise_retry(self):
        result = self.framework.handle_error(
            "background_noise",
            retry_count=0
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

    def test_language_mixing_clarification(self):
        result = self.framework.handle_error(
            "language_mixing"
        )

        self.assertEqual(
            result["action"],
            "clarification"
        )

    def test_retry_limit(self):
        result = self.framework.handle_error(
            "poor_audio",
            retry_count=2
        )

        self.assertEqual(
            result["action"],
            "fallback"
        )

    def test_unknown_error_safe_fallback(self):
        result = self.framework.handle_error(
            "unknown_error"
        )

        self.assertEqual(
            result["action"],
            "fallback"
        )


class TestRobustAIFlow(unittest.TestCase):

    def setUp(self):
        self.flow = RobustAIFlow()

    def test_normal_flow(self):
        result = self.flow.process_input(
            transcript="I have three years of Python experience.",
            audio_quality=0.95,
            background_noise=0.10
        )

        self.assertEqual(
            result["action"],
            "continue"
        )

    def test_poor_audio_flow(self):
        result = self.flow.process_input(
            transcript="I have three years of Python experience.",
            audio_quality=0.30,
            background_noise=0.10
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

    def test_missing_answer_flow(self):
        result = self.flow.process_input(
            transcript="",
            audio_quality=0.95,
            background_noise=0.10
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

    def test_background_noise_flow(self):
        result = self.flow.process_input(
            transcript="I have three years of Python experience.",
            audio_quality=0.90,
            background_noise=0.85
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

    def test_language_mixing_flow(self):
        result = self.flow.process_input(
            transcript=(
                "I have three years experience, "
                "njan Python use cheythittundu."
            ),
            audio_quality=0.90,
            background_noise=0.10
        )

        self.assertEqual(
            result["action"],
            "clarification"
        )

    def test_safe_fallback_after_retries(self):
        result = self.flow.process_input(
            transcript="I have three years of Python experience.",
            audio_quality=0.30,
            background_noise=0.10,
            retry_count=2
        )

        self.assertEqual(
            result["action"],
            "fallback"
        )


class TestDay31Documentation(unittest.TestCase):

    def test_documentation_exists(self):

        documentation_file = (
            BASE_DIR /
            "edge_case_documentation.md"
        )

        self.assertTrue(
            documentation_file.exists()
        )

    def test_documentation_contains_edge_cases(self):

        documentation_file = (
            BASE_DIR /
            "edge_case_documentation.md"
        )

        content = documentation_file.read_text(
            encoding="utf-8"
        ).lower()

        required_topics = [
            "poor audio",
            "missing answer",
            "background noise",
            "language mixing",
            "confused",
            "vague",
            "repeated",
            "retry",
            "fallback"
        ]

        for topic in required_topics:
            self.assertIn(
                topic,
                content
            )


class TestDay31Results(unittest.TestCase):

    def test_results_directory_exists(self):

        self.assertTrue(
            RESULTS_DIR.exists()
        )

        self.assertTrue(
            RESULTS_DIR.is_dir()
        )

    def test_expected_result_files(self):

        expected_files = [
            "edge_case_detection_results.json",
            "error_handling_results.json",
            "robust_ai_flow_results.json"
        ]

        for filename in expected_files:

            file_path = (
                RESULTS_DIR / filename
            )

            self.assertTrue(
                file_path.exists(),
                f"Missing result file: {filename}"
            )

    def test_result_files_are_valid_json(self):

        expected_files = [
            "edge_case_detection_results.json",
            "error_handling_results.json",
            "robust_ai_flow_results.json"
        ]

        for filename in expected_files:

            file_path = (
                RESULTS_DIR / filename
            )

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.assertIsInstance(
                data,
                dict
            )


if __name__ == "__main__":

    print("=" * 60)
    print(
        "DAY 31 — EDGE CASE & FAILURE HANDLING"
    )
    print("=" * 60)

    print("\nDeliverables:")
    print("1. Robust AI flow logic")
    print("2. Error-handling framework")
    print("3. Edge-case documentation")

    print("\nTest Areas:")
    print("1. Poor audio")
    print("2. Language mixing")
    print("3. Missing answers")
    print("4. Background noise")
    print("5. Retry and clarification")
    print("6. Safety fallback")
    print("7. Documentation")
    print("8. Result validation")

    print("\nRunning tests...\n")

    unittest.main(verbosity=2)