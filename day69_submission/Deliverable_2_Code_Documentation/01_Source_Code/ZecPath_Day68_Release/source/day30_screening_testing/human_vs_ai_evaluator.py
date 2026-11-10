import json
from datetime import datetime, timezone
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CURRENT_DIR / "results"


class HumanVsAIEvaluator:
    """
    Compares expected human judgments with AI screening decisions.
    """

    def compare_results(self, simulation_data):
        comparisons = []

        for case in simulation_data["test_cases"]:

            response_type_match = (
                case["expected_response_type"]
                == case["ai_response_type"]
            )

            action_match = (
                case["expected_action"]
                == case["ai_action"]
            )

            overall_match = (
                response_type_match
                and action_match
            )

            comparisons.append({
                "test_id": case["test_id"],
                "description": case["description"],
                "human_judgment": case["human_judgment"],
                "expected_response_type": (
                    case["expected_response_type"]
                ),
                "ai_response_type": (
                    case["ai_response_type"]
                ),
                "expected_action": (
                    case["expected_action"]
                ),
                "ai_action": case["ai_action"],
                "response_type_match": response_type_match,
                "action_match": action_match,
                "overall_match": overall_match,
                "ai_reason": case["ai_reason"]
            })

        total = len(comparisons)

        matched = sum(
            1
            for item in comparisons
            if item["overall_match"]
        )

        mismatched = total - matched

        accuracy = (
            round((matched / total) * 100, 2)
            if total > 0
            else 0
        )

        return {
            "report_type": "Human vs AI Screening Comparison",
            "total_cases": total,
            "matched_cases": matched,
            "mismatched_cases": mismatched,
            "agreement_percentage": accuracy,
            "comparisons": comparisons,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def build_test_report(
        self,
        simulation_data,
        comparison_data
    ):
        """
        Build the final screening system test report.
        """

        mismatches = [
            item
            for item in comparison_data["comparisons"]
            if not item["overall_match"]
        ]

        return {
            "report_type": "Screening System Test Report",
            "objective": (
                "To validate screening system performance "
                "and identify areas for optimization."
            ),
            "test_summary": {
                "total_test_cases": (
                    comparison_data["total_cases"]
                ),
                "matched_cases": (
                    comparison_data["matched_cases"]
                ),
                "mismatched_cases": (
                    comparison_data["mismatched_cases"]
                ),
                "agreement_percentage": (
                    comparison_data["agreement_percentage"]
                )
            },
            "test_categories": [
                "Valid responses",
                "Vague responses",
                "No response / silence",
                "Confused responses",
                "Off-topic responses",
                "Repeated answers",
                "Salary responses",
                "Availability responses",
                "Skills responses"
            ],
            "human_vs_ai_comparison": (
                comparison_data["comparisons"]
            ),
            "identified_issues": mismatches,
            "optimization_required": (
                len(mismatches) > 0
            ),
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def save_json(
        self,
        data,
        filename
    ):
        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = RESULTS_DIR / filename

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4
            )

        return output_path

    def save_text_report(self, report):
        """
        Create a recruiter/developer-friendly text report.
        """

        lines = []

        lines.append("=" * 60)
        lines.append("SCREENING SYSTEM TEST REPORT")
        lines.append("=" * 60)

        lines.append("")
        lines.append("OBJECTIVE")
        lines.append("-" * 60)
        lines.append(report["objective"])

        summary = report["test_summary"]

        lines.append("")
        lines.append("TEST SUMMARY")
        lines.append("-" * 60)
        lines.append(
            f"Total test cases       : "
            f"{summary['total_test_cases']}"
        )
        lines.append(
            f"Matched cases          : "
            f"{summary['matched_cases']}"
        )
        lines.append(
            f"Mismatched cases      : "
            f"{summary['mismatched_cases']}"
        )
        lines.append(
            f"Human-AI agreement     : "
            f"{summary['agreement_percentage']}%"
        )

        lines.append("")
        lines.append("TEST RESULTS")
        lines.append("-" * 60)

        for item in report["human_vs_ai_comparison"]:

            status = (
                "PASS"
                if item["overall_match"]
                else "REVIEW"
            )

            lines.append(
                f"{item['test_id']} - "
                f"{item['description']} : {status}"
            )

            lines.append(
                f"  Human judgment : "
                f"{item['human_judgment']}"
            )

            lines.append(
                f"  Expected action : "
                f"{item['expected_action']}"
            )

            lines.append(
                f"  AI action       : "
                f"{item['ai_action']}"
            )

        lines.append("")
        lines.append("IDENTIFIED ISSUES")
        lines.append("-" * 60)

        if report["identified_issues"]:
            for issue in report["identified_issues"]:
                lines.append(
                    f"- {issue['test_id']}: "
                    f"{issue['description']}"
                )
        else:
            lines.append(
                "No mismatched cases identified."
            )

        lines.append("")
        lines.append("CONCLUSION")
        lines.append("-" * 60)

        if report["optimization_required"]:
            lines.append(
                "The screening system requires optimization "
                "for the identified mismatched cases."
            )
        else:
            lines.append(
                "The tested screening scenarios matched "
                "the expected human judgments."
            )

        lines.append("")
        lines.append(
            f"Report generated at: "
            f"{report['created_at']}"
        )

        output_path = RESULTS_DIR / "screening_test_report.txt"

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write("\n".join(lines))

        return output_path


if __name__ == "__main__":

    simulation_path = (
        RESULTS_DIR /
        "screening_simulation_results.json"
    )

    if not simulation_path.exists():
        print(
            "Simulation results not found."
        )
        print(
            "Run simulated_screening_calls.py first."
        )
        raise SystemExit(1)

    with open(
        simulation_path,
        "r",
        encoding="utf-8"
    ) as file:
        simulation_data = json.load(file)

    evaluator = HumanVsAIEvaluator()

    comparison = evaluator.compare_results(
        simulation_data
    )

    report = evaluator.build_test_report(
        simulation_data,
        comparison
    )

    comparison_path = evaluator.save_json(
        comparison,
        "human_vs_ai_comparison.json"
    )

    report_path = evaluator.save_json(
        report,
        "screening_test_report.json"
    )

    text_path = evaluator.save_text_report(
        report
    )

    print("\nHuman vs AI Comparison:")
    print(json.dumps(comparison, indent=4))

    print("\nScreening System Test Report:")
    print(json.dumps(report, indent=4))

    print(f"\nComparison saved to: {comparison_path}")
    print(f"Report saved to: {report_path}")
    print(f"Text report saved to: {text_path}")