import json
import os
from datetime import datetime, timezone


class FinalScoreBuilder:
    """
    Builds the final candidate screening score object
    from multiple per-question scoring results.
    """

    def calculate_average_score(
        self,
        question_scores,
        parameter
    ):
        """
        Calculate the average score for one scoring parameter.
        """

        if not question_scores:
            return 0.0

        total = sum(
            result.get("scores", {}).get(
                parameter,
                0
            )
            for result in question_scores
        )

        return round(
            total / len(question_scores),
            2
        )

    def calculate_final_score(
        self,
        question_scores
    ):
        """
        Calculate the overall normalized screening score
        from all question scores.
        """

        if not question_scores:
            return 0.0

        total = sum(
            result.get(
                "normalized_score",
                0
            )
            for result in question_scores
        )

        return round(
            total / len(question_scores),
            2
        )

    def collect_strengths(
        self,
        question_scores
    ):
        """
        Collect strengths from all question-level
        scoring results.
        """

        strengths = []

        for result in question_scores:

            explanation = result.get(
                "explanation",
                {}
            )

            question_id = result.get(
                "question_id"
            )

            for strength in explanation.get(
                "strengths",
                []
            ):

                strengths.append({
                    "question_id": question_id,
                    "reason": strength
                })

        return strengths

    def collect_weaknesses(
        self,
        question_scores
    ):
        """
        Collect weaknesses from all question-level
        scoring results.
        """

        weaknesses = []

        for result in question_scores:

            explanation = result.get(
                "explanation",
                {}
            )

            question_id = result.get(
                "question_id"
            )

            for weakness in explanation.get(
                "weaknesses",
                []
            ):

                weaknesses.append({
                    "question_id": question_id,
                    "reason": weakness
                })

        return weaknesses

    def build_final_score(
        self,
        candidate_id,
        job_id,
        question_scores
    ):
        """
        Build the complete final screening score object.
        """

        total_questions = len(
            question_scores
        )

        answered_questions = sum(
            1
            for result in question_scores
            if result.get("answer_status")
            != "no_response"
        )

        no_response_questions = sum(
            1
            for result in question_scores
            if result.get("answer_status")
            == "no_response"
        )

        off_topic_questions = sum(
            1
            for result in question_scores
            if result.get("off_topic") is True
        )

        average_clarity = (
            self.calculate_average_score(
                question_scores,
                "clarity"
            )
        )

        average_relevance = (
            self.calculate_average_score(
                question_scores,
                "relevance"
            )
        )

        average_completeness = (
            self.calculate_average_score(
                question_scores,
                "completeness"
            )
        )

        average_consistency = (
            self.calculate_average_score(
                question_scores,
                "consistency"
            )
        )

        final_score = self.calculate_final_score(
            question_scores
        )

        strengths = self.collect_strengths(
            question_scores
        )

        weaknesses = self.collect_weaknesses(
            question_scores
        )

        final_result = {

            "candidate_id": candidate_id,

            "job_id": job_id,

            "screening_summary": {

                "total_questions": total_questions,

                "answered_questions": answered_questions,

                "no_response_questions": (
                    no_response_questions
                ),

                "off_topic_questions": (
                    off_topic_questions
                )
            },

            "average_scores": {

                "clarity": average_clarity,

                "relevance": average_relevance,

                "completeness": average_completeness,

                "consistency": average_consistency
            },

            "final_screening_score": final_score,

            "score_scale": "0-100",

            "explanation": {

                "strengths": strengths,

                "weaknesses": weaknesses
            },

            "question_scores": question_scores,

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return final_result

    def save_final_score(
        self,
        final_result,
        filename
    ):
        """
        Save the final score object as JSON
        inside the results folder.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

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
                final_result,
                file,
                indent=4,
                ensure_ascii=False
            )

        return file_path


if __name__ == "__main__":

    print("=" * 70)
    print("ZecPath - Day 26")
    print("FINAL SCREENING SCORE OBJECT")
    print("=" * 70)

    builder = FinalScoreBuilder()

    # Example question-level scoring results.
    # These represent results produced by Deliverable 1.

    question_scores = [

        {
            "candidate_id": "candidate_006",
            "job_id": "JOB_BACKEND_001",
            "question_id": "BACKEND_EXP_001",

            "question": (
                "How many years of backend development "
                "experience do you have?"
            ),

            "question_category": "experience",

            "scores": {
                "clarity": 9,
                "relevance": 10,
                "completeness": 10,
                "consistency": 9
            },

            "weighted_score": 9.5,
            "normalized_score": 95.0,

            "answer_status": "valid",
            "intent": "experience",
            "off_topic": False,

            "explanation": {
                "strengths": [
                    "Answer is clear and easy to understand.",
                    "Answer directly addresses the question.",
                    "Required information is sufficiently provided.",
                    "Answer information is consistent."
                ],
                "weaknesses": []
            }
        },

        {
            "candidate_id": "candidate_006",
            "job_id": "JOB_BACKEND_001",
            "question_id": "BACKEND_SKILLS_001",

            "question": (
                "Which technical skills do you have?"
            ),

            "question_category": "skills",

            "scores": {
                "clarity": 9,
                "relevance": 10,
                "completeness": 10,
                "consistency": 9
            },

            "weighted_score": 9.5,
            "normalized_score": 95.0,

            "answer_status": "valid",
            "intent": "skills",
            "off_topic": False,

            "explanation": {
                "strengths": [
                    "Answer directly addresses the question.",
                    "Required information is sufficiently provided."
                ],
                "weaknesses": []
            }
        },

        {
            "candidate_id": "candidate_006",
            "job_id": "JOB_BACKEND_001",
            "question_id": "BACKEND_AVAILABILITY_001",

            "question": (
                "When can you join the organization?"
            ),

            "question_category": "availability",

            "scores": {
                "clarity": 8,
                "relevance": 9,
                "completeness": 8,
                "consistency": 9
            },

            "weighted_score": 8.5,
            "normalized_score": 85.0,

            "answer_status": "valid",
            "intent": "availability",
            "off_topic": False,

            "explanation": {
                "strengths": [
                    "Answer is clear and easy to understand.",
                    "Answer directly addresses the question."
                ],
                "weaknesses": [
                    "Availability information could be more specific."
                ]
            }
        },

        {
            "candidate_id": "candidate_006",
            "job_id": "JOB_BACKEND_001",
            "question_id": "BACKEND_SALARY_001",

            "question": (
                "What are your salary expectations?"
            ),

            "question_category": "salary",

            "scores": {
                "clarity": 9,
                "relevance": 10,
                "completeness": 10,
                "consistency": 9
            },

            "weighted_score": 9.5,
            "normalized_score": 95.0,

            "answer_status": "valid",
            "intent": "salary",
            "off_topic": False,

            "explanation": {
                "strengths": [
                    "Answer is clear and easy to understand.",
                    "Answer directly addresses the question.",
                    "Required information is sufficiently provided."
                ],
                "weaknesses": []
            }
        }
    ]

    # Build final score object
    final_result = builder.build_final_score(
        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_scores=question_scores
    )

    # Display result
    print(
        json.dumps(
            final_result,
            indent=4
        )
    )

    # Save result
    filename = "candidate_006_final_score.json"

    saved_path = builder.save_final_score(
        final_result,
        filename
    )

    print("\nFinal score saved to:")
    print(saved_path)

    print("=" * 70)