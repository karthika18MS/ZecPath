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
from semantic_answer_builder import SemanticAnswerBuilder


class AnswerUnderstandingEngine:
    """
    Main Day 25 Answer Understanding Engine.

    Converts candidate screening answers into
    structured, AI-readable semantic objects.
    """

    def __init__(self):

        self.intent_classifier = (
            IntentClassifier()
        )

        self.answer_extractor = (
            AnswerExtractor()
        )

        self.semantic_builder = (
            SemanticAnswerBuilder()
        )

    def understand(
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
        # Step 1: Detect answer status
        # -----------------------------------------

        status_result = (
            self.intent_classifier
            .detect_answer_status(
                normalized_answer
            )
        )

        # -----------------------------------------
        # Step 2: Handle no response
        # -----------------------------------------

        if status_result["status"] == "no_response":

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
        # Step 3: Intent classification
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
        # Step 4: Off-topic detection
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
        # Step 5: Extract candidate information
        # -----------------------------------------

        extracted_data = (
            self.answer_extractor
            .extract_all(
                normalized_answer
            )
        )

        # -----------------------------------------
        # Step 6: Create semantic object
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
        # Step 7: Determine final answer status
        # -----------------------------------------

        if off_topic_result["is_off_topic"]:

            answer_status = "off_topic"

        elif status_result["status"] == "vague":

            answer_status = "vague"

        else:

            answer_status = "valid"

        # -----------------------------------------
        # Step 8: Calculate confidence
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
        # Step 9: Build final result
        # -----------------------------------------

        result = {

            "candidate_id": candidate_id,

            "job_id": job_id,

            "question_id": question_id,

            "question": question,

            "question_category": question_category,

            "raw_answer": raw_answer,

            "normalized_answer": normalized_answer,

            "intent": intent_result["intent"],

            "answer_status": answer_status,

            "off_topic": (
                off_topic_result["is_off_topic"]
            ),

            "semantic_object": semantic_object,

            "confidence": confidence,

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return result


if __name__ == "__main__":

    engine = AnswerUnderstandingEngine()

    result = engine.understand(

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

    print("=" * 70)
    print("ZecPath - Day 25")
    print("ANSWER UNDERSTANDING ENGINE")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    print("=" * 70)