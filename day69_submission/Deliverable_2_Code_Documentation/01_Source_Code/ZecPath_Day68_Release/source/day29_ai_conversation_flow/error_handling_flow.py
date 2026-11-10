import json
from datetime import datetime, timezone
from pathlib import Path


class ErrorHandlingFlow:
    """
    Handles errors and recovery situations during AI screening calls.

    Supported situations:
    - Silence / no response
    - Confusion
    - Vague response
    - Off-topic response
    - Repeated answer

    The class provides polite recovery actions and prevents
    the conversation from getting stuck in repeated attempts.
    """

    ERROR_TYPES = {
        "no_response",
        "confused",
        "vague",
        "off_topic",
        "repeated"
    }

    ACTIONS = {
        "retry",
        "clarification",
        "follow_up",
        "redirect",
        "next_question",
        "screening_failed"
    }

    DEFAULT_MAX_RETRIES = 2
    DEFAULT_MAX_FOLLOW_UPS = 2

    def __init__(
        self,
        max_retries=DEFAULT_MAX_RETRIES,
        max_follow_ups=DEFAULT_MAX_FOLLOW_UPS
    ):
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        if max_follow_ups < 0:
            raise ValueError("max_follow_ups cannot be negative.")

        self.max_retries = max_retries
        self.max_follow_ups = max_follow_ups

    def normalize_error_type(self, error_type):
        """
        Normalize and validate the response/error type.
        """

        if not isinstance(error_type, str):
            raise ValueError("error_type must be a string.")

        normalized = error_type.strip().lower()

        if normalized not in self.ERROR_TYPES:
            raise ValueError(
                f"Unsupported error type: {error_type}"
            )

        return normalized

    def get_retry_message(self, retry_count):
        """
        Return a polite retry message based on the retry attempt.
        """

        if retry_count <= 1:
            return (
                "I didn't hear a response. "
                "Could you please answer the question?"
            )

        return (
            "No problem. I'll ask that one more time. "
            "Could you please share your answer?"
        )

    def get_clarification_message(self, question):
        """
        Return a polite clarification message.
        """

        return (
            f"Let me put that another way. "
            f"{question}"
        )

    def get_redirect_message(self, question):
        """
        Return a polite message for an off-topic response.
        """

        return (
            f"Thank you. Coming back to the question, "
            f"{question}"
        )

    def get_follow_up_message(self, question_category):
        """
        Return a category-specific follow-up question.
        """

        follow_up_questions = {
            "experience": (
                "Could you briefly describe the type of "
                "projects you worked on?"
            ),
            "skills": (
                "Could you mention some other technologies "
                "or tools you have worked with?"
            ),
            "education": (
                "Could you briefly tell me about your "
                "educational background?"
            ),
            "location": (
                "Could you please confirm your current location?"
            ),
            "salary": (
                "Could you please provide your expected "
                "salary or salary range?"
            ),
            "notice_period": (
                "Could you please tell me your expected "
                "notice period?"
            ),
            "availability": (
                "Could you please tell me when you would "
                "be available to join?"
            ),
            "introduction": (
                "Could you briefly tell me about your "
                "professional background?"
            )
        }

        return follow_up_questions.get(
            question_category,
            "Could you please provide a little more detail?"
        )

    def handle_silence(self, retry_count):
        """
        Handle candidate silence/no response.
        """

        if retry_count < self.max_retries:
            next_retry_count = retry_count + 1

            return {
                "error_type": "no_response",
                "action": "retry",
                "retry_count": next_retry_count,
                "requires_follow_up": False,
                "screening_failed": False,
                "message": self.get_retry_message(next_retry_count),
                "reason": (
                    "No response was detected. "
                    "The AI will politely retry the question."
                )
            }

        return {
            "error_type": "no_response",
            "action": "screening_failed",
            "retry_count": retry_count,
            "requires_follow_up": False,
            "screening_failed": True,
            "message": (
                "It seems we're unable to continue with the "
                "screening at the moment. Thank you for your time."
            ),
            "reason": (
                "The maximum retry limit was reached "
                "without receiving a response."
            )
        }

    def handle_confusion(self, question):
        """
        Handle a confused candidate by providing clarification.
        """

        return {
            "error_type": "confused",
            "action": "clarification",
            "retry_count": 0,
            "requires_follow_up": False,
            "screening_failed": False,
            "message": self.get_clarification_message(question),
            "reason": (
                "The candidate appears confused. "
                "The AI should clarify the question."
            )
        }

    def handle_vague(self, question_category, follow_up_count):
        """
        Handle vague answers using a limited number of follow-ups.
        """

        if follow_up_count < self.max_follow_ups:
            next_follow_up_count = follow_up_count + 1

            return {
                "error_type": "vague",
                "action": "follow_up",
                "follow_up_count": next_follow_up_count,
                "retry_count": 0,
                "requires_follow_up": True,
                "screening_failed": False,
                "message": self.get_follow_up_message(
                    question_category
                ),
                "reason": (
                    "The response is vague. "
                    "The AI will request additional information."
                )
            }

        return {
            "error_type": "vague",
            "action": "next_question",
            "follow_up_count": follow_up_count,
            "retry_count": 0,
            "requires_follow_up": False,
            "screening_failed": False,
            "message": (
                "Thank you. Let's continue with the next question."
            ),
            "reason": (
                "The maximum follow-up limit was reached."
            )
        }

    def handle_off_topic(self, question):
        """
        Handle an off-topic answer by redirecting the candidate.
        """

        return {
            "error_type": "off_topic",
            "action": "redirect",
            "retry_count": 0,
            "requires_follow_up": False,
            "screening_failed": False,
            "message": self.get_redirect_message(question),
            "reason": (
                "The response does not address the current "
                "screening question."
            )
        }

    def handle_repeated(self, question_category, follow_up_count):
        """
        Handle a repeated answer by asking for additional information.
        """

        if follow_up_count < self.max_follow_ups:
            next_follow_up_count = follow_up_count + 1

            return {
                "error_type": "repeated",
                "action": "follow_up",
                "follow_up_count": next_follow_up_count,
                "retry_count": 0,
                "requires_follow_up": True,
                "screening_failed": False,
                "message": self.get_follow_up_message(
                    question_category
                ),
                "reason": (
                    "The candidate repeated a previous answer. "
                    "The AI will ask a deeper follow-up question."
                )
            }

        return {
            "error_type": "repeated",
            "action": "next_question",
            "follow_up_count": follow_up_count,
            "retry_count": 0,
            "requires_follow_up": False,
            "screening_failed": False,
            "message": (
                "Thank you. Let's continue with the next question."
            ),
            "reason": (
                "The maximum follow-up limit was reached "
                "for the repeated response."
            )
        }

    def handle_error(
        self,
        error_type,
        question="",
        question_category="",
        retry_count=0,
        follow_up_count=0
    ):
        """
        Main error-handling method.

        Selects the appropriate recovery logic based on
        the detected response problem.
        """

        error_type = self.normalize_error_type(error_type)

        if error_type == "no_response":
            result = self.handle_silence(retry_count)

        elif error_type == "confused":
            result = self.handle_confusion(question)

        elif error_type == "vague":
            result = self.handle_vague(
                question_category,
                follow_up_count
            )

        elif error_type == "off_topic":
            result = self.handle_off_topic(question)

        elif error_type == "repeated":
            result = self.handle_repeated(
                question_category,
                follow_up_count
            )

        else:
            raise ValueError(
                f"Unsupported error type: {error_type}"
            )

        return result

    def analyze_response(
        self,
        candidate_id,
        job_id,
        question_id,
        question,
        question_category,
        error_type,
        retry_count=0,
        follow_up_count=0
    ):
        """
        Build a complete error-handling result object.
        """

        result = self.handle_error(
            error_type=error_type,
            question=question,
            question_category=question_category,
            retry_count=retry_count,
            follow_up_count=follow_up_count
        )

        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "question_id": question_id,
            "question": question,
            "question_category": question_category,
            "error_handling": result,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def save_result(
        self,
        result,
        filename="error_handling_flow_results.json"
    ):
        """
        Save error-handling result as JSON.
        """

        results_dir = (
            Path(__file__).resolve().parent / "results"
        )

        results_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = results_dir / filename

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4
            )

        return output_path


if __name__ == "__main__":

    candidate_id = "candidate_006"
    job_id = "JOB_BACKEND_001"
    question_id = "BACKEND_EXP_001"

    question = (
        "How many years of backend development "
        "experience do you have?"
    )

    error_handler = ErrorHandlingFlow()

    result = error_handler.analyze_response(
        candidate_id=candidate_id,
        job_id=job_id,
        question_id=question_id,
        question=question,
        question_category="experience",
        error_type="no_response",
        retry_count=0
    )

    output_path = error_handler.save_result(result)

    print("\nError Handling Flow Result:")
    print(json.dumps(result, indent=4))

    print(f"\nResult saved to: {output_path}")