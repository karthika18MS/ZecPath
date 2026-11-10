import json
import os


class HRInterviewScoringEngine:

    DEFAULT_WEIGHTS = {
        "answer_relevance": 0.30,
        "communication": 0.25,
        "confidence": 0.20,
        "consistency": 0.25
    }

    REQUIRED_QUESTION_FIELDS = {
        "question_id",
        "question_text",
        "candidate_answer",
        "answer_relevance",
        "communication_score",
        "confidence_score",
        "consistency_score"
    }

    def __init__(self, weights_file=None):
        """
        Initialize the HR Interview Scoring Engine.

        If scoring_weights.json exists, the engine loads
        the weights from that file.

        Otherwise, default weights are used.
        """

        self.weights = self.load_weights(weights_file)

    def load_weights(self, weights_file=None):
        """
        Load scoring weights from JSON configuration.
        """

        if weights_file is None:
            weights_file = os.path.join(
                os.path.dirname(__file__),
                "scoring_weights.json"
            )

        if os.path.exists(weights_file):

            try:

                with open(
                    weights_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    weights = json.load(file)

                self.validate_weights(weights)

                return weights

            except (
                json.JSONDecodeError,
                OSError,
                ValueError
            ) as error:

                print(
                    "Warning: Invalid weight configuration. "
                    f"Using default weights. Details: {error}"
                )

        return self.DEFAULT_WEIGHTS.copy()

    def validate_weights(self, weights):
        """
        Validate scoring weights.
        """

        required_parameters = {
            "answer_relevance",
            "communication",
            "confidence",
            "consistency"
        }

        if set(weights.keys()) != required_parameters:

            raise ValueError(
                "Weight configuration must contain: "
                "answer_relevance, communication, "
                "confidence, consistency"
            )

        for parameter, weight in weights.items():

            if not isinstance(
                weight,
                (int, float)
            ):

                raise ValueError(
                    f"Weight for {parameter} must be numeric."
                )

            if weight < 0 or weight > 1:

                raise ValueError(
                    f"Weight for {parameter} "
                    "must be between 0 and 1."
                )

        total_weight = sum(
            weights.values()
        )

        if round(total_weight, 6) != 1.0:

            raise ValueError(
                "Total weight must equal 1.0. "
                f"Current total: {total_weight}"
            )

    def normalize_score(self, score):
        """
        Normalize a score to the 0-100 range.
        """

        if score is None:
            return 0.0

        score = float(score)

        return round(
            max(
                0.0,
                min(100.0, score)
            ),
            2
        )

    def validate_question_data(
        self,
        question,
        index
    ):
        """
        Validate the interview question structure.

        Question text and candidate answer are required
        so Day 42 can validate complete interview data.
        """

        if not isinstance(
            question,
            dict
        ):

            raise ValueError(
                f"Question {index} "
                "must be a JSON object."
            )

        for field in self.REQUIRED_QUESTION_FIELDS:

            if field not in question:

                raise ValueError(
                    f"Question {index} "
                    f"is missing required field: {field}"
                )

        if not str(
            question["question_id"]
        ).strip():

            raise ValueError(
                f"Question {index} "
                "has an empty question_id."
            )

        if not str(
            question["question_text"]
        ).strip():

            raise ValueError(
                f"Question {index} "
                "has an empty question_text."
            )

        if not str(
            question["candidate_answer"]
        ).strip():

            raise ValueError(
                f"Question {index} "
                "has an empty candidate_answer."
            )

    def calculate_question_score(
        self,
        question
    ):
        """
        Calculate the weighted score
        for one interview question.
        """

        relevance = self.normalize_score(
            question.get(
                "answer_relevance",
                0
            )
        )

        communication = self.normalize_score(
            question.get(
                "communication_score",
                0
            )
        )

        confidence = self.normalize_score(
            question.get(
                "confidence_score",
                0
            )
        )

        consistency = self.normalize_score(
            question.get(
                "consistency_score",
                0
            )
        )

        relevance_contribution = (
            relevance *
            self.weights[
                "answer_relevance"
            ]
        )

        communication_contribution = (
            communication *
            self.weights[
                "communication"
            ]
        )

        confidence_contribution = (
            confidence *
            self.weights[
                "confidence"
            ]
        )

        consistency_contribution = (
            consistency *
            self.weights[
                "consistency"
            ]
        )

        weighted_score = (
            relevance_contribution
            + communication_contribution
            + confidence_contribution
            + consistency_contribution
        )

        return {

            "question_id":
                question.get(
                    "question_id"
                ),

            "question_text":
                question.get(
                    "question_text"
                ),

            "candidate_answer":
                question.get(
                    "candidate_answer"
                ),

            "answer_relevance":
                relevance,

            "communication_score":
                communication,

            "confidence_score":
                confidence,

            "consistency_score":
                consistency,

            "weighted_contribution": {

                "answer_relevance":
                    round(
                        relevance_contribution,
                        2
                    ),

                "communication":
                    round(
                        communication_contribution,
                        2
                    ),

                "confidence":
                    round(
                        confidence_contribution,
                        2
                    ),

                "consistency":
                    round(
                        consistency_contribution,
                        2
                    )
            },

            "question_score":
                round(
                    weighted_score,
                    2
                )
        }

    def calculate_final_score(
        self,
        question_results
    ):
        """
        Calculate normalized final HR interview score.

        The average of question-level scores is used.
        """

        if not question_results:
            return 0.0

        total_score = sum(
            result["question_score"]
            for result in question_results
        )

        average_score = (
            total_score /
            len(question_results)
        )

        return round(
            self.normalize_score(
                average_score
            ),
            2
        )

    def calculate_parameter_averages(
        self,
        question_results
    ):
        """
        Calculate average score
        for each scoring parameter.
        """

        if not question_results:

            return {
                "answer_relevance": 0.0,
                "communication": 0.0,
                "confidence": 0.0,
                "consistency": 0.0
            }

        count = len(
            question_results
        )

        relevance = sum(
            result["answer_relevance"]
            for result in question_results
        ) / count

        communication = sum(
            result["communication_score"]
            for result in question_results
        ) / count

        confidence = sum(
            result["confidence_score"]
            for result in question_results
        ) / count

        consistency = sum(
            result["consistency_score"]
            for result in question_results
        ) / count

        return {

            "answer_relevance":
                round(
                    relevance,
                    2
                ),

            "communication":
                round(
                    communication,
                    2
                ),

            "confidence":
                round(
                    confidence,
                    2
                ),

            "consistency":
                round(
                    consistency,
                    2
                )
        }

    def score_interview(
        self,
        candidate_id,
        job_id,
        interview_questions
    ):
        """
        Score the complete HR interview.
        """

        question_results = []

        for index, question in enumerate(
            interview_questions,
            start=1
        ):

            self.validate_question_data(
                question,
                index
            )

            result = self.calculate_question_score(
                question
            )

            question_results.append(
                result
            )

        final_score = (
            self.calculate_final_score(
                question_results
            )
        )

        parameter_averages = (
            self.calculate_parameter_averages(
                question_results
            )
        )

        return {

            "candidate_id":
                candidate_id,

            "job_id":
                job_id,

            "total_questions":
                len(interview_questions),

            "scoring_weights":
                self.weights,

            "parameter_averages":
                parameter_averages,

            "question_scores":
                question_results,

            "final_hr_interview_score":
                final_score,

            "score_range":
                "0-100",

            "normalization":
                "Average question score normalized "
                "to a 0-100 scale"
        }

    def save_result(
        self,
        result
    ):
        """
        Save HR interview scoring result.
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
            "hr_interview_score.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        return output_file


def main():

    engine = HRInterviewScoringEngine()

    # ---------------------------------------------------------
    # SAMPLE / DEMO INTERVIEW DATA
    # ---------------------------------------------------------
    #
    # These question texts and candidate answers are
    # demonstration data added for complete interview
    # traceability.
    #
    # They are NOT claimed to be an actual candidate
    # interview transcript.
    # ---------------------------------------------------------

    interview_questions = [

        {
            "question_id":
                "HR_SELF_001",

            "question_text":
                "Can you introduce yourself and briefly "
                "describe your technical background?",

            "candidate_answer":
                "I recently completed my MCA and have a "
                "background in software development. I have "
                "worked with Python, JavaScript, React, Node.js "
                "and databases. I am interested in backend "
                "development and enjoy solving technical "
                "problems and learning new technologies.",

            "answer_relevance":
                90,

            "communication_score":
                91.75,

            "confidence_score":
                70,

            "consistency_score":
                100
        },

        {
            "question_id":
                "HR_TEAM_001",

            "question_text":
                "Tell me about a time when you worked "
                "as part of a team on a project.",

            "candidate_answer":
                "During my academic project, I worked as part "
                "of a team where we divided the work into "
                "different modules. I was responsible for "
                "development-related tasks and coordinated "
                "with other team members when integrating "
                "the modules. We discussed issues regularly "
                "and worked together to complete the project "
                "on time.",

            "answer_relevance":
                95,

            "communication_score":
                91.75,

            "confidence_score":
                80,

            "consistency_score":
                100
        },

        {
            "question_id":
                "HR_GOALS_001",

            "question_text":
                "What are your career goals "
                "for the next few years?",

            "candidate_answer":
                "My goal is to build strong technical "
                "expertise and become a reliable software "
                "professional. I want to improve my development "
                "skills, work on real-world projects and "
                "gradually take more responsibility. I also "
                "want to keep learning new technologies that "
                "are useful for my role.",

            "answer_relevance":
                90,

            "communication_score":
                85,

            "confidence_score":
                85,

            "consistency_score":
                95
        },

        {
            "question_id":
                "HR_AVAILABILITY_001",

            "question_text":
                "Are you comfortable with the job location, "
                "working hours and availability requirements "
                "of this position?",

            "candidate_answer":
                "Yes, I am comfortable with the job requirements "
                "and working schedule. I am willing to adapt "
                "to the organization's working environment "
                "and can manage my time according to the "
                "responsibilities of the role.",

            "answer_relevance":
                100,

            "communication_score":
                90,

            "confidence_score":
                90,

            "consistency_score":
                100
        }
    ]

    result = engine.score_interview(
        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        interview_questions=interview_questions
    )

    output_file = engine.save_result(
        result
    )

    print(
        "DAY 37 — HR INTERVIEW SCORING ENGINE"
    )

    print("=" * 55)

    print(
        f"Candidate: "
        f"{result['candidate_id']}"
    )

    print(
        f"Job ID: "
        f"{result['job_id']}"
    )

    print(
        f"Total Questions: "
        f"{result['total_questions']}"
    )

    print("\nScoring Weights:")

    print(
        f"Answer Relevance: "
        f"{result['scoring_weights']['answer_relevance'] * 100}%"
    )

    print(
        f"Communication: "
        f"{result['scoring_weights']['communication'] * 100}%"
    )

    print(
        f"Confidence: "
        f"{result['scoring_weights']['confidence'] * 100}%"
    )

    print(
        f"Consistency: "
        f"{result['scoring_weights']['consistency'] * 100}%"
    )

    print("\nParameter Averages:")

    averages = result[
        "parameter_averages"
    ]

    print(
        f"Answer Relevance: "
        f"{averages['answer_relevance']}"
    )

    print(
        f"Communication: "
        f"{averages['communication']}"
    )

    print(
        f"Confidence: "
        f"{averages['confidence']}"
    )

    print(
        f"Consistency: "
        f"{averages['consistency']}"
    )

    print("\nQuestion Scores:")

    for question in result[
        "question_scores"
    ]:

        print(
            f"{question['question_id']} "
            f"→ {question['question_score']}/100"
        )

    print(
        "\nFinal HR Interview Score: "
        f"{result['final_hr_interview_score']}/100"
    )

    print(
        f"Saved Result: {output_file}"
    )


if __name__ == "__main__":
    main()