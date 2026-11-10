import json
from pathlib import Path


class AICallFlow:

    """
    Day 29 - Deliverable 1

    Determines the next AI action based on the
    candidate's analyzed screening response.
    """

    VALID_ACTIONS = {
        "next_question",
        "follow_up",
        "retry",
        "clarification",
        "redirect",
        "end_screening"
    }

    RESPONSE_TYPES = {
        "valid",
        "vague",
        "no_response",
        "confused",
        "off_topic",
        "repeated"
    }

    def __init__(self):
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Normalize response information
    # ---------------------------------------------------------

    def normalize_response_type(self, answer_status=None, intent=None):
        """
        Converts Day 25 answer-understanding information
        into a standard response type.
        """

        if answer_status:
            status = str(answer_status).lower().strip()

            if status in self.RESPONSE_TYPES:
                return status

        if intent:
            intent_value = str(intent).lower().strip()

            if intent_value == "off_topic":
                return "off_topic"

            if intent_value in {"vague", "no_response"}:
                return intent_value

            if intent_value == "confused":
                return "confused"

        return "valid"

    # ---------------------------------------------------------
    # 2. Detect repeated answer
    # ---------------------------------------------------------

    def detect_repeated_answer(
        self,
        current_answer,
        previous_answers=None
    ):
        """
        Detects whether the current answer is substantially
        repeated from a previous answer.

        This is a deterministic baseline based on normalized
        text equality.
        """

        if not current_answer:
            return False

        if not previous_answers:
            return False

        current = self.normalize_text(current_answer)

        if not current:
            return False

        for previous in previous_answers:

            previous_text = self.normalize_text(previous)

            if current == previous_text:
                return True

        return False

    # ---------------------------------------------------------
    # 3. Text normalization
    # ---------------------------------------------------------

    @staticmethod
    def normalize_text(text):
        """
        Normalize text for comparison.
        """

        if text is None:
            return ""

        return " ".join(str(text).lower().split())

    # ---------------------------------------------------------
    # 4. Decision logic
    # ---------------------------------------------------------

    def decide_action(
        self,
        answer_status=None,
        intent=None,
        current_answer=None,
        previous_answers=None
    ):
        """
        Decide what the AI should do next.
        """

        response_type = self.normalize_response_type(
            answer_status=answer_status,
            intent=intent
        )

        # Check repeated answer before normal valid handling.
        if self.detect_repeated_answer(
            current_answer,
            previous_answers
        ):
            response_type = "repeated"

        if response_type == "valid":

            return {
                "action": "next_question",
                "response_type": "valid",
                "reason": (
                    "Candidate provided a valid response. "
                    "The AI can continue to the next question."
                ),
                "requires_follow_up": False
            }

        if response_type == "vague":

            return {
                "action": "follow_up",
                "response_type": "vague",
                "reason": (
                    "Candidate response is vague. "
                    "The AI should request more specific information."
                ),
                "requires_follow_up": True
            }

        if response_type == "no_response":

            return {
                "action": "retry",
                "response_type": "no_response",
                "reason": (
                    "No candidate response was received. "
                    "The AI should retry the question."
                ),
                "requires_follow_up": False
            }

        if response_type == "confused":

            return {
                "action": "clarification",
                "response_type": "confused",
                "reason": (
                    "Candidate appears confused. "
                    "The AI should clarify the question."
                ),
                "requires_follow_up": True
            }

        if response_type == "off_topic":

            return {
                "action": "redirect",
                "response_type": "off_topic",
                "reason": (
                    "Candidate response is off-topic. "
                    "The AI should redirect the candidate "
                    "to the current question."
                ),
                "requires_follow_up": True
            }

        if response_type == "repeated":

            return {
                "action": "follow_up",
                "response_type": "repeated",
                "reason": (
                    "Candidate repeated information already "
                    "provided. The AI should request the "
                    "missing information."
                ),
                "requires_follow_up": True
            }

        return {
            "action": "next_question",
            "response_type": "valid",
            "reason": "Response accepted as valid.",
            "requires_follow_up": False
        }

    # ---------------------------------------------------------
    # 5. Follow-up questions
    # ---------------------------------------------------------

    def get_follow_up_question(
        self,
        question_category,
        response_type
    ):
        """
        Returns a suitable follow-up question based on
        the current question category.
        """

        category = str(question_category).lower().strip()

        follow_up_questions = {

            "experience": (
                "Could you provide more details about "
                "your relevant experience?"
            ),

            "skills": (
                "Could you mention the specific skills "
                "or technologies you have worked with?"
            ),

            "education": (
                "Could you provide more details about "
                "your educational qualification?"
            ),

            "location": (
                "Could you please confirm your current "
                "location?"
            ),

            "salary": (
                "Could you please provide your expected "
                "salary?"
            ),

            "notice_period": (
                "Could you please confirm your notice period "
                "or earliest joining date?"
            ),

            "availability": (
                "Could you please tell me when you would "
                "be available to join?"
            ),

            "introduction": (
                "Could you briefly tell me more about "
                "yourself and your professional background?"
            )
        }

        return follow_up_questions.get(
            category,
            "Could you please provide more details?"
        )

    # ---------------------------------------------------------
    # 6. Clarification question
    # ---------------------------------------------------------

    def get_clarification_question(self, question):
        """
        Creates a simple clarification prompt.
        """

        if not question:
            return "Could you please clarify your answer?"

        return (
            "No problem. Let me clarify the question: "
            f"{question}"
        )

    # ---------------------------------------------------------
    # 7. Redirect question
    # ---------------------------------------------------------

    def get_redirect_question(self, question):
        """
        Redirects an off-topic response back to the
        original question.
        """

        if not question:
            return (
                "Let's return to the current question. "
                "Could you please answer it?"
            )

        return (
            "Thank you. Let's return to the current question. "
            f"{question}"
        )

    # ---------------------------------------------------------
    # 8. Build complete call-flow decision
    # ---------------------------------------------------------

    def analyze_response(
        self,
        candidate_id,
        job_id,
        question_id,
        question,
        question_category,
        answer_status=None,
        intent=None,
        current_answer=None,
        previous_answers=None
    ):
        """
        Creates a complete AI call-flow decision object.
        """

        decision = self.decide_action(
            answer_status=answer_status,
            intent=intent,
            current_answer=current_answer,
            previous_answers=previous_answers
        )

        response_type = decision["response_type"]
        action = decision["action"]

        next_prompt = None

        if action == "follow_up":

            next_prompt = self.get_follow_up_question(
                question_category,
                response_type
            )

        elif action == "clarification":

            next_prompt = self.get_clarification_question(
                question
            )

        elif action == "redirect":

            next_prompt = self.get_redirect_question(
                question
            )

        elif action == "retry":

            next_prompt = (
                "I didn't hear your response. "
                "Could you please answer the question?"
            )

        elif action == "next_question":

            next_prompt = "Continue to the next screening question."

        result = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "question_id": question_id,
            "question": question,
            "question_category": question_category,
            "answer_status": answer_status,
            "intent": intent,
            "response_type": response_type,
            "decision": {
                "action": action,
                "reason": decision["reason"],
                "requires_follow_up": decision["requires_follow_up"]
            },
            "next_prompt": next_prompt
        }

        return result

    # ---------------------------------------------------------
    # 9. Save result
    # ---------------------------------------------------------

    def save_result(
        self,
        result,
        filename="ai_call_flow_results.json"
    ):
        """
        Save AI call-flow result as JSON.
        """

        file_path = self.results_dir / filename

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        return file_path


# -------------------------------------------------------------
# Example execution
# -------------------------------------------------------------

if __name__ == "__main__":

    flow = AICallFlow()

    result = flow.analyze_response(
        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_EXP_001",
        question=(
            "How many years of backend development "
            "experience do you have?"
        ),
        question_category="experience",
        answer_status="valid",
        intent="experience",
        current_answer=(
            "I have three years of backend development "
            "experience."
        ),
        previous_answers=[]
    )

    print("\nAI CALL FLOW LOGIC")
    print("=" * 60)
    print(json.dumps(result, indent=4))

    output_file = flow.save_result(result)

    print("\nResult saved to:")
    print(output_file)