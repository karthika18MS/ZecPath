import json
from datetime import datetime
from pathlib import Path

from edge_case_detector import EdgeCaseDetector
from error_handling_framework import ErrorHandlingFramework


class RobustAIFlow:
    """
    Day 31 - Deliverable 1

    Connects:
    Edge Case Detector
            +
    Error Handling Framework
            =
    Robust AI Screening Flow
    """

    def __init__(self):
        self.detector = EdgeCaseDetector()
        self.error_handler = ErrorHandlingFramework()

    # ---------------------------------------------------------
    # PROCESS SINGLE INPUT
    # ---------------------------------------------------------

    def process_input(
        self,
        transcript,
        audio_quality=1.0,
        background_noise=0.0,
        retry_count=0,
        follow_up_count=0
    ):
        """
        Detect edge cases and select the appropriate
        recovery action.
        """

        detection = self.detector.detect(
            transcript=transcript,
            audio_quality=audio_quality,
            background_noise=background_noise
        )

        # -----------------------------------------------------
        # NORMAL INPUT
        # -----------------------------------------------------

        if detection["status"] == "normal":

            return {
                "status": "success",
                "action": "continue",
                "error_type": None,
                "retry_count": retry_count,
                "follow_up_count": follow_up_count,
                "message": (
                    "Input processed successfully."
                ),
                "edge_case_detection": detection
            }

        # -----------------------------------------------------
        # EDGE CASE
        # -----------------------------------------------------

        error_type = detection["primary_error"]

        handling = self.error_handler.handle_error(
            error_type=error_type,
            retry_count=retry_count,
            follow_up_count=follow_up_count
        )

        return {
            "status": handling["status"],
            "action": handling["action"],
            "error_type": error_type,
            "retry_count": handling.get(
                "retry_count",
                retry_count
            ),
            "follow_up_count": handling.get(
                "follow_up_count",
                follow_up_count
            ),
            "message": handling["message"],
            "edge_case_detection": detection,
            "error_handling": handling
        }

    # ---------------------------------------------------------
    # PROCESS MULTIPLE CASES
    # ---------------------------------------------------------

    def process_batch(self, test_cases):
        """
        Process multiple edge-case scenarios.
        """

        results = []

        for case in test_cases:

            result = self.process_input(
                transcript=case.get(
                    "transcript",
                    ""
                ),
                audio_quality=case.get(
                    "audio_quality",
                    1.0
                ),
                background_noise=case.get(
                    "background_noise",
                    0.0
                ),
                retry_count=case.get(
                    "retry_count",
                    0
                ),
                follow_up_count=case.get(
                    "follow_up_count",
                    0
                )
            )

            actual_action = result["action"]

            expected_action = case[
                "expected_action"
            ]

            matched = (
                actual_action == expected_action
            )

            results.append({
                "case_id": case["case_id"],
                "expected_action": expected_action,
                "actual_action": actual_action,
                "matched": matched,
                "result": result
            })

        return results

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    def save_results(self, results):

        output_path = (
            Path(__file__).parent
            / "results"
            / "robust_ai_flow_results.json"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        matched = sum(
            1
            for result in results
            if result["matched"]
        )

        mismatched = (
            len(results) - matched
        )

        agreement = (
            (matched / len(results)) * 100
            if results
            else 0
        )

        report = {
            "report_type":
                "Robust AI Flow Results",

            "total_cases":
                len(results),

            "matched_cases":
                matched,

            "mismatched_cases":
                mismatched,

            "agreement_percentage":
                round(agreement, 2),

            "results":
                results,

            "created_at":
                datetime.utcnow().isoformat() + "Z"
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        return output_path


# =============================================================
# STANDALONE TEST
# =============================================================

if __name__ == "__main__":

    flow = RobustAIFlow()

    test_cases = [

        # -----------------------------------------------------
        # NORMAL
        # -----------------------------------------------------

        {
            "case_id": "NORMAL_001",

            "transcript":
                "I have three years of "
                "Python experience.",

            "audio_quality": 0.95,

            "background_noise": 0.10,

            "expected_action":
                "continue"
        },

        # -----------------------------------------------------
        # POOR AUDIO
        # -----------------------------------------------------

        {
            "case_id": "POOR_AUDIO_001",

            "transcript":
                "I have three years of "
                "Python experience.",

            "audio_quality": 0.30,

            "background_noise": 0.10,

            "expected_action":
                "retry"
        },

        # -----------------------------------------------------
        # MISSING ANSWER
        # -----------------------------------------------------

        {
            "case_id": "MISSING_ANSWER_001",

            "transcript": "",

            "audio_quality": 0.95,

            "background_noise": 0.10,

            "expected_action":
                "retry"
        },

        # -----------------------------------------------------
        # BACKGROUND NOISE
        # -----------------------------------------------------

        {
            "case_id": "BACKGROUND_NOISE_001",

            "transcript":
                "I have three years of "
                "Python experience.",

            "audio_quality": 0.90,

            "background_noise": 0.85,

            "expected_action":
                "retry"
        },

        # -----------------------------------------------------
        # LANGUAGE MIXING
        # -----------------------------------------------------

        {
            "case_id": "LANGUAGE_MIXING_001",

            "transcript":
                "I have three years experience, "
                "njan Python use cheythittundu.",

            "audio_quality": 0.90,

            "background_noise": 0.10,

            "expected_action":
                "clarification"
        },

        # -----------------------------------------------------
        # RETRY LIMIT
        # -----------------------------------------------------

        {
            "case_id": "RETRY_LIMIT_001",

            "transcript":
                "I have three years of "
                "Python experience.",

            "audio_quality": 0.30,

            "background_noise": 0.10,

            "retry_count": 2,

            "expected_action":
                "fallback"
        }
    ]

    results = flow.process_batch(
        test_cases
    )

    matched = sum(
        1
        for result in results
        if result["matched"]
    )

    print("\nRobust AI Flow Results:")
    print("=" * 60)

    for result in results:

        print(
            f"{result['case_id']}: "
            f"{result['actual_action']} "
            f"(expected: "
            f"{result['expected_action']})"
        )

    print("\nSummary:")

    summary = {
        "total_cases": len(results),
        "matched_cases": matched,
        "mismatched_cases":
            len(results) - matched,
        "agreement_percentage":
            round(
                (matched / len(results)) * 100,
                2
            )
    }

    print(
        json.dumps(
            summary,
            indent=4
        )
    )

    output_path = flow.save_results(
        results
    )

    print(
        f"\nResult saved to: {output_path}"
    )