import json
import os
from datetime import datetime, timezone

from scoring_parameters import ScoringParameters


class ScreeningScoringEngine:
    """
    Evaluates a candidate's screening response using four parameters:

    1. Clarity
    2. Relevance
    3. Completeness
    4. Consistency

    Each parameter is scored from 0 to 10.

    The final weighted score is normalized to 0-100.
    """

    def score_clarity(self, normalized_answer, answer_status):
        """
        Score how clearly the candidate communicates the answer.
        """

        if answer_status == "no_response":
            return 0

        if answer_status == "off_topic":
            return 2

        if answer_status == "vague":
            return 4

        if not normalized_answer:
            return 0

        word_count = len(normalized_answer.split())

        if word_count <= 3:
            return 7

        if word_count <= 30:
            return 9

        return 8

    def score_relevance(
        self,
        intent,
        question_category,
        off_topic
    ):
        """
        Score whether the answer is relevant to the question.
        """

        if off_topic:
            return 1

        if intent == "no_response":
            return 0

        if intent == "vague":
            return 4

        if intent == question_category:
            return 10

        return 6

    def score_completeness(
        self,
        semantic_object,
        question_category,
        answer_status
    ):
        """
        Score whether the answer contains the expected information.
        """

        if answer_status == "no_response":
            return 0

        if answer_status == "off_topic":
            return 1

        if answer_status == "vague":
            return 3

        if not semantic_object:
            return 5

        # Experience question
        if question_category == "experience":

            experience = semantic_object.get(
                "experience",
                {}
            )

            has_years = experience.get("years") is not None
            has_domain = bool(
                experience.get("domain")
            )

            if has_years and has_domain:
                return 10

            if has_years:
                return 8

            if has_domain:
                return 7

            return 5

        # Skills question
        if question_category == "skills":

            skills = semantic_object.get(
                "skills",
                []
            )

            skill_count = len(skills)

            if skill_count >= 3:
                return 10

            if skill_count == 2:
                return 9

            if skill_count == 1:
                return 7

            return 2

        # Availability question
        if question_category == "availability":

            availability = semantic_object.get(
                "availability",
                {}
            )

            if availability.get("immediate") is True:
                return 10

            if availability.get("days") is not None:
                return 10

            return 7

        # Salary question
        if question_category == "salary":

            salary = semantic_object.get(
                "salary_expectation",
                {}
            )

            has_amount = salary.get("amount") is not None
            has_currency = bool(
                salary.get("currency")
            )
            has_period = bool(
                salary.get("period")
            )

            if has_amount and has_currency and has_period:
                return 10

            return 7

        # Education / location / introduction
        if question_category in [
            "education",
            "location",
            "introduction"
        ]:

            return 8 if semantic_object else 5

        # Notice period
        if question_category == "notice_period":

            availability = semantic_object.get(
                "availability",
                {}
            )

            if availability.get("days") is not None:
                return 10

            return 5

        return 7

    def score_consistency(
        self,
        semantic_object,
        answer_status
    ):
        """
        Score whether the extracted answer information
        is logically consistent.

        This is the initial deterministic consistency
        implementation. It checks whether meaningful
        structured information was successfully extracted.
        """

        if answer_status == "no_response":
            return 0

        if answer_status == "off_topic":
            return 3

        if answer_status == "vague":
            return 5

        if not semantic_object:
            return 6

        meaningful_values = 0

        for value in semantic_object.values():

            if isinstance(value, dict):

                for nested_value in value.values():

                    if nested_value not in [
                        None,
                        "",
                        [],
                        {}
                    ]:
                        meaningful_values += 1

            elif isinstance(value, list):

                if value:
                    meaningful_values += 1

            elif value not in [
                None,
                ""
            ]:
                meaningful_values += 1

        if meaningful_values >= 1:
            return 9

        return 7

    def build_explanation(
        self,
        clarity,
        relevance,
        completeness,
        consistency,
        answer_status,
        off_topic
    ):
        """
        Create explainable strengths and weaknesses
        for the scoring result.
        """

        strengths = []
        weaknesses = []

        # Clarity
        if clarity >= 8:
            strengths.append(
                "Answer is clear and easy to understand."
            )
        elif clarity < 5:
            weaknesses.append(
                "Answer lacks clarity."
            )

        # Relevance
        if relevance >= 8:
            strengths.append(
                "Answer directly addresses the question."
            )
        elif relevance < 5:
            weaknesses.append(
                "Answer is not sufficiently relevant."
            )

        # Completeness
        if completeness >= 8:
            strengths.append(
                "Required information is sufficiently provided."
            )
        elif completeness < 5:
            weaknesses.append(
                "Answer does not provide enough required information."
            )

        # Consistency
        if consistency >= 8:
            strengths.append(
                "Answer information is consistent."
            )
        elif consistency < 5:
            weaknesses.append(
                "Answer information may be incomplete or inconsistent."
            )

        # Status-specific explanations
        if answer_status == "vague":
            weaknesses.append(
                "Answer is vague and lacks specific information."
            )

        if answer_status == "no_response":
            weaknesses.append(
                "No meaningful answer was provided."
            )

        if off_topic:
            weaknesses.append(
                "Answer does not address the screening question."
            )

        return {
            "strengths": strengths,
            "weaknesses": weaknesses
        }

    def score_response(
        self,
        candidate_id,
        job_id,
        question_id,
        question,
        question_category,
        normalized_answer,
        intent,
        answer_status,
        off_topic,
        semantic_object
    ):
        """
        Generate a complete scoring result for one
        candidate screening response.
        """

        clarity = self.score_clarity(
            normalized_answer,
            answer_status
        )

        relevance = self.score_relevance(
            intent,
            question_category,
            off_topic
        )

        completeness = self.score_completeness(
            semantic_object,
            question_category,
            answer_status
        )

        consistency = self.score_consistency(
            semantic_object,
            answer_status
        )

        # Calculate weighted score out of 10
        weighted_score = ScoringParameters.calculate_weighted_score(
            clarity=clarity,
            relevance=relevance,
            completeness=completeness,
            consistency=consistency
        )

        # Convert to 0-100
        normalized_score = ScoringParameters.normalize_score(
            weighted_score
        )

        explanation = self.build_explanation(
            clarity=clarity,
            relevance=relevance,
            completeness=completeness,
            consistency=consistency,
            answer_status=answer_status,
            off_topic=off_topic
        )

        result = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "question_id": question_id,
            "question": question,
            "question_category": question_category,

            "scores": {
                "clarity": clarity,
                "relevance": relevance,
                "completeness": completeness,
                "consistency": consistency
            },

            "weighted_score": weighted_score,
            "normalized_score": normalized_score,

            "answer_status": answer_status,
            "intent": intent,
            "off_topic": off_topic,

            "explanation": explanation,

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return result

    def save_result(self, result, filename):
        """
        Save one screening scoring result as JSON
        inside the Day 26 results folder.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        # Create results directory if it does not exist
        os.makedirs(
            results_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            results_dir,
            filename
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        return file_path


if __name__ == "__main__":

    print("=" * 70)
    print("ZecPath - Day 26")
    print("SCREENING SCORING ENGINE")
    print("=" * 70)

    engine = ScreeningScoringEngine()

    # Example Day 25 semantic answer
    result = engine.score_response(

        candidate_id="candidate_006",

        job_id="JOB_BACKEND_001",

        question_id="BACKEND_EXP_001",

        question=(
            "How many years of backend development "
            "experience do you have?"
        ),

        question_category="experience",

        normalized_answer=(
            "I have three years of backend development "
            "experience. I have worked with Python and Django."
        ),

        intent="experience",

        answer_status="valid",

        off_topic=False,

        semantic_object={
            "skills": [
                "Python",
                "Django"
            ],

            "experience": {
                "years": 3,
                "months": None,
                "domain": "backend development"
            }
        }
    )

    # Display result
    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # Save result
    filename = "candidate_006_screening_score.json"

    saved_path = engine.save_result(
        result,
        filename
    )

    print("\nResult saved to:")
    print(saved_path)

    print("=" * 70)