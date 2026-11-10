import json
import os


class FollowUpEngine:
    """
    Day 34 — Dynamic Follow-Up Logic

    Decides what action the AI should take after
    receiving a candidate's response.
    """

    MAX_FOLLOW_UPS = 2

    def __init__(self):
        self.follow_up_rules = {
            "no_response": {
                "action": "retry",
                "follow_up_type": "retry",
                "reason": "No response was captured from the candidate."
            },
            "confused": {
                "action": "clarification",
                "follow_up_type": "clarification",
                "reason": "The candidate appears confused and needs clarification."
            },
            "vague": {
                "action": "clarification",
                "follow_up_type": "clarification",
                "reason": "The candidate response is vague and needs more detail."
            },
            "incomplete": {
                "action": "clarification",
                "follow_up_type": "clarification",
                "reason": "The candidate response is incomplete."
            },
            "off_topic": {
                "action": "redirect",
                "follow_up_type": "redirect",
                "reason": "The candidate response is not related to the question."
            },
            "repeated": {
                "action": "alternate_question",
                "follow_up_type": "alternate",
                "reason": "The candidate has repeated a previous response."
            },
            "valid": {
                "action": "deepening",
                "follow_up_type": "deepening",
                "reason": "The response is valid and can be explored further."
            }
        }

    def normalize_status(self, answer_status):
        """
        Normalize the response status.
        """

        if answer_status is None:
            return "no_response"

        return str(answer_status).strip().lower()

    def can_follow_up(self, follow_up_count):
        """
        Check whether another follow-up question is allowed.
        """

        return follow_up_count < self.MAX_FOLLOW_UPS

    def determine_follow_up(self, answer_status, follow_up_count=0):
        """
        Determine the appropriate follow-up action.
        """

        status = self.normalize_status(answer_status)

        # Prevent unlimited follow-up questions
        if not self.can_follow_up(follow_up_count):
            return {
                "action": "next_question",
                "follow_up_type": "none",
                "follow_up_eligible": False,
                "reason": "Maximum follow-up limit reached.",
                "follow_up_count": follow_up_count
            }

        # Unknown status
        if status not in self.follow_up_rules:
            return {
                "action": "clarification",
                "follow_up_type": "clarification",
                "follow_up_eligible": True,
                "reason": "Response status is unclear and requires clarification.",
                "follow_up_count": follow_up_count + 1
            }

        rule = self.follow_up_rules[status]

        return {
            "action": rule["action"],
            "follow_up_type": rule["follow_up_type"],
            "follow_up_eligible": True,
            "reason": rule["reason"],
            "follow_up_count": follow_up_count + 1
        }

    def analyze_response(
        self,
        candidate_id,
        question_id,
        answer_status,
        answer="",
        follow_up_count=0
    ):
        """
        Analyze a candidate response and create
        a structured follow-up decision.
        """

        decision = self.determine_follow_up(
            answer_status,
            follow_up_count
        )

        result = {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "answer": answer,
            "answer_status": self.normalize_status(answer_status),
            "follow_up_decision": decision
        }

        return result

    def save_result(self, result, filename="follow_up_results.json"):
        """
        Save follow-up decision to the results folder.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(results_dir, exist_ok=True)

        file_path = os.path.join(results_dir, filename)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        return file_path


if __name__ == "__main__":

    engine = FollowUpEngine()

    result = engine.analyze_response(
        candidate_id="candidate_006",
        question_id="HR_TEAM_001",
        answer_status="vague",
        answer="I worked with a team.",
        follow_up_count=0
    )

    file_path = engine.save_result(result)

    print("DAY 34 — FOLLOW-UP ENGINE")
    print("=" * 40)
    print(f"Candidate: {result['candidate_id']}")
    print(f"Question ID: {result['question_id']}")
    print(f"Answer Status: {result['answer_status']}")
    print(
        f"Follow-Up Type: "
        f"{result['follow_up_decision']['follow_up_type']}"
    )
    print(
        f"Action: "
        f"{result['follow_up_decision']['action']}"
    )
    print(
        f"Follow-Up Eligible: "
        f"{result['follow_up_decision']['follow_up_eligible']}"
    )
    print(
        f"Reason: "
        f"{result['follow_up_decision']['reason']}"
    )
    print(f"Saved Result: {file_path}")