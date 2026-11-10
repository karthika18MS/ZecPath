import json
import re
from datetime import datetime, timezone
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CURRENT_DIR / "results"


class ImprovedIntentClassifier:
    """
    Improved intent and response classification for Day 30.

    Improvements:
    1. Detects confusion before normal intent classification.
    2. Detects off-topic responses by comparing detected intent
       with the current question category.
    3. Preserves valid responses when the intent matches the
       question category.
    4. Handles silence explicitly.
    """

    CONFUSION_PATTERNS = [
        "i don't understand",
        "i dont understand",
        "i'm confused",
        "im confused",
        "i am confused",
        "what do you mean",
        "could you explain",
        "can you explain",
        "not sure what you mean",
        "i don't know what you mean",
        "i dont know what you mean"
    ]

    OFF_TOPIC_INTENT_PATTERNS = {
        "education": [
            "mca",
            "bca",
            "btech",
            "m.tech",
            "degree",
            "graduated",
            "graduation",
            "college",
            "university",
            "education",
            "studied",
            "course"
        ],
        "location": [
            "kerala",
            "kochi",
            "trivandrum",
            "thiruvananthapuram",
            "calicut",
            "kozhikode",
            "location",
            "living",
            "live in",
            "based in"
        ],
        "experience": [
            "years of experience",
            "year of experience",
            "years experience",
            "worked with",
            "work experience",
            "professional experience",
            "backend experience",
            "development experience"
        ],
        "skills": [
            "python",
            "java",
            "javascript",
            "django",
            "fastapi",
            "flask",
            "sql",
            "mongodb",
            "postgresql",
            "docker",
            "aws",
            "react",
            "node",
            "technology",
            "technologies",
            "framework",
            "frameworks",
            "skill",
            "skills"
        ],
        "salary": [
            "salary",
            "lakh",
            "lakhs",
            "per year",
            "per annum",
            "package",
            "compensation",
            "expected pay",
            "rupees",
            "inr"
        ],
        "availability": [
            "immediately",
            "available",
            "join",
            "joining",
            "can join",
            "start",
            "available to join"
        ],
        "notice_period": [
            "notice period",
            "notice",
            "days to join",
            "months to join"
        ],
        "introduction": [
            "my name is",
            "i am",
            "i'm",
            "about myself",
            "my background"
        ]
    }

    def normalize_text(self, text):
        if not isinstance(text, str):
            return ""

        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)

        return text

    def detect_confusion(self, text):
        """
        Detect whether the candidate appears confused.
        """

        normalized = self.normalize_text(text)

        if not normalized:
            return False

        return any(
            pattern in normalized
            for pattern in self.CONFUSION_PATTERNS
        )

    def detect_intent(self, text):
        """
        Detect the most likely semantic intent from the answer.
        """

        normalized = self.normalize_text(text)

        if not normalized:
            return "no_response"

        scores = {}

        for intent, patterns in self.OFF_TOPIC_INTENT_PATTERNS.items():

            score = 0

            for pattern in patterns:
                if pattern in normalized:
                    score += 1

            if score > 0:
                scores[intent] = score

        if not scores:
            return "unknown"

        return max(
            scores,
            key=scores.get
        )

    def detect_off_topic(
        self,
        question_category,
        detected_intent
    ):
        """
        Detect whether the detected intent conflicts with
        the current question category.
        """

        if detected_intent in {
            "unknown",
            "no_response",
            question_category
        }:
            return False

        return True

    def classify_response(
        self,
        answer,
        question_category
    ):
        """
        Improved response classification.

        Priority:
        1. Silence
        2. Confusion
        3. Semantic intent
        4. Off-topic mismatch
        5. Valid / unknown
        """

        normalized = self.normalize_text(answer)

        if not normalized:
            return {
                "response_type": "no_response",
                "intent": "no_response",
                "confidence": 1.0,
                "reason": "No candidate response was provided."
            }

        if self.detect_confusion(normalized):

            return {
                "response_type": "confused",
                "intent": "confused",
                "confidence": 0.95,
                "reason": (
                    "The response contains language indicating "
                    "that the candidate does not understand "
                    "the question."
                )
            }

        detected_intent = self.detect_intent(normalized)

        if self.detect_off_topic(
            question_category,
            detected_intent
        ):

            return {
                "response_type": "off_topic",
                "intent": detected_intent,
                "confidence": 0.90,
                "reason": (
                    f"The detected intent '{detected_intent}' "
                    f"does not match the question category "
                    f"'{question_category}'."
                )
            }

        if detected_intent == question_category:

            return {
                "response_type": "valid",
                "intent": detected_intent,
                "confidence": 0.95,
                "reason": (
                    "The detected intent matches the "
                    "question category."
                )
            }

        return {
            "response_type": "valid",
            "intent": question_category,
            "confidence": 0.70,
            "reason": (
                "The response does not contain a strong "
                "conflicting intent, so it is treated as "
                "potentially relevant."
            )
        }

    def save_result(
        self,
        result,
        filename="intent_optimization_results.json"
    ):
        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = RESULTS_DIR / filename

        result["created_at"] = datetime.now(
            timezone.utc
        ).isoformat()

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

    classifier = ImprovedIntentClassifier()

    test_cases = [
        {
            "test_id": "SC004",
            "question_category": "experience",
            "answer": (
                "I'm not sure what you mean "
                "by backend development."
            )
        },
        {
            "test_id": "SC005",
            "question_category": "experience",
            "answer": (
                "I completed my MCA in 2024."
            )
        },
        {
            "test_id": "SC010",
            "question_category": "skills",
            "answer": (
                "I am currently living in Kerala."
            )
        }
    ]

    results = []

    for case in test_cases:

        classification = classifier.classify_response(
            answer=case["answer"],
            question_category=case["question_category"]
        )

        results.append({
            "test_id": case["test_id"],
            "question_category": case["question_category"],
            "answer": case["answer"],
            "classification": classification
        })

    output = {
        "report_type": "Improved Intent Classification Results",
        "improvement_focus": [
            "Confusion detection",
            "Off-topic detection",
            "Question-category matching"
        ],
        "results": results
    }

    output_path = classifier.save_result(output)

    print("\nImproved Intent Classification Results:")
    print(json.dumps(output, indent=4))

    print(
        f"\nResult saved to: {output_path}"
    )