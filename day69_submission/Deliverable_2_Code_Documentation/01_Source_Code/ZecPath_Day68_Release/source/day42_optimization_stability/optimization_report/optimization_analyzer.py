import json
from pathlib import Path


class OptimizationAnalyzer:

    def __init__(
        self,
        stable_report_path
    ):

        self.stable_report_path = Path(
            stable_report_path
        )

    # =========================================================
    # LOAD STABILITY REPORT
    # =========================================================

    def load_report(self):

        if not self.stable_report_path.exists():

            raise FileNotFoundError(
                f"Stability report not found: "
                f"{self.stable_report_path}"
            )

        with open(
            self.stable_report_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # =========================================================
    # ANALYZE REPORT
    # =========================================================

    def analyze(self):

        report = self.load_report()

        hr_validation = report.get(
            "hr_score_validation",
            {}
        )

        stability = report.get(
            "interview_stability",
            {}
        )

        errors = stability.get(
            "errors",
            []
        )

        warnings = stability.get(
            "warnings",
            []
        )

        duplicate_questions = stability.get(
            "duplicate_questions",
            []
        )

        question_validation = stability.get(
            "question_validation",
            {}
        )

        total_questions = stability.get(
            "total_questions",
            0
        )

        question_text_available = (
            question_validation.get(
                "question_text_available",
                0
            )
        )

        candidate_answer_available = (
            question_validation.get(
                "candidate_answer_available",
                0
            )
        )

        response_status_available = (
            question_validation.get(
                "response_status_available",
                0
            )
        )

        # =====================================================
        # BASIC REPORT
        # =====================================================

        analysis = {

            "system":
                "ZecPath Day 42 Optimization Report",

            "candidate_id":
                report.get(
                    "candidate_id"
                ),

            "job_id":
                report.get(
                    "job_id"
                ),

            "hr_score":
                hr_validation.get(
                    "final_hr_interview_score"
                ),

            "question_count":
                hr_validation.get(
                    "question_count"
                ),

            "hr_score_validation": {

                "valid":
                    hr_validation.get(
                        "valid",
                        False
                    ),

                "error_count":
                    len(
                        hr_validation.get(
                            "errors",
                            []
                        )
                    )
            },

            "interview_stability": {

                "stable":
                    stability.get(
                        "stable",
                        False
                    ),

                "total_questions":
                    total_questions,

                "duplicate_question_count":
                    len(
                        duplicate_questions
                    ),

                "error_count":
                    len(errors),

                "warning_count":
                    len(warnings),

                "question_text_available":
                    question_text_available,

                "candidate_answer_available":
                    candidate_answer_available,

                "response_status_available":
                    response_status_available
            },

            "optimization_findings": [],

            "recommended_improvements": [],

            "overall_status":
                report.get(
                    "overall_status",
                    "UNKNOWN"
                )
        }

        # =====================================================
        # HR SCORING
        # =====================================================

        if hr_validation.get("valid"):

            analysis[
                "optimization_findings"
            ].append(
                "HR scoring structure is valid."
            )

        else:

            analysis[
                "optimization_findings"
            ].append(
                "HR scoring validation requires review."
            )

            analysis[
                "recommended_improvements"
            ].append(
                "Review invalid HR scoring fields."
            )

        # =====================================================
        # INTERVIEW STABILITY
        # =====================================================

        if stability.get("stable"):

            analysis[
                "optimization_findings"
            ].append(
                "Interview flow passed stability validation."
            )

        else:

            analysis[
                "optimization_findings"
            ].append(
                "Interview flow contains stability errors."
            )

            analysis[
                "recommended_improvements"
            ].append(
                "Review interview flow errors."
            )

        # =====================================================
        # DUPLICATE QUESTIONS
        # =====================================================

        if duplicate_questions:

            analysis[
                "optimization_findings"
            ].append(
                "Duplicate question IDs were detected."
            )

            analysis[
                "recommended_improvements"
            ].append(
                "Improve duplicate-question prevention."
            )

        else:

            analysis[
                "optimization_findings"
            ].append(
                "No duplicate question IDs detected."
            )

        # =====================================================
        # ERRORS
        # =====================================================

        if errors:

            analysis[
                "optimization_findings"
            ].append(
                f"{len(errors)} "
                f"stability error(s) detected."
            )

        else:

            analysis[
                "optimization_findings"
            ].append(
                "No interview stability errors detected."
            )

        # =====================================================
        # WARNINGS
        # =====================================================

        if warnings:

            analysis[
                "optimization_findings"
            ].append(
                f"{len(warnings)} "
                f"warning(s) detected."
            )

            analysis[
                "recommended_improvements"
            ].append(
                "Review the remaining non-blocking "
                "interview warnings."
            )

        else:

            analysis[
                "optimization_findings"
            ].append(
                "No warnings detected."
            )

        # =====================================================
        # QUESTION CONTENT
        # =====================================================

        if (
            total_questions > 0
            and question_text_available
                == total_questions
            and candidate_answer_available
                == total_questions
            and response_status_available
                == total_questions
        ):

            analysis[
                "optimization_findings"
            ].append(
                "Question text, candidate answers, "
                "and response status are available "
                "for all questions."
            )

            analysis[
                "recommended_improvements"
            ].append(
                "Question-level content validation "
                "is complete for the current "
                "sample dataset."
            )

        else:

            analysis[
                "optimization_findings"
            ].append(
                "Some question-level interview "
                "content is incomplete."
            )

            analysis[
                "recommended_improvements"
            ].append(
                "Ensure every Day 37 question contains "
                "question_text, candidate_answer, "
                "and valid interview status data."
            )

        # =====================================================
        # GENERAL STABILITY RECOMMENDATION
        # =====================================================

        if (
            analysis["overall_status"]
            == "STABLE"
            and len(errors) == 0
            and len(warnings) == 0
        ):

            analysis[
                "recommended_improvements"
            ].append(
                "Continue testing additional interview "
                "sessions while preserving the current "
                "stability validation rules."
            )

        return analysis