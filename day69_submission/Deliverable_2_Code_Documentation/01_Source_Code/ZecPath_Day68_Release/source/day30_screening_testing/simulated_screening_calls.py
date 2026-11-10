import json
import sys
from datetime import datetime, timezone
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

DAY29_DIR = PROJECT_ROOT / "day29_ai_conversation_flow"

if str(DAY29_DIR) not in sys.path:
    sys.path.insert(0, str(DAY29_DIR))

from ai_call_flow import AICallFlow
from conversation_state_machine import ConversationStateMachine


class SimulatedScreeningCalls:
    """
    Creates simulated screening-call scenarios and evaluates
    how the Day 29 conversation flow responds.
    """

    def __init__(self):
        self.ai_call_flow = AICallFlow()

    def get_test_cases(self):
        """
        Return realistic screening scenarios with expected
        human judgment.
        """

        return [
            {
                "test_id": "SC001",
                "description": "Strong valid experience response",
                "question_id": "BACKEND_EXP_001",
                "question": (
                    "How many years of backend development "
                    "experience do you have?"
                ),
                "question_category": "experience",
                "answer_status": "valid",
                "intent": "experience",
                "current_answer": (
                    "I have three years of backend development "
                    "experience using Python and Django."
                ),
                "previous_answers": [],
                "expected_response_type": "valid",
                "expected_action": "next_question",
                "human_judgment": "Valid response"
            },
            {
                "test_id": "SC002",
                "description": "Vague experience response",
                "question_id": "BACKEND_EXP_001",
                "question": (
                    "How many years of backend development "
                    "experience do you have?"
                ),
                "question_category": "experience",
                "answer_status": "vague",
                "intent": "experience",
                "current_answer": (
                    "I have some backend experience."
                ),
                "previous_answers": [],
                "expected_response_type": "vague",
                "expected_action": "follow_up",
                "human_judgment": "Needs more information"
            },
            {
                "test_id": "SC003",
                "description": "Candidate gives no response",
                "question_id": "BACKEND_EXP_001",
                "question": (
                    "How many years of backend development "
                    "experience do you have?"
                ),
                "question_category": "experience",
                "answer_status": "no_response",
                "intent": "no_response",
                "current_answer": "",
                "previous_answers": [],
                "expected_response_type": "no_response",
                "expected_action": "retry",
                "human_judgment": "Retry required"
            },
            {
                "test_id": "SC004",
                "description": "Confused candidate response",
                "question_id": "BACKEND_EXP_001",
                "question": (
                    "How many years of backend development "
                    "experience do you have?"
                ),
                "question_category": "experience",
                "answer_status": "valid",
                "intent": "vague",
                "current_answer": (
                    "I'm not sure what you mean by backend development."
                ),
                "previous_answers": [],
                "expected_response_type": "confused",
                "expected_action": "clarification",
                "human_judgment": "Clarification required"
            },
            {
                "test_id": "SC005",
                "description": "Off-topic candidate response",
                "question_id": "BACKEND_EXP_001",
                "question": (
                    "How many years of backend development "
                    "experience do you have?"
                ),
                "question_category": "experience",
                "answer_status": "valid",
                "intent": "education",
                "current_answer": (
                    "I completed my MCA in 2024."
                ),
                "previous_answers": [],
                "expected_response_type": "off_topic",
                "expected_action": "redirect",
                "human_judgment": "Off-topic response"
            },
            {
                "test_id": "SC006",
                "description": "Repeated candidate answer",
                "question_id": "BACKEND_EXP_001",
                "question": (
                    "How many years of backend development "
                    "experience do you have?"
                ),
                "question_category": "experience",
                "answer_status": "valid",
                "intent": "experience",
                "current_answer": (
                    "I have three years of backend development experience."
                ),
                "previous_answers": [
                    "I have three years of backend development experience."
                ],
                "expected_response_type": "repeated",
                "expected_action": "follow_up",
                "human_judgment": "Additional information required"
            },
            {
                "test_id": "SC007",
                "description": "Relevant but incomplete skills response",
                "question_id": "BACKEND_SKILLS_001",
                "question": (
                    "What backend technologies have you worked with?"
                ),
                "question_category": "skills",
                "answer_status": "valid",
                "intent": "skills",
                "current_answer": "Python.",
                "previous_answers": [],
                "expected_response_type": "valid",
                "expected_action": "next_question",
                "human_judgment": "Valid but limited response"
            },
            {
                "test_id": "SC008",
                "description": "Salary response",
                "question_id": "BACKEND_SALARY_001",
                "question": (
                    "What are your salary expectations?"
                ),
                "question_category": "salary",
                "answer_status": "valid",
                "intent": "salary",
                "current_answer": (
                    "I am expecting around 8 lakh rupees per year."
                ),
                "previous_answers": [],
                "expected_response_type": "valid",
                "expected_action": "next_question",
                "human_judgment": "Valid salary response"
            },
            {
                "test_id": "SC009",
                "description": "Availability response",
                "question_id": "BACKEND_AVAILABILITY_001",
                "question": (
                    "When would you be available to join?"
                ),
                "question_category": "availability",
                "answer_status": "valid",
                "intent": "availability",
                "current_answer": (
                    "I can join immediately."
                ),
                "previous_answers": [],
                "expected_response_type": "valid",
                "expected_action": "next_question",
                "human_judgment": "Valid availability response"
            },
            {
                "test_id": "SC010",
                "description": "Irrelevant response to skills question",
                "question_id": "BACKEND_SKILLS_001",
                "question": (
                    "What backend technologies have you worked with?"
                ),
                "question_category": "skills",
                "answer_status": "valid",
                "intent": "location",
                "current_answer": (
                    "I am currently living in Kerala."
                ),
                "previous_answers": [],
                "expected_response_type": "off_topic",
                "expected_action": "redirect",
                "human_judgment": "Off-topic response"
            }
        ]

    def run_test_case(self, case):
        """
        Run one simulated response through the AI call-flow logic.
        """

        result = self.ai_call_flow.analyze_response(
            candidate_id="simulated_candidate",
            job_id="JOB_BACKEND_001",
            question_id=case["question_id"],
            question=case["question"],
            question_category=case["question_category"],
            answer_status=case["answer_status"],
            intent=case["intent"],
            current_answer=case["current_answer"],
            previous_answers=case["previous_answers"]
        )

        return result

    def run_all(self):
        """
        Run all simulated screening scenarios.
        """

        results = []

        for case in self.get_test_cases():
            ai_result = self.run_test_case(case)

            results.append({
                "test_id": case["test_id"],
                "description": case["description"],
                "question_category": case["question_category"],
                "human_judgment": case["human_judgment"],
                "expected_response_type": case["expected_response_type"],
                "expected_action": case["expected_action"],
                "ai_response_type": ai_result["response_type"],
                "ai_action": ai_result["decision"]["action"],
                "ai_reason": ai_result["decision"]["reason"],
                "next_prompt": ai_result["next_prompt"]
            })

        return {
            "report_type": "Simulated Screening Call Test Results",
            "total_test_cases": len(results),
            "test_cases": results,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def save_results(self, results):
        """
        Save simulated screening results.
        """

        results_dir = CURRENT_DIR / "results"
        results_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = (
            results_dir /
            "screening_simulation_results.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                results,
                file,
                indent=4
            )

        return output_path


if __name__ == "__main__":

    simulator = SimulatedScreeningCalls()

    results = simulator.run_all()

    output_path = simulator.save_results(results)

    print("\nSimulated Screening Call Results:")
    print(json.dumps(results, indent=4))

    print(f"\nResult saved to: {output_path}")