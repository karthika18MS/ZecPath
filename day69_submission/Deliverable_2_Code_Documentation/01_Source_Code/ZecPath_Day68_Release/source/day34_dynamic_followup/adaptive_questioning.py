import json
import os


class AdaptiveQuestioning:
    """
    Day 34 — Adaptive Questioning Framework

    Selects the appropriate type of follow-up question
    based on the candidate's response.
    """

    MAX_FOLLOW_UPS = 2

    def __init__(self):
        self.question_templates = {
            "clarification": (
                "Could you please explain that in a little more detail?"
            ),

            "deepening": (
                "Could you tell me more about your experience?"
            ),

            "example_based": (
                "Could you give me a specific example?"
            ),

            "retry": (
                "I'm sorry, I didn't get your response. "
                "Could you please answer the question again?"
            ),

            "redirect": (
                "Let's focus on the question. "
                "Could you tell me about your experience related to this?"
            ),

            "alternate": (
                "Let's approach this from another perspective. "
                "Could you describe a different experience?"
            )
        }

    def normalize_status(self, answer_status):
        """
        Normalize the candidate's answer status.
        """

        if answer_status is None:
            return "no_response"

        return str(answer_status).strip().lower()

    def select_question_type(
        self,
        answer_status,
        follow_up_eligible=True,
        follow_up_count=0
    ):
        """
        Decide which type of adaptive question should be used.
        """

        status = self.normalize_status(answer_status)

        # Do not generate follow-up if it is not eligible
        if not follow_up_eligible:
            return "next_question"

        # Prevent unlimited follow-ups
        if follow_up_count >= self.MAX_FOLLOW_UPS:
            return "next_question"

        mapping = {
            "vague": "clarification",
            "incomplete": "clarification",
            "confused": "clarification",
            "no_response": "retry",
            "off_topic": "redirect",
            "repeated": "alternate",
            "valid": "deepening"
        }

        return mapping.get(status, "clarification")

    def generate_question(
        self,
        question_type,
        original_question=""
    ):
        """
        Generate an adaptive question using the
        selected question type.
        """

        if question_type == "next_question":
            return None

        question = self.question_templates.get(
            question_type,
            self.question_templates["clarification"]
        )

        return question

    def adapt_question(
        self,
        candidate_id,
        question_id,
        original_question,
        answer,
        answer_status,
        follow_up_eligible=True,
        follow_up_count=0
    ):
        """
        Complete adaptive questioning process.
        """

        question_type = self.select_question_type(
            answer_status=answer_status,
            follow_up_eligible=follow_up_eligible,
            follow_up_count=follow_up_count
        )

        adaptive_question = self.generate_question(
            question_type=question_type,
            original_question=original_question
        )

        result = {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "original_question": original_question,
            "candidate_answer": answer,
            "answer_status": self.normalize_status(answer_status),
            "follow_up_eligible": follow_up_eligible,
            "follow_up_count": follow_up_count,
            "adaptive_question_type": question_type,
            "adaptive_question": adaptive_question
        }

        return result

    def save_result(
        self,
        result,
        filename="adaptive_questioning_results.json"
    ):
        """
        Save adaptive questioning result.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(results_dir, exist_ok=True)

        file_path = os.path.join(
            results_dir,
            filename
        )

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        return file_path


if __name__ == "__main__":

    adaptive = AdaptiveQuestioning()

    result = adaptive.adapt_question(
        candidate_id="candidate_006",
        question_id="HR_TEAM_001",
        original_question=(
            "Tell me about your teamwork experience."
        ),
        answer="I worked with a team.",
        answer_status="vague",
        follow_up_eligible=True,
        follow_up_count=0
    )

    file_path = adaptive.save_result(result)

    print("DAY 34 — ADAPTIVE QUESTIONING")
    print("=" * 40)
    print(f"Candidate: {result['candidate_id']}")
    print(f"Question ID: {result['question_id']}")
    print(f"Answer Status: {result['answer_status']}")
    print(
        f"Adaptive Question Type: "
        f"{result['adaptive_question_type']}"
    )
    print(
        f"Adaptive Question: "
        f"{result['adaptive_question']}"
    )
    print(f"Follow-Up Count: {result['follow_up_count']}")
    print(f"Saved Result: {file_path}")