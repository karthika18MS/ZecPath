import json
import os


class InterviewSummaryGenerator:

    def __init__(self):
        self.performance_levels = {
            "strong": "Strong",
            "moderate": "Moderate",
            "needs_improvement": "Needs Improvement"
        }

    def normalize_score(self, score):
        """
        Keeps scores within the 0–100 range.
        """
        score = max(0, min(100, score))
        return round(score, 2)

    def get_performance_level(self, score):
        """
        Converts an overall score into a descriptive level.
        """

        if score >= 80:
            return "strong"

        elif score >= 60:
            return "moderate"

        return "needs_improvement"

    def calculate_overall_score(self, evaluation_data):
        """
        Calculates an overall interview performance score.

        The current model combines:
        HR interview,
        communication,
        confidence,
        logical reasoning,
        and scenario evaluation.
        """

        scores = {
            "hr_interview_score":
                evaluation_data.get("hr_interview_score", 0),

            "communication_score":
                evaluation_data.get("communication_score", 0),

            "confidence_score":
                evaluation_data.get("confidence_score", 0),

            "logical_reasoning_score":
                evaluation_data.get("logical_reasoning_score", 0),

            "scenario_score":
                evaluation_data.get("scenario_score", 0)
        }

        valid_scores = [
            score for score in scores.values()
            if isinstance(score, (int, float))
        ]

        if not valid_scores:
            return 0

        overall_score = sum(valid_scores) / len(valid_scores)

        return self.normalize_score(overall_score)

    def identify_strengths(self, evaluation_data):
        """
        Identifies strong areas based on evaluation scores.
        """

        strengths = []

        if evaluation_data.get("communication_score", 0) >= 80:
            strengths.append("Strong communication skills")

        if evaluation_data.get("confidence_score", 0) >= 80:
            strengths.append("Strong confidence indicators")

        if evaluation_data.get("logical_reasoning_score", 0) >= 80:
            strengths.append("Good logical reasoning ability")

        if evaluation_data.get("scenario_score", 0) >= 80:
            strengths.append("Good practical problem-solving ability")

        if evaluation_data.get("relevance_score", 0) >= 80:
            strengths.append("Relevant and focused responses")

        if evaluation_data.get("consistency_score", 0) >= 80:
            strengths.append("Consistent responses")

        return strengths

    def identify_weaknesses(self, evaluation_data):
        """
        Identifies areas that require improvement.
        """

        weaknesses = []

        if evaluation_data.get("communication_score", 0) < 60:
            weaknesses.append("Communication requires improvement")

        if evaluation_data.get("confidence_score", 0) < 60:
            weaknesses.append("Confidence indicators require improvement")

        if evaluation_data.get("logical_reasoning_score", 0) < 60:
            weaknesses.append("Logical reasoning requires improvement")

        if evaluation_data.get("scenario_score", 0) < 60:
            weaknesses.append("Practical problem-solving requires improvement")

        if evaluation_data.get("relevance_score", 0) < 60:
            weaknesses.append("Responses need to be more relevant")

        if evaluation_data.get("consistency_score", 0) < 60:
            weaknesses.append("Response consistency requires improvement")

        return weaknesses

    def identify_cultural_fit_indicators(self, evaluation_data):
        """
        Identifies positive workplace/cultural indicators.
        """

        indicators = []

        if evaluation_data.get("communication_score", 0) >= 80:
            indicators.append(
                "Communicates ideas clearly"
            )

        if evaluation_data.get("scenario_score", 0) >= 80:
            indicators.append(
                "Demonstrates practical problem-solving"
            )

        if evaluation_data.get("consistency_score", 0) >= 80:
            indicators.append(
                "Demonstrates consistent responses"
            )

        if evaluation_data.get("teamwork_indicator", False):
            indicators.append(
                "Demonstrates teamwork orientation"
            )

        if evaluation_data.get("adaptability_indicator", False):
            indicators.append(
                "Demonstrates adaptability"
            )

        return indicators

    def identify_risk_flags(self, evaluation_data):
        """
        Identifies areas that may require recruiter attention.
        """

        risk_flags = []

        if evaluation_data.get("confidence_score", 0) < 60:
            risk_flags.append(
                "Low confidence indicators detected"
            )

        if evaluation_data.get("consistency_score", 0) < 60:
            risk_flags.append(
                "Response consistency requires review"
            )

        if evaluation_data.get("off_topic_count", 0) > 0:
            risk_flags.append(
                "Off-topic responses detected"
            )

        if evaluation_data.get("contradiction_detected", False):
            risk_flags.append(
                "Contradictory response pattern detected"
            )

        if evaluation_data.get("missing_answer_count", 0) > 0:
            risk_flags.append(
                "Missing or incomplete responses detected"
            )

        return risk_flags

    def identify_inconsistencies(self, evaluation_data):
        """
        Identifies inconsistencies from interview analysis.
        """

        inconsistencies = []

        if evaluation_data.get("contradiction_detected", False):
            inconsistencies.append(
                "Contradictory information was detected "
                "between responses."
            )

        if evaluation_data.get("skill_experience_mismatch", False):
            inconsistencies.append(
                "A possible mismatch was detected between "
                "reported skills and experience."
            )

        if evaluation_data.get("availability_mismatch", False):
            inconsistencies.append(
                "Availability information requires verification."
            )

        return inconsistencies

    def generate_hr_performance_summary(
        self,
        overall_score,
        strengths,
        weaknesses
    ):
        """
        Generates a natural-language summary.
        """

        level = self.get_performance_level(overall_score)

        if level == "strong":

            summary = (
                "The candidate demonstrated strong overall "
                "HR interview performance. The evaluation "
                "indicates good communication, reasoning, "
                "and practical problem-solving ability."
            )

        elif level == "moderate":

            summary = (
                "The candidate demonstrated moderate overall "
                "HR interview performance. The candidate "
                "shows several positive capabilities, while "
                "some areas require further evaluation."
            )

        else:

            summary = (
                "The candidate's overall HR interview "
                "performance requires improvement. Several "
                "evaluation areas may require additional "
                "assessment."
            )

        return {
            "performance_level": self.performance_levels[level],
            "summary": summary
        }

    def generate_report(self, evaluation_data):

        overall_score = self.calculate_overall_score(
            evaluation_data
        )

        strengths = self.identify_strengths(
            evaluation_data
        )

        weaknesses = self.identify_weaknesses(
            evaluation_data
        )

        cultural_fit = self.identify_cultural_fit_indicators(
            evaluation_data
        )

        risk_flags = self.identify_risk_flags(
            evaluation_data
        )

        inconsistencies = self.identify_inconsistencies(
            evaluation_data
        )

        performance_summary = (
            self.generate_hr_performance_summary(
                overall_score,
                strengths,
                weaknesses
            )
        )

        return {
            "candidate_id":
                evaluation_data.get("candidate_id"),

            "job_id":
                evaluation_data.get("job_id"),

            "evaluation_scores": {
                "hr_interview_score":
                    evaluation_data.get(
                        "hr_interview_score"
                    ),

                "communication_score":
                    evaluation_data.get(
                        "communication_score"
                    ),

                "confidence_score":
                    evaluation_data.get(
                        "confidence_score"
                    ),

                "logical_reasoning_score":
                    evaluation_data.get(
                        "logical_reasoning_score"
                    ),

                "scenario_score":
                    evaluation_data.get(
                        "scenario_score"
                    )
            },

            "overall_hr_performance": {
                "score": overall_score,
                "level":
                    performance_summary["performance_level"],
                "summary":
                    performance_summary["summary"]
            },

            "strengths": strengths,

            "weaknesses": weaknesses,

            "cultural_fit_indicators":
                cultural_fit,

            "risk_flags":
                risk_flags,

            "inconsistencies":
                inconsistencies
        }

    def save_report(self, report, output_file):

        directory = os.path.dirname(output_file)

        if directory:
            os.makedirs(directory, exist_ok=True)

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


if __name__ == "__main__":

    print("DAY 39 — AI INTERVIEW REPORT GENERATOR")
    print("--------------------------------------")

    generator = InterviewSummaryGenerator()

    # Sample evaluation data
    # Based on the type of evaluation outputs
    # generated by the previous ZecPath modules.

    candidate_data = {

        "candidate_id": "candidate_006",

        "job_id": "JOB_BACKEND_001",

        "hr_interview_score": 91.47,

        "communication_score": 91.75,

        "confidence_score": 81.25,

        "logical_reasoning_score": 86.75,

        "scenario_score": 89.90,

        "relevance_score": 93.75,

        "consistency_score": 98.75,

        "teamwork_indicator": True,

        "adaptability_indicator": True,

        "off_topic_count": 0,

        "contradiction_detected": False,

        "missing_answer_count": 0,

        "skill_experience_mismatch": False,

        "availability_mismatch": False
    }

    report = generator.generate_report(
        candidate_data
    )

    output_file = os.path.join(
        os.path.dirname(__file__),
        "results",
        "structured_interview_summary.json"
    )

    generator.save_report(
        report,
        output_file
    )

    print(
        f"Candidate: "
        f"{report['candidate_id']}"
    )

    print(
        f"Job: "
        f"{report['job_id']}"
    )

    print()

    print("Evaluation Scores:")

    for key, value in report[
        "evaluation_scores"
    ].items():

        print(
            f"{key.replace('_', ' ').title()}: "
            f"{value}"
        )

    print()

    print(
        "Overall HR Performance:"
    )

    print(
        f"Score: "
        f"{report['overall_hr_performance']['score']}"
    )

    print(
        f"Level: "
        f"{report['overall_hr_performance']['level']}"
    )

    print()

    print("Strengths:")

    for item in report["strengths"]:
        print(f"- {item}")

    print()

    print("Weaknesses:")

    if report["weaknesses"]:
        for item in report["weaknesses"]:
            print(f"- {item}")
    else:
        print("- No major weaknesses identified")

    print()

    print("Cultural Fit Indicators:")

    for item in report[
        "cultural_fit_indicators"
    ]:
        print(f"- {item}")

    print()

    print("Risk Flags:")

    if report["risk_flags"]:
        for item in report["risk_flags"]:
            print(f"- {item}")
    else:
        print("- No major risk flags identified")

    print()

    print("Inconsistencies:")

    if report["inconsistencies"]:
        for item in report["inconsistencies"]:
            print(f"- {item}")
    else:
        print("- No major inconsistencies identified")

    print()

    print(
        f"Saved Result: {output_file}"
    )