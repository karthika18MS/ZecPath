import json
from pathlib import Path


class RecruiterReportFormatter:
    """
    Converts the structured AI screening report into a
    recruiter-friendly text report.
    """

    def __init__(self, report):
        self.report = report

    def format_header(self):
        candidate_id = self.report.get("candidate_id", "N/A")
        job_id = self.report.get("job_id", "N/A")

        return (
            "\n"
            + "=" * 70
            + "\n"
            + "                    AI SCREENING REPORT\n"
            + "=" * 70
            + "\n"
            + f"Candidate ID : {candidate_id}\n"
            + f"Job ID       : {job_id}\n"
            + "=" * 70
            + "\n"
        )

    def format_screening_score(self):
        evaluation = self.report.get("screening_evaluation", {})

        final_score = evaluation.get("final_screening_score", "N/A")
        average_scores = evaluation.get("average_scores", {})
        summary = evaluation.get("screening_summary", {})

        lines = [
            "\n1. SCREENING SCORE",
            "-" * 70,
            f"Final Screening Score : {final_score}/100",
            "",
            "Average Parameter Scores:",
            f"  Clarity       : {average_scores.get('clarity', 'N/A')}/10",
            f"  Relevance     : {average_scores.get('relevance', 'N/A')}/10",
            f"  Completeness  : {average_scores.get('completeness', 'N/A')}/10",
            f"  Consistency   : {average_scores.get('consistency', 'N/A')}/10",
            "",
            "Screening Summary:",
            f"  Total Questions      : {summary.get('total_questions', 'N/A')}",
            f"  Answered Questions   : {summary.get('answered_questions', 'N/A')}",
            f"  No Response          : {summary.get('no_response_questions', 'N/A')}",
            f"  Off-topic Responses  : {summary.get('off_topic_questions', 'N/A')}",
        ]

        return "\n".join(lines)

    def format_key_answers(self):
        key_answers = self.report.get("key_answers", {})

        lines = [
            "\n2. KEY ANSWERS",
            "-" * 70,
        ]

        experience = key_answers.get("experience")

        if experience:
            lines.append("Experience:")
            lines.append(
                f"  Years  : {experience.get('years', 'N/A')}"
            )
            lines.append(
                f"  Months : {experience.get('months', 'N/A')}"
            )
            lines.append(
                f"  Domain : {experience.get('domain', 'N/A')}"
            )

        response = key_answers.get("response")

        if response:
            lines.extend(
                [
                    "",
                    "Candidate Response:",
                    f"  {response}",
                ]
            )

        if not experience and not response:
            lines.append("No key answer information available.")

        return "\n".join(lines)

    def format_highlights(self):
        highlights = self.report.get("highlights", {})

        salary = highlights.get("salary_expectation")
        availability = highlights.get("availability")
        skills = highlights.get("skill_confirmations", [])

        lines = [
            "\n3. RECRUITER HIGHLIGHTS",
            "-" * 70,
            "",
            "Skill Confirmations:",
        ]

        if skills:
            for skill in skills:
                lines.append(f"  - {skill}")
        else:
            lines.append("  - None identified")

        lines.extend(
            [
                "",
                "Salary Expectation:",
                f"  {self.format_value(salary)}",
                "",
                "Availability:",
                f"  {self.format_value(availability)}",
            ]
        )

        return "\n".join(lines)

    def format_strengths(self):
        strengths = self.report.get("strengths", [])

        lines = [
            "\n4. STRENGTHS",
            "-" * 70,
        ]

        if strengths:
            for strength in strengths:
                lines.append(f"  + {strength}")
        else:
            lines.append("  No major strengths identified.")

        return "\n".join(lines)

    def format_risks(self):
        risks = self.report.get("risks", [])

        lines = [
            "\n5. RISKS",
            "-" * 70,
        ]

        if risks:
            for risk in risks:
                lines.append(f"  ! {risk}")
        else:
            lines.append("  No major risks identified.")

        return "\n".join(lines)

    def format_missing_data(self):
        missing_data = self.report.get("missing_data", [])

        lines = [
            "\n6. MISSING DATA",
            "-" * 70,
        ]

        if missing_data:
            for item in missing_data:
                lines.append(f"  - {item}")
        else:
            lines.append("  No missing data identified.")

        return "\n".join(lines)

    def format_communication_summary(self):
        communication = self.report.get("communication_summary", {})

        lines = [
            "\n7. COMMUNICATION SUMMARY",
            "-" * 70,
        ]

        indicators = [
            ("Confidence", "confidence"),
            ("Clarity", "clarity"),
            ("Engagement", "engagement"),
            ("Consistency", "consistency"),
            ("Communication Strength", "communication_strength"),
        ]

        for label, key in indicators:
            data = communication.get(key, {})

            score = data.get("score", "N/A")
            level = data.get("level", "N/A")

            lines.append(
                f"  {label:<25}: {score}/100 ({level})"
            )

        return "\n".join(lines)

    def format_behavioral_signals(self):
        signals = self.report.get("behavioral_signals", {})

        lines = [
            "\n8. BEHAVIORAL / RESPONSE SIGNALS",
            "-" * 70,
            f"  Hesitation Count       : {signals.get('hesitation_count', 'N/A')}",
            f"  Uncertainty Count     : {signals.get('uncertainty_count', 'N/A')}",
            f"  Response Word Count   : {signals.get('response_word_count', 'N/A')}",
            f"  Response Pace         : {signals.get('pace', 'N/A')}",
            f"  Sentiment             : {signals.get('sentiment', 'N/A')}",
            f"  Sentiment Score       : {signals.get('sentiment_score', 'N/A')}",
            f"  Contradiction Detected: {signals.get('contradiction_detected', 'N/A')}",
        ]

        return "\n".join(lines)

    def format_question_scores(self):
        question_scores = self.report.get("question_scores", [])

        lines = [
            "\n9. QUESTION-WISE EVALUATION",
            "-" * 70,
        ]

        if not question_scores:
            lines.append("  No question-wise scores available.")
            return "\n".join(lines)

        for index, question in enumerate(question_scores, start=1):
            lines.extend(
                [
                    "",
                    f"Question {index}:",
                    f"  Question ID : {question.get('question_id', 'N/A')}",
                    f"  Question    : {question.get('question', 'N/A')}",
                    f"  Category    : {question.get('question_category', 'N/A')}",
                    f"  Score       : {question.get('normalized_score', 'N/A')}/100",
                    f"  Status      : {question.get('answer_status', 'N/A')}",
                    f"  Intent      : {question.get('intent', 'N/A')}",
                    f"  Off-topic   : {question.get('off_topic', 'N/A')}",
                ]
            )

            strengths = question.get("strengths", [])
            weaknesses = question.get("weaknesses", [])

            if strengths:
                lines.append("  Strengths:")
                for strength in strengths:
                    lines.append(f"    + {strength}")

            if weaknesses:
                lines.append("  Weaknesses:")
                for weakness in weaknesses:
                    lines.append(f"    - {weakness}")

        return "\n".join(lines)

    def format_footer(self):
        answer_status = self.report.get("answer_status", "N/A")
        created_at = self.report.get("created_at", "N/A")

        return (
            "\n"
            + "=" * 70
            + "\n"
            + "10. REPORT INFORMATION\n"
            + "-" * 70
            + "\n"
            + f"Answer Status : {answer_status}\n"
            + f"Created At   : {created_at}\n"
            + "=" * 70
            + "\n"
        )

    @staticmethod
    def format_value(value):
        if value is None:
            return "Not provided"

        if isinstance(value, dict):
            if not value:
                return "Not provided"

            return ", ".join(
                f"{key}: {val}"
                for key, val in value.items()
            )

        if isinstance(value, list):
            if not value:
                return "Not provided"

            return ", ".join(str(item) for item in value)

        return str(value)

    def format_report(self):
        """
        Build the complete recruiter-ready report.
        """

        sections = [
            self.format_header(),
            self.format_screening_score(),
            self.format_key_answers(),
            self.format_highlights(),
            self.format_strengths(),
            self.format_risks(),
            self.format_missing_data(),
            self.format_communication_summary(),
            self.format_behavioral_signals(),
            self.format_question_scores(),
            self.format_footer(),
        ]

        return "\n".join(sections)

    @classmethod
    def load_from_file(cls, file_path):
        """
        Load a structured AI screening report from JSON.
        """

        with open(file_path, "r", encoding="utf-8") as file:
            report = json.load(file)

        return cls(report)

    def save_report(self, file_path):
        """
        Save recruiter-ready report as a text file.
        """

        report_text = self.format_report()

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(report_text)

        return file_path


if __name__ == "__main__":

    input_file = (
        Path(__file__).parent
        / "results"
        / "candidate_006_screening_report.json"
    )

    output_file = (
        Path(__file__).parent
        / "results"
        / "candidate_006_recruiter_report.txt"
    )

    formatter = RecruiterReportFormatter.load_from_file(input_file)

    report_text = formatter.format_report()

    print(report_text)

    formatter.save_report(output_file)

    print("\nRecruiter-ready report saved to:")
    print(output_file)