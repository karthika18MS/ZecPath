import json
import os
from datetime import datetime

from intent_optimizer import ImprovedIntentClassifier


class OptimizedConversationFlow:
    """
    Optimized conversation logic for AI screening.

    Uses improved intent detection and additional answer-quality
    checks to decide whether the AI should:
    - continue to the next question
    - ask a follow-up
    - clarify the question
    - redirect an off-topic answer
    - retry after silence
    - end the screening safely
    """

    MAX_RETRIES = 2
    MAX_FOLLOW_UPS = 2

    ACTIONS = [
        "next_question",
        "follow_up",
        "clarification",
        "redirect",
        "retry",
        "screening_failed"
    ]

    def __init__(self):
        self.intent_classifier = ImprovedIntentClassifier()

    def normalize_text(self, text):
        """
        Normalize answer text for comparison and rule checking.
        """

        if not text:
            return ""

        return " ".join(
            str(text).lower().strip().split()
        )

    def detect_vague_answer(self, answer, question_category):
        """
        Detect whether an answer is too vague to continue
        without asking a follow-up question.
        """

        text = self.normalize_text(answer)

        if not text:
            return False

        # General vague expressions
        vague_patterns = [
            "some experience",
            "some knowledge",
            "a little experience",
            "a little knowledge",
            "not much",
            "kind of",
            "sort of",
            "maybe",
            "perhaps",
            "i think",
            "i guess",
            "i have experience",
            "i have some"
        ]

        if any(
            pattern in text
            for pattern in vague_patterns
        ):
            return True

        # Experience questions need useful experience details.
        if question_category == "experience":

            has_years = any(
                word in text
                for word in [
                    "year",
                    "years",
                    "yr",
                    "yrs",
                    "month",
                    "months"
                ]
            )

            has_domain = any(
                word in text
                for word in [
                    "backend",
                    "frontend",
                    "software",
                    "development",
                    "developer",
                    "data",
                    "testing",
                    "machine learning",
                    "analytics"
                ]
            )

            if not has_years and not has_domain:
                return True

        return False

    def detect_repeated_answer(
        self,
        current_answer,
        previous_answers=None
    ):
        """
        Detect whether the candidate repeated a previous answer.
        """

        if not current_answer or not previous_answers:
            return False

        current = self.normalize_text(current_answer)

        return any(
            current == self.normalize_text(previous)
            for previous in previous_answers
        )

    def get_clarification_message(self, question):
        """
        Message used when the candidate is confused.
        """

        return (
            "I'd be happy to clarify. "
            "Could you please answer this question directly: "
            f"{question}"
        )

    def get_redirect_message(self, question):
        """
        Message used when the candidate gives an off-topic answer.
        """

        return (
            "Thank you. Let's stay with the current question. "
            f"Could you please answer: {question}"
        )

    def get_follow_up_message(self, question_category):
        """
        Generate a category-specific follow-up question.
        """

        follow_up_questions = {

            "experience":
                "Could you briefly mention your years of "
                "experience and the relevant area you worked in?",

            "skills":
                "Could you mention the main technical skills "
                "you have experience with?",

            "education":
                "Could you briefly describe your highest "
                "qualification?",

            "location":
                "Could you tell me your current location?",

            "salary":
                "Could you provide your expected salary?",

            "availability":
                "Could you tell me when you would be available "
                "to join?",

            "notice_period":
                "Could you tell me your notice period?",

            "introduction":
                "Could you briefly introduce yourself?"
        }

        return follow_up_questions.get(
            question_category,
            "Could you please provide a little more information?"
        )

    def decide_action(
        self,
        answer,
        question,
        question_category,
        retry_count=0,
        follow_up_count=0,
        previous_answers=None
    ):
        """
        Decide the optimized conversation action.

        Decision priority:

        1. Silence
        2. Repeated answer
        3. Improved intent classification
        4. Confusion
        5. Off-topic
        6. Vague answer
        7. Valid answer
        """

        answer = answer or ""

        # ---------------------------------------------------------
        # 1. EMPTY RESPONSE / SILENCE
        # ---------------------------------------------------------

        if not self.normalize_text(answer):

            if retry_count < self.MAX_RETRIES:

                return {
                    "action": "retry",
                    "response_type": "no_response",
                    "reason": (
                        "No response detected. "
                        "Retry is allowed."
                    ),
                    "message": (
                        "I didn't hear a response. "
                        "Could you please answer the question?"
                    )
                }

            return {
                "action": "screening_failed",
                "response_type": "no_response",
                "reason": (
                    "Maximum retry attempts reached."
                ),
                "message": (
                    "I'm sorry, but I couldn't get a response. "
                    "We'll end the screening here."
                )
            }

        # ---------------------------------------------------------
        # 2. REPEATED ANSWER
        # ---------------------------------------------------------

        if self.detect_repeated_answer(
            answer,
            previous_answers
        ):

            if follow_up_count < self.MAX_FOLLOW_UPS:

                return {
                    "action": "follow_up",
                    "response_type": "repeated",
                    "reason": (
                        "Candidate repeated a previous answer."
                    ),
                    "message": self.get_follow_up_message(
                        question_category
                    )
                }

            return {
                "action": "next_question",
                "response_type": "repeated",
                "reason": (
                    "Repeated answer limit reached. "
                    "Moving forward."
                ),
                "message": (
                    "Thank you. Let's move to the next question."
                )
            }

        # ---------------------------------------------------------
        # 3. IMPROVED INTENT CLASSIFICATION
        # ---------------------------------------------------------

        classification = (
            self.intent_classifier.classify_response(
                answer,
                question_category
            )
        )

        response_type = classification["response_type"]
        detected_intent = classification["intent"]
        confidence = classification["confidence"]

        # ---------------------------------------------------------
        # 4. CONFUSION
        # ---------------------------------------------------------

        if response_type == "confused":

            return {
                "action": "clarification",
                "response_type": "confused",
                "intent": detected_intent,
                "confidence": confidence,
                "reason": (
                    "Candidate appears confused about "
                    "the question."
                ),
                "message": self.get_clarification_message(
                    question
                )
            }

        # ---------------------------------------------------------
        # 5. OFF-TOPIC
        # ---------------------------------------------------------

        if response_type == "off_topic":

            return {
                "action": "redirect",
                "response_type": "off_topic",
                "intent": detected_intent,
                "confidence": confidence,
                "reason": (
                    f"Detected intent '{detected_intent}' "
                    f"does not match question category "
                    f"'{question_category}'."
                ),
                "message": self.get_redirect_message(
                    question
                )
            }

        # ---------------------------------------------------------
        # 6. VAGUE ANSWER
        # ---------------------------------------------------------

        # Even if the intent matches the question category,
        # the answer may still be too vague to evaluate.

        if (
            response_type == "valid"
            and self.detect_vague_answer(
                answer,
                question_category
            )
        ):
            response_type = "vague"

        if response_type == "vague":

            if follow_up_count < self.MAX_FOLLOW_UPS:

                return {
                    "action": "follow_up",
                    "response_type": "vague",
                    "intent": detected_intent,
                    "confidence": confidence,
                    "reason": (
                        "Answer is too vague for reliable "
                        "screening evaluation."
                    ),
                    "message": self.get_follow_up_message(
                        question_category
                    )
                }

            return {
                "action": "next_question",
                "response_type": "vague",
                "intent": detected_intent,
                "confidence": confidence,
                "reason": (
                    "Maximum follow-up attempts reached."
                ),
                "message": (
                    "Thank you. Let's continue to "
                    "the next question."
                )
            }

        # ---------------------------------------------------------
        # 7. VALID ANSWER
        # ---------------------------------------------------------

        return {
            "action": "next_question",
            "response_type": "valid",
            "intent": detected_intent,
            "confidence": confidence,
            "reason": (
                "Candidate provided a relevant response."
            ),
            "message": (
                "Thank you. Let's move to the next question."
            )
        }

    def analyze_case(self, case):
        """
        Analyze one simulated screening case.
        """

        result = self.decide_action(
            answer=case.get("answer", ""),
            question=case.get("question", ""),
            question_category=case.get(
                "question_category",
                ""
            ),
            retry_count=case.get(
                "retry_count",
                0
            ),
            follow_up_count=case.get(
                "follow_up_count",
                0
            ),
            previous_answers=case.get(
                "previous_answers",
                []
            )
        )

        return {
            "test_id": case.get("test_id"),
            "question": case.get("question"),
            "question_category": case.get(
                "question_category"
            ),
            "answer": case.get("answer"),
            "expected_action": case.get(
                "expected_action"
            ),
            "optimized_result": result,
            "action_match": (
                result["action"]
                == case.get("expected_action")
            )
        }

    def save_results(self, results, output_path):
        """
        Save optimized conversation results.
        """

        matched_cases = sum(
            1
            for result in results
            if result["action_match"]
        )

        mismatched_cases = sum(
            1
            for result in results
            if not result["action_match"]
        )

        total_cases = len(results)

        agreement = (
            round(
                (matched_cases / total_cases) * 100,
                2
            )
            if total_cases > 0
            else 0.0
        )

        report = {
            "report_type":
                "Optimized Conversation Logic Results",

            "model":
                "Improved Rule-Based Conversation Flow",

            "optimization_focus": [
                "confusion handling",
                "off-topic redirection",
                "vague answer follow-up",
                "silence retry",
                "repeated answer handling",
                "retry limits",
                "follow-up limits"
            ],

            "total_cases": total_cases,

            "matched_cases": matched_cases,

            "mismatched_cases": mismatched_cases,

            "agreement_percentage": agreement,

            "results": results,

            "created_at":
                datetime.now()
                .astimezone()
                .isoformat()
        }

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

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

        return report


if __name__ == "__main__":

    optimizer = OptimizedConversationFlow()

    test_cases = [

        # -----------------------------------------------------
        # SC004 - CONFUSED
        # -----------------------------------------------------

        {
            "test_id": "SC004",

            "question":
                "How many years of backend development "
                "experience do you have?",

            "question_category":
                "experience",

            "answer":
                "I'm confused. What do you mean?",

            "expected_action":
                "clarification"
        },

        # -----------------------------------------------------
        # SC005 - OFF TOPIC EDUCATION
        # -----------------------------------------------------

        {
            "test_id": "SC005",

            "question":
                "How many years of backend development "
                "experience do you have?",

            "question_category":
                "experience",

            "answer":
                "I completed my MCA in Computer Applications.",

            "expected_action":
                "redirect"
        },

        # -----------------------------------------------------
        # SC010 - OFF TOPIC LOCATION
        # -----------------------------------------------------

        {
            "test_id": "SC010",

            "question":
                "What technical skills do you have?",

            "question_category":
                "skills",

            "answer":
                "I live in Kerala.",

            "expected_action":
                "redirect"
        },

        # -----------------------------------------------------
        # VAGUE ANSWER
        # -----------------------------------------------------

        {
            "test_id": "VAGUE",

            "question":
                "How many years of backend development "
                "experience do you have?",

            "question_category":
                "experience",

            "answer":
                "I have some experience.",

            "expected_action":
                "follow_up"
        },

        # -----------------------------------------------------
        # SILENCE
        # -----------------------------------------------------

        {
            "test_id": "SILENCE",

            "question":
                "What technical skills do you have?",

            "question_category":
                "skills",

            "answer":
                "",

            "expected_action":
                "retry"
        },

        # -----------------------------------------------------
        # VALID ANSWER
        # -----------------------------------------------------

        {
            "test_id": "VALID",

            "question":
                "How many years of backend development "
                "experience do you have?",

            "question_category":
                "experience",

            "answer":
                "I have three years of backend development "
                "experience.",

            "expected_action":
                "next_question"
        }
    ]

    results = []

    for case in test_cases:

        result = optimizer.analyze_case(case)

        results.append(result)

        print(
            f"{case['test_id']}: "
            f"{result['optimized_result']['action']} "
            f"(expected: "
            f"{case['expected_action']})"
        )

    output_path = os.path.join(
        os.path.dirname(__file__),
        "results",
        "conversation_optimization_results.json"
    )

    report = optimizer.save_results(
        results,
        output_path
    )

    print("\nOptimized Conversation Results:")

    print(
        json.dumps(
            report,
            indent=4
        )
    )

    print(
        f"\nResult saved to: {output_path}"
    )