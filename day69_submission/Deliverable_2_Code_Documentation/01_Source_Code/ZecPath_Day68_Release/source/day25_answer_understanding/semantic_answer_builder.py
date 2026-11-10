import os
import sys
import json
from datetime import datetime, timezone


DAY25_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    DAY25_DIR
)

from intent_classifier import IntentClassifier
from answer_extractor import AnswerExtractor


class SemanticAnswerBuilder:
    """
    Converts a candidate answer into a semantic object.

    Combines:
        - Intent
        - Answer status
        - Off-topic detection
        - Extracted information
    """

    def __init__(self):

        self.intent_classifier = (
            IntentClassifier()
        )

        self.answer_extractor = (
            AnswerExtractor()
        )

    def build(
        self,
        candidate_id,
        job_id,
        question_id,
        question,
        question_category,
        raw_answer,
        normalized_answer
    ):

        # -----------------------------------------
        # 1. Answer status
        # -----------------------------------------

        status_result = (
            self.intent_classifier
            .detect_answer_status(
                normalized_answer
            )
        )

        answer_status = status_result[
            "status"
        ]

        # -----------------------------------------
        # 2. No response
        # -----------------------------------------

        if answer_status == "no_response":

            return {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "question_id": question_id,
                "question": question,
                "question_category": question_category,
                "raw_answer": raw_answer,
                "normalized_answer": normalized_answer,
                "intent": "no_response",
                "answer_status": "no_response",
                "off_topic": False,
                "semantic_object": {},
                "confidence": 1.0,
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }

        # -----------------------------------------
        # 3. Intent
        # -----------------------------------------

        intent_result = (
            self.intent_classifier
            .classify(
                question=question,
                answer=normalized_answer,
                question_category=question_category
            )
        )

        # -----------------------------------------
        # 4. Off-topic
        # -----------------------------------------

        off_topic_result = (
            self.intent_classifier
            .detect_off_topic(
                question=question,
                answer=normalized_answer,
                question_category=question_category
            )
        )

        # -----------------------------------------
        # 5. Extract information
        # -----------------------------------------

        extracted_data = (
            self.answer_extractor
            .extract_all(
                normalized_answer
            )
        )

        # -----------------------------------------
        # 6. Build semantic object
        # -----------------------------------------

        semantic_object = {}

        if extracted_data["skills"]:
            semantic_object["skills"] = (
                extracted_data["skills"]
            )

        if extracted_data["experience"]:
            semantic_object["experience"] = (
                extracted_data["experience"]
            )

        if extracted_data["availability"]:
            semantic_object["availability"] = (
                extracted_data["availability"]
            )

        if extracted_data[
            "salary_expectation"
        ]:
            semantic_object[
                "salary_expectation"
            ] = extracted_data[
                "salary_expectation"
            ]

        # -----------------------------------------
        # 7. Final status
        # -----------------------------------------

        if off_topic_result["is_off_topic"]:

            final_status = "off_topic"

        elif answer_status == "vague":

            final_status = "vague"

        else:

            final_status = "valid"

        # -----------------------------------------
        # 8. Confidence
        # -----------------------------------------

        confidence = round(
            (
                status_result["confidence"]
                + intent_result["confidence"]
                + off_topic_result["confidence"]
            ) / 3,
            4
        )

        # -----------------------------------------
        # 9. Final object
        # -----------------------------------------

        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "question_id": question_id,
            "question": question,
            "question_category": question_category,

            "raw_answer": raw_answer,
            "normalized_answer": normalized_answer,

            "intent": intent_result["intent"],

            "answer_status": final_status,

            "off_topic": (
                off_topic_result["is_off_topic"]
            ),

            "semantic_object": semantic_object,

            "confidence": confidence,

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }


if __name__ == "__main__":

    builder = SemanticAnswerBuilder()

    result = builder.build(
        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_EXP_001",
        question=(
            "How many years of backend "
            "development experience do you have?"
        ),
        question_category="experience",
        raw_answer=(
            "Um, I have like three years of "
            "backend development experience. "
            "I have worked with Python and Django."
        ),
        normalized_answer=(
            "I have three years of backend "
            "development experience. "
            "I have worked with Python and Django."
        )
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )