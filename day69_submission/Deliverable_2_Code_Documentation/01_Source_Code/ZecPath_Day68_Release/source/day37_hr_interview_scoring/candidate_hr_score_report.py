import json
import os


class CandidateHRScoreReport:

    def __init__(
        self,
        score_file=None
    ):
        """
        Initialize the report generator.
        """

        if score_file is None:

            score_file = os.path.join(
                os.path.dirname(__file__),
                "results",
                "hr_interview_score.json"
            )

        self.score_file = score_file

    def load_score_data(self):
        """
        Load the HR interview scoring result.
        """

        if not os.path.exists(
            self.score_file
        ):

            raise FileNotFoundError(
                f"Score file not found: "
                f"{self.score_file}"
            )

        with open(
            self.score_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def determine_score_category(
        self,
        score
    ):
        """
        Categorize the final score.
        """

        if score >= 80:
            return "strong"

        if score >= 60:
            return "moderate"

        return "needs_improvement"

    def validate_question_data(
        self,
        question,
        index
    ):
        """
        Validate question text and candidate answer.
        """

        required_fields = [
            "question_id",
            "question_text",
            "candidate_answer"
        ]

        missing_fields = []

        for field in required_fields:

            value = question.get(
                field,
                ""
            )

            if not str(value).strip():

                missing_fields.append(
                    field
                )

        if missing_fields:

            raise ValueError(
                f"Question {index} is missing: "
                f"{', '.join(missing_fields)}"
            )

    def build_report(
        self,
        score_data
    ):
        """
        Build the candidate HR score report.
        """

        final_score = score_data[
            "final_hr_interview_score"
        ]

        parameter_averages = score_data[
            "parameter_averages"
        ]

        question_scores = score_data[
            "question_scores"
        ]

        # Validate every question
        for index, question in enumerate(
            question_scores,
            start=1
        ):

            self.validate_question_data(
                question,
                index
            )

        report = {

            "candidate_information": {

                "candidate_id":
                    score_data[
                        "candidate_id"
                    ],

                "job_id":
                    score_data[
                        "job_id"
                    ]
            },

            "interview_summary": {

                "total_questions":
                    score_data[
                        "total_questions"
                    ],

                "score_range":
                    score_data[
                        "score_range"
                    ]
            },

            "scoring_weights":
                score_data[
                    "scoring_weights"
                ],

            "parameter_scores": {

                "answer_relevance":
                    parameter_averages[
                        "answer_relevance"
                    ],

                "communication":
                    parameter_averages[
                        "communication"
                    ],

                "confidence":
                    parameter_averages[
                        "confidence"
                    ],

                "consistency":
                    parameter_averages[
                        "consistency"
                    ]
            },

            "question_score_breakdown":
                question_scores,

            "final_evaluation": {

                "final_hr_interview_score":
                    final_score,

                "score_category":
                    self.determine_score_category(
                        final_score
                    )
            },

            "explainability": {

                "method":
                    (
                        "Weighted average of answer "
                        "relevance, communication, "
                        "confidence, and consistency."
                    ),

                "normalization":
                    score_data[
                        "normalization"
                    ],

                "question_level_traceability":
                    (
                        "Each question score is linked "
                        "to its question text and "
                        "candidate answer."
                    )
            }
        }

        return report

    def save_report(
        self,
        report
    ):
        """
        Save the candidate HR score report.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(
            results_dir,
            exist_ok=True
        )

        output_file = os.path.join(
            results_dir,
            "candidate_hr_score_report.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        return output_file


def main():

    generator = CandidateHRScoreReport()

    score_data = (
        generator.load_score_data()
    )

    report = generator.build_report(
        score_data
    )

    output_file = (
        generator.save_report(
            report
        )
    )

    print(
        "DAY 37 — CANDIDATE HR SCORE REPORT"
    )

    print("=" * 55)

    print(
        f"Candidate: "
        f"{report['candidate_information']['candidate_id']}"
    )

    print(
        f"Job ID: "
        f"{report['candidate_information']['job_id']}"
    )

    print(
        f"Total Questions: "
        f"{report['interview_summary']['total_questions']}"
    )

    print("\nParameter Scores:")

    scores = report[
        "parameter_scores"
    ]

    print(
        f"Answer Relevance: "
        f"{scores['answer_relevance']}"
    )

    print(
        f"Communication: "
        f"{scores['communication']}"
    )

    print(
        f"Confidence: "
        f"{scores['confidence']}"
    )

    print(
        f"Consistency: "
        f"{scores['consistency']}"
    )

    print("\nQuestion Scores:")

    for question in report[
        "question_score_breakdown"
    ]:

        print(
            f"{question['question_id']} "
            f"→ {question['question_score']}/100"
        )

    print(
        "\nFinal HR Interview Score: "
        f"{report['final_evaluation']['final_hr_interview_score']}/100"
    )

    print(
        f"Score Category: "
        f"{report['final_evaluation']['score_category']}"
    )

    print(
        f"\nSaved Report: {output_file}"
    )


if __name__ == "__main__":
    main()