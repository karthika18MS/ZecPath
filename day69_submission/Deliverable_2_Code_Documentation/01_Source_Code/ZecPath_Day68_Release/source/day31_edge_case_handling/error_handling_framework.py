import json
from datetime import datetime
from pathlib import Path


class ErrorHandlingFramework:
    """
    Day 31 - Deliverable 2

    Handles common screening errors such as:
    - Poor audio
    - Missing answers
    - Background noise
    - Language mixing
    - Confusion
    - Vague responses
    - Repeated responses
    """

    ERROR_TYPES = [
        "poor_audio",
        "missing_answer",
        "background_noise",
        "language_mixing",
        "confused",
        "vague",
        "repeated",
        "unknown"
    ]

    ACTIONS = [
        "retry",
        "clarification",
        "follow_up",
        "redirect",
        "next_question",
        "fallback"
    ]

    DEFAULT_MAX_RETRIES = 2
    DEFAULT_MAX_FOLLOW_UPS = 2

    def __init__(
        self,
        max_retries=DEFAULT_MAX_RETRIES,
        max_follow_ups=DEFAULT_MAX_FOLLOW_UPS
    ):
        self.max_retries = max_retries
        self.max_follow_ups = max_follow_ups

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------

    def normalize_error_type(self, error_type):
        """
        Normalize the incoming error type.
        """

        if not error_type:
            return "unknown"

        error_type = str(error_type).strip().lower()

        aliases = {
            "poor audio": "poor_audio",
            "bad audio": "poor_audio",
            "audio_problem": "poor_audio",

            "missing": "missing_answer",
            "no_answer": "missing_answer",
            "no_response": "missing_answer",

            "noise": "background_noise",
            "background noise": "background_noise",

            "language mix": "language_mixing",
            "mixed_language": "language_mixing",

            "confusion": "confused",
            "confused_answer": "confused",

            "vague_answer": "vague",

            "repeated_answer": "repeated"
        }

        return aliases.get(error_type, error_type)

    # ---------------------------------------------------------
    # RETRY
    # ---------------------------------------------------------

    def handle_retry(self, error_type, retry_count):
        """
        Handle errors that require the candidate
        to repeat their answer.
        """

        if retry_count < self.max_retries:

            return {
                "status": "retry_required",
                "action": "retry",
                "error_type": error_type,
                "retry_count": retry_count + 1,
                "message": self.get_retry_message(error_type)
            }

        return {
            "status": "fallback_required",
            "action": "fallback",
            "error_type": error_type,
            "retry_count": retry_count,
            "message": (
                "We are having difficulty processing your response. "
                "We will continue with the screening process."
            )
        }

    # ---------------------------------------------------------
    # RETRY MESSAGE
    # ---------------------------------------------------------

    def get_retry_message(self, error_type):
        """
        Generate a polite retry message.
        """

        messages = {
            "poor_audio": (
                "I couldn't hear you clearly. "
                "Could you please repeat your answer?"
            ),

            "missing_answer": (
                "I didn't receive your answer. "
                "Could you please answer the question?"
            ),

            "background_noise": (
                "There seems to be some background noise. "
                "Could you please repeat your answer clearly?"
            )
        }

        return messages.get(
            error_type,
            "Could you please repeat your answer?"
        )

    # ---------------------------------------------------------
    # CLARIFICATION
    # ---------------------------------------------------------

    def handle_clarification(self, error_type):
        """
        Handle situations where the candidate needs
        clarification before answering.
        """

        messages = {
            "language_mixing": (
                "Could you please answer the question "
                "in English so I can understand your response clearly?"
            ),

            "confused": (
                "Let me clarify the question. "
                "Could you please answer it again?"
            )
        }

        return {
            "status": "clarification_required",
            "action": "clarification",
            "error_type": error_type,
            "retry_count": 0,
            "message": messages.get(
                error_type,
                "Let me clarify the question. Please try again."
            )
        }

    # ---------------------------------------------------------
    # FOLLOW-UP
    # ---------------------------------------------------------

    def handle_follow_up(self, error_type, follow_up_count):
        """
        Handle vague or repeated answers.
        """

        if follow_up_count < self.max_follow_ups:

            messages = {
                "vague": (
                    "Could you provide a little more detail "
                    "about your answer?"
                ),

                "repeated": (
                    "Could you provide a specific example "
                    "or additional detail?"
                )
            }

            return {
                "status": "follow_up_required",
                "action": "follow_up",
                "error_type": error_type,
                "follow_up_count": follow_up_count + 1,
                "message": messages.get(
                    error_type,
                    "Could you provide more details?"
                )
            }

        return {
            "status": "continue",
            "action": "next_question",
            "error_type": error_type,
            "follow_up_count": follow_up_count,
            "message": (
                "Thank you. Let's continue with the next question."
            )
        }

    # ---------------------------------------------------------
    # ERROR HANDLER
    # ---------------------------------------------------------

    def handle_error(
        self,
        error_type,
        retry_count=0,
        follow_up_count=0
    ):
        """
        Main error-handling method.

        Determines the correct recovery action
        based on the detected error.
        """

        error_type = self.normalize_error_type(error_type)

        # Unknown errors use safe fallback.
        if error_type not in self.ERROR_TYPES:
            return {
                "status": "fallback_required",
                "action": "fallback",
                "error_type": "unknown",
                "retry_count": retry_count,
                "message": (
                    "We were unable to process that response. "
                    "Let's continue with the screening."
                )
            }

        # Audio / missing answer / noise
        if error_type in [
            "poor_audio",
            "missing_answer",
            "background_noise"
        ]:
            return self.handle_retry(
                error_type,
                retry_count
            )

        # Language mixing / confusion
        if error_type in [
            "language_mixing",
            "confused"
        ]:
            return self.handle_clarification(
                error_type
            )

        # Vague / repeated
        if error_type in [
            "vague",
            "repeated"
        ]:
            return self.handle_follow_up(
                error_type,
                follow_up_count
            )

        # Safe fallback
        return {
            "status": "fallback_required",
            "action": "fallback",
            "error_type": error_type,
            "retry_count": retry_count,
            "message": (
                "We could not process the response reliably. "
                "Let's continue with the screening."
            )
        }

    # ---------------------------------------------------------
    # COMPLETE ANALYSIS
    # ---------------------------------------------------------

    def analyze_response(
        self,
        error_type,
        retry_count=0,
        follow_up_count=0
    ):
        """
        Analyze an error and return a structured
        error-handling result.
        """

        result = self.handle_error(
            error_type=error_type,
            retry_count=retry_count,
            follow_up_count=follow_up_count
        )

        result["created_at"] = (
            datetime.utcnow().isoformat() + "Z"
        )

        return result

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    def save_results(self, results):
        """
        Save error-handling results as JSON.
        """

        output_path = (
            Path(__file__).parent
            / "results"
            / "error_handling_results.json"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        report = {
            "report_type": "Error Handling Framework Results",
            "framework": "Rule-Based Screening Error Handler",
            "total_cases": len(results),
            "results": results,
            "created_at": (
                datetime.utcnow().isoformat() + "Z"
            )
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
# STANDALONE TEST / DEMONSTRATION
# =============================================================

if __name__ == "__main__":

    framework = ErrorHandlingFramework()

    test_cases = [
        {
            "case_id": "ERROR_001",
            "error_type": "poor_audio",
            "retry_count": 0
        },
        {
            "case_id": "ERROR_002",
            "error_type": "missing_answer",
            "retry_count": 0
        },
        {
            "case_id": "ERROR_003",
            "error_type": "background_noise",
            "retry_count": 0
        },
        {
            "case_id": "ERROR_004",
            "error_type": "language_mixing",
            "retry_count": 0
        },
        {
            "case_id": "ERROR_005",
            "error_type": "confused",
            "retry_count": 0
        },
        {
            "case_id": "ERROR_006",
            "error_type": "vague",
            "retry_count": 0,
            "follow_up_count": 0
        },
        {
            "case_id": "ERROR_007",
            "error_type": "repeated",
            "retry_count": 0,
            "follow_up_count": 0
        },
        {
            "case_id": "ERROR_008",
            "error_type": "poor_audio",
            "retry_count": 2
        },
        {
            "case_id": "ERROR_009",
            "error_type": "unknown_error",
            "retry_count": 0
        }
    ]

    results = []

    print("\nError Handling Framework Results")
    print("=" * 60)

    for case in test_cases:

        result = framework.analyze_response(
            error_type=case["error_type"],
            retry_count=case.get("retry_count", 0),
            follow_up_count=case.get(
                "follow_up_count",
                0
            )
        )

        result["case_id"] = case["case_id"]

        results.append(result)

        print(
            f"{case['case_id']}: "
            f"{case['error_type']} -> "
            f"{result['action']}"
        )

        print(
            f"  Message: {result['message']}"
        )

    print("=" * 60)

    output_path = framework.save_results(results)

    print(f"\nTotal cases: {len(results)}")
    print(
        f"Results saved to: {output_path}"
    )