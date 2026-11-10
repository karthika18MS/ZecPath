from pathlib import Path

from .optimization_analyzer import (
    OptimizationAnalyzer
)

from .report_generator import (
    OptimizationReportGenerator
)


def main():

    print("=" * 75)

    print(
        "       ZecPath DAY 42 - "
        "OPTIMIZATION REPORT"
    )

    print("=" * 75)

    # ========================================================
    # PROJECT ROOT
    # ========================================================

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    # ========================================================
    # STABILITY REPORT
    # ========================================================

    stable_report = (
        project_root
        / "day42_optimization_stability"
        / "stable_hr_interview_ai"
        / "results"
        / "stable_hr_interview_report.json"
    )

    # ========================================================
    # OUTPUT REPORT
    # ========================================================

    output_report = (
        project_root
        / "day42_optimization_stability"
        / "optimization_report"
        / "results"
        / "optimization_report.json"
    )

    print()

    print(
        "Loading real Day 42 stability report..."
    )

    print(
        f"Source: {stable_report}"
    )

    # ========================================================
    # ANALYZE
    # ========================================================

    analyzer = OptimizationAnalyzer(
        stable_report
    )

    analysis = analyzer.analyze()

    # ========================================================
    # DISPLAY
    # ========================================================

    print()

    print(
        "Optimization analysis:"
    )

    print(
        f"Candidate       : "
        f"{analysis['candidate_id']}"
    )

    print(
        f"HR Score        : "
        f"{analysis['hr_score']}"
    )

    print(
        f"Questions       : "
        f"{analysis['question_count']}"
    )

    print(
        f"HR Validation   : "
        f"{'PASS' if analysis['hr_score_validation']['valid'] else 'FAIL'}"
    )

    print(
        f"Interview       : "
        f"{'STABLE' if analysis['interview_stability']['stable'] else 'UNSTABLE'}"
    )

    print(
        f"Errors          : "
        f"{analysis['interview_stability']['error_count']}"
    )

    print(
        f"Warnings        : "
        f"{analysis['interview_stability']['warning_count']}"
    )

    print(
        f"Question Text   : "
        f"{analysis['interview_stability']['question_text_available']}"
    )

    print(
        f"Candidate Answers: "
        f"{analysis['interview_stability']['candidate_answer_available']}"
    )

    print(
        f"Response Status : "
        f"{analysis['interview_stability']['response_status_available']}"
    )

    # ========================================================
    # GENERATE
    # ========================================================

    generator = (
        OptimizationReportGenerator(
            output_report
        )
    )

    saved_path = generator.generate(
        analysis
    )

    print()

    print("=" * 75)

    print(
        "Optimization report generated successfully."
    )

    print()

    print(
        f"Report saved to:\n{saved_path}"
    )

    print("=" * 75)


if __name__ == "__main__":
    main()