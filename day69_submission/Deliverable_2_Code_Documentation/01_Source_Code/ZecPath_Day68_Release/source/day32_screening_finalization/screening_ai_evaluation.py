import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

PIPELINE_RESULT_FILE = RESULTS_DIR / "final_screening_pipeline_result.json"
JSON_REPORT_FILE = RESULTS_DIR / "screening_ai_evaluation_report.json"
TEXT_REPORT_FILE = RESULTS_DIR / "screening_ai_evaluation_report.txt"


class ScreeningAIEvaluator:
    """
    Evaluates the final Day 32 ZecPath AI screening pipeline.

    The evaluator reads the actual final screening pipeline output
    and produces a structured evaluation report.
    """

    def __init__(self, pipeline_result_file=PIPELINE_RESULT_FILE):
        self.pipeline_result_file = Path(pipeline_result_file)

    def load_pipeline_result(self):
        """Load the final screening pipeline JSON result."""

        if not self.pipeline_result_file.exists():
            raise FileNotFoundError(
                f"Pipeline result not found: {self.pipeline_result_file}"
            )

        with open(self.pipeline_result_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def evaluate_question_processing(self, result):
        """Evaluate question processing performance."""

        summary = result.get("screening_summary", {})
        responses = result.get("responses", [])

        total_questions = summary.get("total_questions", len(responses))
        successfully_processed = summary.get(
            "successfully_processed",
            len(responses)
        )

        if total_questions > 0:
            processing_rate = round(
                (successfully_processed / total_questions) * 100,
                2
            )
        else:
            processing_rate = 0.0

        return {
            "total_questions": total_questions,
            "successfully_processed": successfully_processed,
            "processing_success_rate": processing_rate
        }

    def evaluate_screening_scores(self, result):
        """Evaluate question-level and final screening scores."""

        summary = result.get("screening_summary", {})
        responses = result.get("responses", [])

        question_scores = []

        for response in responses:
            scoring = response.get("screening_scoring", {})

            score = scoring.get("normalized_score")

            if score is None:
                score = scoring.get("final_score")

            if score is not None:
                question_scores.append(float(score))

        if question_scores:
            average_question_score = round(
                sum(question_scores) / len(question_scores),
                2
            )
        else:
            average_question_score = 0.0

        final_score = float(
            summary.get("final_screening_score", 0)
        )

        return {
            "question_scores": question_scores,
            "questions_with_scores": len(question_scores),
            "average_question_score": average_question_score,
            "final_screening_score": final_score
        }

    def evaluate_communication(self, result):
        """Evaluate communication analysis."""

        summary = result.get("screening_summary", {})
        communication = summary.get("average_communication", {})

        return {
            "confidence": communication.get("confidence", 0),
            "clarity": communication.get("clarity", 0),
            "engagement": communication.get("engagement", 0),
            "consistency": communication.get("consistency", 0),
            "communication_strength": communication.get(
                "communication_strength",
                0
            )
        }

    def evaluate_conversation_flow(self, result):
        """Evaluate conversation decisions."""

        responses = result.get("responses", [])

        actions = []

        for response in responses:
            conversation = response.get("conversation_flow", {})
            action = conversation.get("action")

            if action:
                actions.append(action)

        action_counts = {}

        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_conversation_decisions": len(actions),
            "actions": actions,
            "action_counts": action_counts,
            "all_decisions_available": (
                len(actions) == len(responses)
            )
        }

    def evaluate_edge_cases(self, result):
        """Evaluate edge case handling."""

        summary = result.get("screening_summary", {})

        edge_cases_handled = summary.get(
            "edge_cases_handled",
            0
        )

        return {
            "edge_cases_handled": edge_cases_handled,
            "edge_case_free_demo": edge_cases_handled == 0
        }

    def evaluate_candidate_extraction(self, result):
        """Evaluate extracted candidate information."""

        responses = result.get("responses", [])

        skills = set()
        experience_years = None
        experience_domain = None
        availability = None
        salary_amount = None
        salary_currency = None
        salary_period = None

        for response in responses:

            answer_understanding = response.get(
                "answer_understanding",
                {}
            )

            semantic = answer_understanding.get(
                "semantic_object",
                {}
            )

            # Skills
            extracted_skills = semantic.get("skills", [])

            if isinstance(extracted_skills, list):
                for skill in extracted_skills:
                    skills.add(str(skill))

            # Experience
            experience = semantic.get("experience", {})

            if isinstance(experience, dict):
                if experience.get("years") is not None:
                    experience_years = experience.get("years")

                if experience.get("domain"):
                    experience_domain = experience.get("domain")

            # Availability
            extracted_availability = semantic.get(
                "availability"
            )

            if extracted_availability:
                availability = extracted_availability

            # Salary
            salary = semantic.get(
                "salary_expectation"
            )

            if isinstance(salary, dict):
                if salary.get("amount") is not None:
                    salary_amount = salary.get("amount")

                if salary.get("currency"):
                    salary_currency = salary.get("currency")

                if salary.get("period"):
                    salary_period = salary.get("period")

        return {
            "skills": sorted(skills),
            "skill_count": len(skills),
            "experience_years": experience_years,
            "experience_domain": experience_domain,
            "availability": availability,
            "salary_amount": salary_amount,
            "salary_currency": salary_currency,
            "salary_period": salary_period
        }

    def evaluate_system_reliability(self, result):
        """Evaluate overall system reliability."""

        question_eval = self.evaluate_question_processing(result)
        conversation_eval = self.evaluate_conversation_flow(result)
        edge_eval = self.evaluate_edge_cases(result)

        processing_rate = question_eval["processing_success_rate"]

        if processing_rate >= 95:
            processing_status = "Excellent"
        elif processing_rate >= 80:
            processing_status = "Good"
        elif processing_rate >= 60:
            processing_status = "Moderate"
        else:
            processing_status = "Needs Improvement"

        return {
            "processing_success_rate": processing_rate,
            "processing_status": processing_status,
            "all_conversation_decisions_available":
                conversation_eval["all_decisions_available"],
            "edge_case_count": edge_eval["edge_cases_handled"]
        }

    def generate_strengths(
        self,
        question_eval,
        score_eval,
        communication_eval,
        conversation_eval,
        extraction_eval
    ):
        """Generate strengths based on actual evaluation results."""

        strengths = []

        if question_eval["processing_success_rate"] >= 95:
            strengths.append(
                "High screening question processing reliability."
            )

        if score_eval["final_screening_score"] >= 90:
            strengths.append(
                "Strong final screening score for the evaluated candidate."
            )

        if communication_eval["communication_strength"] >= 80:
            strengths.append(
                "Strong overall communication quality."
            )

        if communication_eval["confidence"] >= 80:
            strengths.append(
                "Strong confidence indicator."
            )

        if communication_eval["clarity"] >= 80:
            strengths.append(
                "Clear candidate responses."
            )

        if conversation_eval["all_decisions_available"]:
            strengths.append(
                "Conversation flow produced a decision for every response."
            )

        if extraction_eval["skill_count"] > 0:
            strengths.append(
                "Relevant candidate skills were successfully extracted."
            )

        return strengths

    def generate_limitations(self):
        """Return known limitations of the current evaluation."""

        return [
            "The evaluation is based on the available Day 32 screening scenario.",
            "The current sentiment analysis uses a rule-based baseline.",
            "Contradiction detection is currently limited and should be expanded for production use.",
            "Edge-case evaluation depends on configured thresholds and supported detection patterns.",
            "A single candidate scenario is not sufficient to establish production-level model accuracy.",
            "Human recruiter evaluation should be added for larger-scale validation."
        ]

    def build_report(self, result):
        """Build the complete evaluation report."""

        question_eval = self.evaluate_question_processing(result)
        score_eval = self.evaluate_screening_scores(result)
        communication_eval = self.evaluate_communication(result)
        conversation_eval = self.evaluate_conversation_flow(result)
        edge_eval = self.evaluate_edge_cases(result)
        extraction_eval = self.evaluate_candidate_extraction(result)
        reliability_eval = self.evaluate_system_reliability(result)

        strengths = self.generate_strengths(
            question_eval,
            score_eval,
            communication_eval,
            conversation_eval,
            extraction_eval
        )

        report = {
            "report_title": "ZecPath AI Screening Evaluation Report",
            "day": 32,
            "evaluation_type": "Final Integrated Screening System",
            "candidate_id": result.get("candidate_id"),
            "job_id": result.get("job_id"),

            "overall_evaluation": {
                "final_screening_score":
                    score_eval["final_screening_score"],
                "system_status":
                    reliability_eval["processing_status"],
                "overall_result":
                    "Successfully evaluated"
            },

            "question_processing": question_eval,

            "screening_score_evaluation": score_eval,

            "communication_evaluation": communication_eval,

            "conversation_flow_evaluation": conversation_eval,

            "edge_case_evaluation": edge_eval,

            "candidate_information_extraction": extraction_eval,

            "system_reliability": reliability_eval,

            "strengths": strengths,

            "limitations": self.generate_limitations(),

            "recommendations": [
                "Expand evaluation using multiple candidates and job roles.",
                "Compare AI screening scores with recruiter assessments.",
                "Improve multilingual and accent-aware speech processing.",
                "Expand contradiction detection across multiple candidate answers.",
                "Improve adaptive follow-up question generation.",
                "Calibrate screening scores using a larger validation dataset.",
                "Add production monitoring and evaluation metrics."
            ],

            "conclusion": (
                "The Day 32 integrated ZecPath AI screening pipeline "
                "successfully processes candidate responses, generates "
                "structured screening scores, evaluates communication "
                "indicators, performs candidate information extraction, "
                "and produces conversation decisions. The current "
                "implementation provides a strong foundation for further "
                "multi-candidate validation and production development."
            )
        }

        return report

    def save_report(self, report):
        """Save JSON and text evaluation reports."""

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        with open(
            JSON_REPORT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        text_report = self.format_text_report(report)

        with open(
            TEXT_REPORT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(text_report)

    def format_text_report(self, report):
        """Create recruiter-readable text report."""

        overall = report["overall_evaluation"]
        question = report["question_processing"]
        score = report["screening_score_evaluation"]
        communication = report["communication_evaluation"]
        conversation = report["conversation_flow_evaluation"]
        edge = report["edge_case_evaluation"]
        extraction = report["candidate_information_extraction"]
        reliability = report["system_reliability"]

        lines = []

        lines.append("=" * 75)
        lines.append("ZecPath AI SCREENING EVALUATION REPORT")
        lines.append("=" * 75)
        lines.append("")

        lines.append("EVALUATION INFORMATION")
        lines.append("-" * 75)
        lines.append(f"Day: {report['day']}")
        lines.append(f"Candidate: {report['candidate_id']}")
        lines.append(f"Job: {report['job_id']}")
        lines.append(
            f"Evaluation Type: {report['evaluation_type']}"
        )
        lines.append("")

        lines.append("OVERALL EVALUATION")
        lines.append("-" * 75)
        lines.append(
            f"Final Screening Score: "
            f"{overall['final_screening_score']}/100"
        )
        lines.append(
            f"System Status: {overall['system_status']}"
        )
        lines.append(
            f"Overall Result: {overall['overall_result']}"
        )
        lines.append("")

        lines.append("QUESTION PROCESSING")
        lines.append("-" * 75)
        lines.append(
            f"Total Questions: "
            f"{question['total_questions']}"
        )
        lines.append(
            f"Successfully Processed: "
            f"{question['successfully_processed']}"
        )
        lines.append(
            f"Processing Success Rate: "
            f"{question['processing_success_rate']}%"
        )
        lines.append("")

        lines.append("SCREENING SCORE EVALUATION")
        lines.append("-" * 75)
        lines.append(
            f"Questions With Scores: "
            f"{score['questions_with_scores']}"
        )
        lines.append(
            f"Average Question Score: "
            f"{score['average_question_score']}"
        )
        lines.append(
            f"Final Screening Score: "
            f"{score['final_screening_score']}"
        )
        lines.append("")

        lines.append("COMMUNICATION EVALUATION")
        lines.append("-" * 75)
        lines.append(
            f"Confidence: {communication['confidence']}"
        )
        lines.append(
            f"Clarity: {communication['clarity']}"
        )
        lines.append(
            f"Engagement: {communication['engagement']}"
        )
        lines.append(
            f"Consistency: {communication['consistency']}"
        )
        lines.append(
            f"Communication Strength: "
            f"{communication['communication_strength']}"
        )
        lines.append("")

        lines.append("CONVERSATION FLOW")
        lines.append("-" * 75)
        lines.append(
            f"Conversation Decisions: "
            f"{conversation['total_conversation_decisions']}"
        )
        lines.append(
            f"Actions: {', '.join(conversation['actions'])}"
        )
        lines.append(
            f"All Decisions Available: "
            f"{conversation['all_decisions_available']}"
        )
        lines.append("")

        lines.append("EDGE CASE EVALUATION")
        lines.append("-" * 75)
        lines.append(
            f"Edge Cases Handled: "
            f"{edge['edge_cases_handled']}"
        )
        lines.append(
            f"Edge Case Free Demo: "
            f"{edge['edge_case_free_demo']}"
        )
        lines.append("")

        lines.append("CANDIDATE INFORMATION EXTRACTION")
        lines.append("-" * 75)
        lines.append(
            f"Skills: "
            f"{', '.join(extraction['skills'])}"
        )
        lines.append(
            f"Skill Count: {extraction['skill_count']}"
        )
        lines.append(
            f"Experience: "
            f"{extraction['experience_years']} years"
        )
        lines.append(
            f"Experience Domain: "
            f"{extraction['experience_domain']}"
        )
        lines.append(
            f"Availability: "
            f"{extraction['availability']}"
        )
        lines.append(
            f"Salary Amount: "
            f"{extraction['salary_amount']}"
        )
        lines.append(
            f"Salary Currency: "
            f"{extraction['salary_currency']}"
        )
        lines.append(
            f"Salary Period: "
            f"{extraction['salary_period']}"
        )
        lines.append("")

        lines.append("SYSTEM RELIABILITY")
        lines.append("-" * 75)
        lines.append(
            f"Processing Success Rate: "
            f"{reliability['processing_success_rate']}%"
        )
        lines.append(
            f"Processing Status: "
            f"{reliability['processing_status']}"
        )
        lines.append(
            f"All Conversation Decisions Available: "
            f"{reliability['all_conversation_decisions_available']}"
        )
        lines.append(
            f"Edge Case Count: "
            f"{reliability['edge_case_count']}"
        )
        lines.append("")

        lines.append("STRENGTHS")
        lines.append("-" * 75)

        for strength in report["strengths"]:
            lines.append(f"- {strength}")

        lines.append("")

        lines.append("LIMITATIONS")
        lines.append("-" * 75)

        for limitation in report["limitations"]:
            lines.append(f"- {limitation}")

        lines.append("")

        lines.append("RECOMMENDATIONS")
        lines.append("-" * 75)

        for recommendation in report["recommendations"]:
            lines.append(f"- {recommendation}")

        lines.append("")

        lines.append("CONCLUSION")
        lines.append("-" * 75)
        lines.append(report["conclusion"])
        lines.append("")

        lines.append("=" * 75)
        lines.append("END OF SCREENING AI EVALUATION REPORT")
        lines.append("=" * 75)

        return "\n".join(lines)

    def run(self):
        """Run the complete evaluation."""

        print("=" * 75)
        print("DAY 32 — SCREENING AI EVALUATION")
        print("=" * 75)
        print()

        result = self.load_pipeline_result()

        report = self.build_report(result)

        self.save_report(report)

        print("Evaluation completed successfully.")
        print()
        print(
            f"Candidate: "
            f"{report['candidate_id']}"
        )
        print(
            f"Job: "
            f"{report['job_id']}"
        )
        print(
            f"Final Screening Score: "
            f"{report['overall_evaluation']['final_screening_score']}/100"
        )
        print(
            f"Processing Success Rate: "
            f"{report['question_processing']['processing_success_rate']}%"
        )
        print(
            f"Communication Strength: "
            f"{report['communication_evaluation']['communication_strength']}"
        )
        print(
            f"Edge Cases Handled: "
            f"{report['edge_case_evaluation']['edge_cases_handled']}"
        )
        print()
        print(
            f"Saved JSON report: "
            f"{JSON_REPORT_FILE}"
        )
        print(
            f"Saved text report: "
            f"{TEXT_REPORT_FILE}"
        )
        print()


if __name__ == "__main__":
    evaluator = ScreeningAIEvaluator()
    evaluator.run()