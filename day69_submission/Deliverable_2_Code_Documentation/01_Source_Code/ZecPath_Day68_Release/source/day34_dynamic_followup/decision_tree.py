import json
import os


class DecisionTree:
    """
    Day 34 — Decision Tree Logic

    Determines the next interview action based
    on the candidate's response status.
    """

    MAX_FOLLOW_UPS = 2

    def __init__(self):
        self.rules = {
            "no_response": {
                "action": "retry",
                "reason": "No response was received from the candidate."
            },
            "confused": {
                "action": "clarification",
                "reason": "The candidate appears confused."
            },
            "vague": {
                "action": "clarification",
                "reason": "The candidate's answer is vague."
            },
            "incomplete": {
                "action": "clarification",
                "reason": "The candidate's answer is incomplete."
            },
            "off_topic": {
                "action": "redirect",
                "reason": "The candidate's answer is off-topic."
            },
            "repeated": {
                "action": "alternate_question",
                "reason": "The candidate repeated a previous response."
            },
            "valid": {
                "action": "deepening",
                "reason": "The candidate provided a valid answer."
            }
        }

    def normalize_status(self, answer_status):
        """
        Normalize answer status.
        """

        if answer_status is None:
            return "no_response"

        return str(answer_status).strip().lower()

    def evaluate(
        self,
        answer_status,
        follow_up_eligible=True,
        follow_up_count=0
    ):
        """
        Evaluate the candidate response and
        determine the next interview action.
        """

        status = self.normalize_status(answer_status)

        # Follow-up is not allowed
        if not follow_up_eligible:
            return {
                "decision": "next_question",
                "follow_up_required": False,
                "reason": "Follow-up is not eligible."
            }

        # Maximum follow-up limit
        if follow_up_count >= self.MAX_FOLLOW_UPS:
            return {
                "decision": "next_question",
                "follow_up_required": False,
                "reason": "Maximum follow-up limit reached."
            }

        # Known response status
        if status in self.rules:

            rule = self.rules[status]

            return {
                "decision": rule["action"],
                "follow_up_required": True,
                "reason": rule["reason"]
            }

        # Unknown response status
        return {
            "decision": "clarification",
            "follow_up_required": True,
            "reason": "Response status is unknown."
        }

    def build_decision(
        self,
        candidate_id,
        question_id,
        answer,
        answer_status,
        follow_up_eligible=True,
        follow_up_count=0
    ):
        """
        Build a complete structured decision object.
        """

        decision = self.evaluate(
            answer_status=answer_status,
            follow_up_eligible=follow_up_eligible,
            follow_up_count=follow_up_count
        )

        result = {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "answer": answer,
            "answer_status": self.normalize_status(answer_status),
            "follow_up_eligible": follow_up_eligible,
            "follow_up_count": follow_up_count,
            "decision": decision
        }

        return result

    def save_result(
        self,
        result,
        filename="decision_tree_results.json"
    ):
        """
        Save decision tree result.
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

    decision_tree = DecisionTree()

    result = decision_tree.build_decision(
        candidate_id="candidate_006",
        question_id="HR_TEAM_001",
        answer="I worked with a team.",
        answer_status="vague",
        follow_up_eligible=True,
        follow_up_count=0
    )

    file_path = decision_tree.save_result(result)

    print("DAY 34 — DECISION TREE")
    print("=" * 40)
    print(f"Candidate: {result['candidate_id']}")
    print(f"Question ID: {result['question_id']}")
    print(f"Answer Status: {result['answer_status']}")
    print(
        f"Decision: "
        f"{result['decision']['decision']}"
    )
    print(
        f"Follow-Up Required: "
        f"{result['decision']['follow_up_required']}"
    )
    print(
        f"Reason: "
        f"{result['decision']['reason']}"
    )
    print(f"Saved Result: {file_path}")