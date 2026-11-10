
"""
ZecPath Day 56 - System Performance Analysis

Reads the End-to-End AI Test Report and generates:
1. system_performance_analysis.json
2. system_performance_analysis.md

Supports both report formats:
- Latest: execution_results
- Older: stages

Separates outer process timings from internal batch timings when available.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone


# ==================================================
# 1. FILE PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_REPORT = RESULTS_DIR / "end_to_end_test_report.json"

JSON_OUTPUT = RESULTS_DIR / "system_performance_analysis.json"
MARKDOWN_OUTPUT = RESULTS_DIR / "system_performance_analysis.md"


# ==================================================
# 2. LOAD END-TO-END REPORT
# ==================================================

def load_test_report():
    """Load the saved end-to-end test report."""

    if not INPUT_REPORT.exists():
        raise FileNotFoundError(
            f"Input report not found:\n{INPUT_REPORT}\n\n"
            "Run full_system_runner.py first."
        )

    try:
        with INPUT_REPORT.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"The input report contains invalid JSON: {error}"
        ) from error

    if not isinstance(report, dict):
        raise ValueError(
            "The end-to-end report must contain a JSON object."
        )

    return report


# ==================================================
# 3. EXTRACT STAGE TIMINGS
# ==================================================

def find_timing(text, patterns):
    """Find an internal timing in captured console output, if present."""

    if not isinstance(text, str):
        return None

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            try:
                return round(float(match.group(1)), 4)
            except (TypeError, ValueError):
                continue

    return None


def extract_stage_data(report):
    """
    Extract timing data from the current or older report format.

    Latest format:
        execution_results
        execution_status

    Older format:
        stages
        status
    """

    stages = report.get("execution_results")

    if not isinstance(stages, list) or not stages:
        stages = report.get("stages", [])

    if not isinstance(stages, list) or not stages:
        raise ValueError(
            "No stage timing data found. Expected a non-empty "
            "'execution_results' or 'stages' list in the report."
        )

    extracted = []

    for stage in stages:
        if not isinstance(stage, dict):
            continue

        raw_time = stage.get("execution_time_seconds")

        if raw_time is None:
            continue

        try:
            seconds = float(raw_time)
        except (TypeError, ValueError):
            continue

        if seconds < 0:
            continue

        stage_name = stage.get("stage", "Unknown stage")

        status = stage.get(
            "execution_status",
            stage.get("status", "UNKNOWN")
        )

        stdout = stage.get("stdout", "")
        stderr = stage.get("stderr", "")
        captured_output = f"{stdout}\n{stderr}"

        stage_record = {
            "stage": str(stage_name),
            "execution_time_seconds": round(seconds, 4),
            "status": str(status).upper(),
            "demo_data_used": bool(
                stage.get("demo_data_used", False)
            ),
        }

        # Outer stage time is measured by the full-system runner.
        # Internal times are separate measurements from each script.
        if (
            "batch" in str(stage_name).lower()
            or "optimized ats" in str(stage_name).lower()
        ):
            # ----------------------------------------------
            # Extract internal batch-processing time.
            # Example: Total Batch Time: 3.367114 sec
            # ----------------------------------------------

            internal_batch_time = find_timing(
                captured_output,
                [
                    r"total\s+batch\s+time\s*[:=]\s*"
                    r"([0-9]+(?:\.[0-9]+)?)\s*(?:seconds?|s)?",
                    r"batch\s+(?:processing\s+)?time\s*[:=]\s*"
                    r"([0-9]+(?:\.[0-9]+)?)\s*(?:seconds?|s)?",
                ],
            )

            # ----------------------------------------------
            # Extract model-load time.
            # ----------------------------------------------

            model_load_time = find_timing(
                captured_output,
                [
                    r"(?:initial\s+)?model\s+load(?:ing)?\s+"
                    r"(?:time)?\s*[:=]\s*"
                    r"([0-9]+(?:\.[0-9]+)?)\s*(?:seconds?|s)?",
                    r"model\s+loaded\s+in\s+"
                    r"([0-9]+(?:\.[0-9]+)?)\s*(?:seconds?|s)",
                ],
            )

            if internal_batch_time is not None:
                stage_record[
                    "internal_batch_processing_time_seconds"
                ] = internal_batch_time

            if model_load_time is not None:
                stage_record[
                    "model_load_time_seconds"
                ] = model_load_time

            # ----------------------------------------------
            # Extract Day 17 internal total elapsed time.
            # Example: Total elapsed: 37.10 seconds
            #
            # This can include candidate preparation,
            # model loading, and semantic processing.
            # It is not equivalent to batch-processing time.
            # ----------------------------------------------

            internal_total_elapsed_time = find_timing(
                captured_output,
                [
                    r"total\s+elapsed\s*[:=]\s*"
                    r"([0-9]+(?:\.[0-9]+)?)\s*(?:seconds?|s)?",
                ],
            )

            if internal_total_elapsed_time is not None:
                stage_record[
                    "internal_total_elapsed_time_seconds"
                ] = internal_total_elapsed_time

        extracted.append(stage_record)

    if not extracted:
        raise ValueError(
            "Stage records were found, but no valid execution "
            "timings were available."
        )

    return extracted


# ==================================================
# 4. CALCULATE PERFORMANCE METRICS
# ==================================================

def calculate_performance(stage_data, report):
    """Calculate stage timings, percentages, and summary metrics."""

    measured_total = sum(
        item["execution_time_seconds"]
        for item in stage_data
    )

    summary = report.get("summary", {})

    if not isinstance(summary, dict):
        summary = {}

    raw_total = summary.get(
        "total_execution_time_seconds",
        report.get("total_execution_time_seconds")
    )

    try:
        reported_total = (
            float(raw_total) if raw_total is not None else None
        )
    except (TypeError, ValueError):
        reported_total = None

    if reported_total is not None and reported_total >= 0:
        total_execution_time = reported_total
        total_time_source = "End-to-end report summary"
    else:
        total_execution_time = measured_total
        total_time_source = "Sum of stage timings"

    # Stage percentages use the sum of individual stage times.
    # This is not necessarily the same as total workflow wall time.
    for item in stage_data:
        if measured_total > 0:
            item["time_percentage"] = round(
                item["execution_time_seconds"]
                / measured_total * 100,
                2
            )
        else:
            item["time_percentage"] = 0.0

    sorted_stages = sorted(
        stage_data,
        key=lambda item: item["execution_time_seconds"],
        reverse=True
    )

    average_time = measured_total / len(stage_data)

    slow_stages = [
        item for item in sorted_stages
        if item["execution_time_seconds"] >= 5.0
    ]

    failed_stages = [
        item["stage"]
        for item in stage_data
        if item["status"] in {"FAIL", "FAILED", "ERROR"}
    ]

    top_two_time = sum(
        item["execution_time_seconds"]
        for item in sorted_stages[:2]
    )

    top_two_percentage = (
        top_two_time / measured_total * 100
        if measured_total > 0
        else 0.0
    )

    return {
        "total_execution_time_seconds": round(
            total_execution_time, 4
        ),
        "total_time_source": total_time_source,
        "sum_of_stage_times_seconds": round(
            measured_total, 4
        ),
        "average_stage_time_seconds": round(
            average_time, 4
        ),
        "number_of_stages_measured": len(stage_data),
        "number_of_failed_stages": len(failed_stages),
        "failed_stages": failed_stages,
        "slow_stages": slow_stages,
        "slowest_stages": sorted_stages[:5],
        "slowest_two_stages_percentage": round(
            top_two_percentage, 2
        ),
        "stage_timings": stage_data,
    }


# ==================================================
# 5. GENERATE RECOMMENDATIONS
# ==================================================

def generate_recommendations(metrics):
    """Generate recommendations based on actual stage timings."""

    recommendations = []

    slowest = metrics["slowest_stages"]

    if slowest:
        slowest_stage = slowest[0]

        if slowest_stage["execution_time_seconds"] >= 5:
            recommendations.append(
                f"Investigate '{slowest_stage['stage']}', which took "
                f"{slowest_stage['execution_time_seconds']:.4f} seconds. "
                "Profile model initialization, inference, file access, "
                "and external calls before making changes."
            )

    for item in metrics["slow_stages"]:
        stage_name = item["stage"].lower()

        if "semantic" in stage_name:
            recommendations.append(
                "For semantic matching, measure model loading and "
                "inference separately. Reuse the loaded model where "
                "appropriate instead of initializing it for each task."
            )

        if "batch" in stage_name or "optimized ats" in stage_name:
            recommendations.append(
                "For the optimized ATS batch, compare process startup "
                "time with actual batch-processing time. Measure "
                "per-candidate latency separately."
            )

    if metrics["number_of_failed_stages"] > 0:
        recommendations.append(
            "Investigate failed stages and repeat the test after "
            "correcting errors."
        )

    recommendations.extend([
        "Repeat the test several times under consistent conditions "
        "and calculate minimum, average, and maximum execution times.",
        "Compare runs using equivalent inputs, hardware, model versions, "
        "and cache conditions.",
        "Measure complete workflow time separately from individual "
        "stage timings because their totals may differ.",
        "Treat these timings as performance observations, not evidence "
        "of hiring accuracy or model fairness."
    ])

    return recommendations


# ==================================================
# 6. SAVE JSON REPORT
# ==================================================

def save_json_report(metrics, recommendations, report):
    """Save the performance analysis in JSON format."""

    output = {
        "project": "ZecPath",
        "day": 56,
        "report_type": "System Performance Analysis",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "candidate_id": report.get("candidate_id"),
        "target_role": report.get("target_role"),
        "source_report": str(INPUT_REPORT),
        "performance_metrics": metrics,
        "recommendations": recommendations,
        "limitations": [
            "This report analyzes one recorded test run.",
            "Stage timings may vary due to model loading, caching, "
            "network activity, and system conditions.",
            "Stages taking five seconds or more are flagged for "
            "investigation, not automatically classified as failures.",
            "Performance timing does not establish AI assessment accuracy.",
            "Repeated controlled runs are required for reliable benchmarks."
        ]
    }

    with JSON_OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output


# ==================================================
# 7. SAVE MARKDOWN REPORT
# ==================================================

def save_markdown_report(output):
    """Generate a readable Markdown performance report."""

    metrics = output["performance_metrics"]
    stage_timings = metrics["stage_timings"]

    lines = [
        "# ZecPath Day 56 - System Performance Analysis",
        "",
        f"- Candidate ID: {output.get('candidate_id') or 'Not specified'}",
        f"- Target role: {output.get('target_role') or 'Not specified'}",
        f"- Generated UTC: {output['generated_at_utc']}",
        "",
        "## 1. Performance Summary",
        "",
        f"- Total recorded execution time: "
        f"{metrics['total_execution_time_seconds']:.4f} seconds",
        f"- Timing source: {metrics['total_time_source']}",
        f"- Sum of stage timings: "
        f"{metrics['sum_of_stage_times_seconds']:.4f} seconds",
        f"- Number of stages measured: "
        f"{metrics['number_of_stages_measured']}",
        f"- Average stage time: "
        f"{metrics['average_stage_time_seconds']:.4f} seconds",
        f"- Failed stages: {metrics['number_of_failed_stages']}",
        f"- Combined share of two slowest stages: "
        f"{metrics['slowest_two_stages_percentage']:.2f}%",
        "",
        "## 2. Stage-by-Stage Performance",
        "",
        "| Stage | Process Time (s) | Internal Batch Time (s) | "
        "Internal Total Elapsed (s) | Model Load (s) | "
        "Share of Stage Time | Status |",
        "|---|---:|---:|---:|---:|---:|---|"
    ]

    sorted_timings = sorted(
        stage_timings,
        key=lambda item: item["execution_time_seconds"],
        reverse=True
    )

    for item in sorted_timings:
        internal_time = item.get(
            "internal_batch_processing_time_seconds"
        )

        internal_total_elapsed_time = item.get(
            "internal_total_elapsed_time_seconds"
        )

        model_load_time = item.get("model_load_time_seconds")

        internal_display = (
            f"{internal_time:.4f}"
            if internal_time is not None
            else "N/A"
        )

        internal_total_elapsed_display = (
            f"{internal_total_elapsed_time:.4f}"
            if internal_total_elapsed_time is not None
            else "N/A"
        )

        model_display = (
            f"{model_load_time:.4f}"
            if model_load_time is not None
            else "N/A"
        )

        lines.append(
            f"| {item['stage']} "
            f"| {item['execution_time_seconds']:.4f} "
            f"| {internal_display} "
            f"| {internal_total_elapsed_display} "
            f"| {model_display} "
            f"| {item['time_percentage']:.2f}% "
            f"| {item['status']} |"
        )

    lines.extend([
        "",
        "## 3. Slow Stages",
        "",
        "Stages taking five seconds or more are flagged for "
        "further investigation.",
        ""
    ])

    if metrics["slow_stages"]:
        for item in metrics["slow_stages"]:
            lines.append(
                f"- **{item['stage']}**: "
                f"{item['execution_time_seconds']:.4f} seconds "
                f"({item['time_percentage']:.2f}% of stage time)."
            )
    else:
        lines.append(
            "No stage exceeded the five-second investigation threshold."
        )

    lines.extend([
        "",
        "## 4. Five Slowest Stages",
        ""
    ])

    for index, item in enumerate(
        metrics["slowest_stages"],
        start=1
    ):
        lines.append(
            f"{index}. **{item['stage']}** - "
            f"{item['execution_time_seconds']:.4f} seconds."
        )

    lines.extend([
        "",
        "## 5. Performance Recommendations",
        ""
    ])

    for recommendation in output["recommendations"]:
        lines.append(f"- {recommendation}")

    lines.extend([
        "",
        "## 6. Limitations",
        ""
    ])

    for limitation in output["limitations"]:
        lines.append(f"- {limitation}")

    lines.extend([
        "",
        "## 7. Conclusion",
        "",
        "The analyzer evaluated the recorded execution times and "
        "identified stages for further performance investigation. "
        "The measurements describe the supplied test run only. "
        "Repeated controlled tests are needed before drawing "
        "general performance conclusions.",
        ""
    ])

    with MARKDOWN_OUTPUT.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))


# ==================================================
# 8. MAIN FUNCTION
# ==================================================

def main():
    """Run the complete performance analysis."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 60)
    print("ZecPath Day 56 - System Performance Analysis")
    print("=" * 60)

    report = load_test_report()
    stage_data = extract_stage_data(report)

    metrics = calculate_performance(
        stage_data,
        report
    )

    recommendations = generate_recommendations(metrics)

    output = save_json_report(
        metrics,
        recommendations,
        report
    )

    save_markdown_report(output)

    print("\nPERFORMANCE SUMMARY")
    print("-" * 40)
    print(
        f"Total recorded time: "
        f"{metrics['total_execution_time_seconds']:.4f} seconds"
    )
    print(
        f"Sum of stage timings: "
        f"{metrics['sum_of_stage_times_seconds']:.4f} seconds"
    )
    print(
        f"Stages measured: "
        f"{metrics['number_of_stages_measured']}"
    )
    print(
        f"Average stage time: "
        f"{metrics['average_stage_time_seconds']:.4f} seconds"
    )
    print(
        f"Failed stages: "
        f"{metrics['number_of_failed_stages']}"
    )

    print("\nFIVE SLOWEST STAGES")
    print("-" * 40)

    for item in metrics["slowest_stages"]:
        print(
            f"{item['stage']}: "
            f"{item['execution_time_seconds']:.4f} seconds "
            f"({item['time_percentage']:.2f}%)"
        )

    print("\nGENERATED REPORTS")
    print("-" * 40)
    print(f"JSON report: {JSON_OUTPUT}")
    print(f"Markdown report: {MARKDOWN_OUTPUT}")
    print("\nSystem performance analysis completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as error:
        print(f"\nERROR: {error}")
        raise SystemExit(1)
