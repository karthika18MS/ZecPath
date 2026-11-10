
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# ZecPath Day 56 - Full System Simulation
# Candidate: candidate_006
# Deliverable 1: End-to-End AI Test Report
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DAY56_DIR = Path(__file__).resolve().parent
RESULTS_DIR = DAY56_DIR / "results"

CANDIDATE_ID = "candidate_006"
PYTHON = sys.executable

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

JSON_REPORT = RESULTS_DIR / "end_to_end_test_report.json"
MD_REPORT = RESULTS_DIR / "end_to_end_test_report.md"


# ============================================================
# JSON UTILITIES
# ============================================================

def read_json(path):
    """Read JSON safely."""
    try:
        with Path(path).open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def find_number(data, field_names):
    """Find a numeric score in a nested JSON structure."""
    if isinstance(data, dict):
        for field in field_names:
            value = data.get(field)

            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and 0 <= value <= 100
            ):
                return round(float(value), 2)

        for value in data.values():
            result = find_number(value, field_names)
            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_number(item, field_names)
            if result is not None:
                return result

    return None


def find_value(data, field_names):
    """Find a non-empty field value in nested JSON."""
    if isinstance(data, dict):
        for field in field_names:
            if field in data and data[field] not in (None, ""):
                return data[field]

        for value in data.values():
            result = find_value(value, field_names)
            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_value(item, field_names)
            if result is not None:
                return result

    return None


def relative_path(path):
    """Return a project-relative path where possible."""
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


# ============================================================
# COMMAND EXECUTION
# ============================================================

def run_command(stage_name, command, demo_data=False):
    """Run a stage and record its real process status."""
    print("\n" + "=" * 68)
    print(f"STAGE: {stage_name}")
    print("COMMAND:", " ".join(str(item) for item in command))
    print("=" * 68)

    started = time.perf_counter()

    try:
        process = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
            env={
                **os.environ,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1"
            }
        )

        elapsed = round(time.perf_counter() - started, 4)

        if process.stdout:
            print(process.stdout)

        if process.stderr:
            print("STDERR:")
            print(process.stderr)

        return {
            "stage": stage_name,
            "command": " ".join(str(item) for item in command),
            "execution_status": (
                "PASS" if process.returncode == 0 else "FAIL"
            ),
            "return_code": process.returncode,
            "execution_time_seconds": elapsed,
            "demo_data_used": demo_data,
            "stdout": process.stdout[-5000:],
            "stderr": process.stderr[-5000:]
        }

    except subprocess.TimeoutExpired as error:
        elapsed = round(time.perf_counter() - started, 4)

        return {
            "stage": stage_name,
            "command": " ".join(str(item) for item in command),
            "execution_status": "FAIL",
            "return_code": None,
            "execution_time_seconds": elapsed,
            "demo_data_used": demo_data,
            "stdout": str(error.stdout or "")[-5000:],
            "stderr": "Stage exceeded the 600-second timeout."
        }

    except OSError as error:
        elapsed = round(time.perf_counter() - started, 4)

        return {
            "stage": stage_name,
            "command": " ".join(str(item) for item in command),
            "execution_status": "FAIL",
            "return_code": None,
            "execution_time_seconds": elapsed,
            "demo_data_used": demo_data,
            "stdout": "",
            "stderr": str(error)
        }


# ============================================================
# OUTPUT VALIDATION
# ============================================================

def check_json_output(name, path):
    """Check whether a JSON output exists and is readable."""
    path = Path(path)

    result = {
        "check": name,
        "path": relative_path(path)
    }

    if not path.is_file():
        result.update({
            "status": "FAIL",
            "details": "Expected output file does not exist."
        })
        return result

    data = read_json(path)

    if not isinstance(data, (dict, list)):
        result.update({
            "status": "FAIL",
            "details": (
                "File is not valid JSON or has an unexpected structure."
            )
        })
        return result

    result.update({
        "status": "PASS",
        "details": "JSON file exists and is readable."
    })

    return result


def check_numeric_score(name, path, field_names):
    """Validate that an output contains a numeric score from 0 to 100."""
    path = Path(path)
    data = read_json(path) if path.is_file() else None

    score = find_number(data, field_names)

    if score is None:
        return {
            "check": name,
            "path": relative_path(path),
            "status": "FAIL",
            "details": (
                "No numeric score from 0 to 100 was found "
                "under the expected score fields."
            ),
            "score": None
        }

    return {
        "check": name,
        "path": relative_path(path),
        "status": "PASS",
        "details": f"Numeric score verified: {score}",
        "score": score
    }


def check_candidate_identity(name, path, expected_id=CANDIDATE_ID):
    """Verify that an assessment output belongs to the target candidate."""
    path = Path(path)
    data = read_json(path) if path.is_file() else None

    actual_id = find_value(
        data,
        ["candidate_id", "candidateId"]
    )

    status = "PASS" if actual_id == expected_id else "FAIL"

    return {
        "assessment": name,
        "path": relative_path(path),
        "expected_candidate_id": expected_id,
        "actual_candidate_id": actual_id,
        "status": status
    }


# ============================================================
# MAIN TEST
# ============================================================

def main():
    total_started = time.perf_counter()

    print("=" * 68)
    print("ZECPATH DAY 56 - CANDIDATE 006 END-TO-END TEST")
    print("=" * 68)

    # --------------------------------------------------------
    # 1. Verify candidate configuration and input files
    # --------------------------------------------------------

    test_cases_path = ROOT / "day17_testing" / "test_cases.json"
    test_cases = read_json(test_cases_path)

    if not isinstance(test_cases, dict):
        raise SystemExit(
            f"Could not read candidate test configuration: "
            f"{test_cases_path}"
        )

    if CANDIDATE_ID not in test_cases:
        raise SystemExit(
            f"{CANDIDATE_ID} was not found in test_cases.json."
        )

    candidate_case = test_cases[CANDIDATE_ID]
    target_role = candidate_case.get("target_role")

    if not target_role:
        raise SystemExit("Candidate target_role is missing.")

    resume_path = (
        ROOT / "day17_testing" / "resumes"
        / f"{CANDIDATE_ID}.docx"
    )

    jd_filename = candidate_case.get("job_description")

    if not jd_filename:
        raise SystemExit("Candidate job_description is missing.")

    jd_path = (
        ROOT / "day17_testing" / "job_descriptions"
        / str(jd_filename)
    )

    input_checks = [
        {
            "check": "Candidate resume",
            "path": relative_path(resume_path),
            "status": "PASS" if resume_path.is_file() else "FAIL",
            "details": (
                "Resume exists."
                if resume_path.is_file()
                else "Resume file is missing."
            )
        },
        {
            "check": "Job description",
            "path": relative_path(jd_path),
            "status": "PASS" if jd_path.is_file() else "FAIL",
            "details": (
                "Job description exists."
                if jd_path.is_file()
                else "Job description file is missing."
            )
        }
    ]

    if any(item["status"] == "FAIL" for item in input_checks):
        raise SystemExit(
            "Input validation failed. Check the resume and job description."
        )

    print(f"Candidate ID: {CANDIDATE_ID}")
    print(f"Target role: {target_role}")
    print("Input validation: PASS")

    # --------------------------------------------------------
    # 2. Run the Day 17 assessment modules
    # Semantic matching uses the optimized batch module.
    # --------------------------------------------------------

    execution_results = []

    day17_stages = [
        (
            "Resume extraction and input validation",
            "day17_testing.run_day17_test"
        ),
        (
            "Skill matching",
            "day17_testing.day17_skill_matching"
        ),
        (
            "Optimized semantic matching batch",
            "day17_testing.day17_semantic_batch"
        ),
        (
            "Experience matching",
            "day17_testing.day17_experience"
        ),
        (
            "Education matching",
            "day17_testing.day17_education"
        ),
        (
            "Final ATS scoring",
            "day17_testing.day17_final_scoring"
        )
    ]

    for stage_name, module_name in day17_stages:
        record = run_command(
            stage_name,
            [
                PYTHON,
                "-m",
                module_name,
                CANDIDATE_ID,
                target_role
            ]
        )

        execution_results.append(record)

        if record["execution_status"] == "FAIL":
            print(
                f"\nDay 17 stopped because '{stage_name}' failed."
            )
            break

    day17_failed = any(
        item["execution_status"] == "FAIL"
        for item in execution_results
    )

    # --------------------------------------------------------
    # 3. Run Day 18 optimized ATS batch
    # This runner processes its configured candidates.
    # --------------------------------------------------------

    if not day17_failed:
        execution_results.append(
            run_command(
                "Day 18 optimized ATS batch",
                [
                    PYTHON,
                    "-m",
                    "day18_optimization.day18_batch_runner"
                ]
            )
        )
    else:
        print("Day 18 batch skipped because a Day 17 stage failed.")

    # --------------------------------------------------------
    # 4. Run eligibility engine
    # --------------------------------------------------------

    execution_results.append(
        run_command(
            "Day 21 eligibility engine",
            [
                PYTHON,
                "-m",
                "eligibility_engine.run_eligibility"
            ]
        )
    )

    # --------------------------------------------------------
    # 5. Run HR demonstration assessment
    # --------------------------------------------------------

    execution_results.append(
        run_command(
            "Day 37 HR interview scoring - demonstration data",
            [
                PYTHON,
                "-m",
                "day37_hr_interview_scoring.hr_interview_scoring_engine"
            ],
            demo_data=True
        )
    )

    # --------------------------------------------------------
    # 6. Run aptitude demonstration assessments
    # --------------------------------------------------------

    execution_results.append(
        run_command(
            "Day 38 logical reasoning - demonstration data",
            [
                PYTHON,
                str(
                    ROOT / "day38_aptitude_logic"
                    / "logical_reasoning_scorer.py"
                )
            ],
            demo_data=True
        )
    )

    execution_results.append(
        run_command(
            "Day 38 scenario evaluation - demonstration data",
            [
                PYTHON,
                str(
                    ROOT / "day38_aptitude_logic"
                    / "scenario_evaluation.py"
                )
            ],
            demo_data=True
        )
    )

    # --------------------------------------------------------
    # 7. Run cross-round scoring
    # --------------------------------------------------------

    execution_results.append(
        run_command(
            "Day 41 cross-round scoring",
            [
                PYTHON,
                "-m",
                "day41_cross_round_scoring.run_cross_round"
            ]
        )
    )

    # --------------------------------------------------------
    # 8. Define actual output paths
    # --------------------------------------------------------

    day17_candidate_dir = (
        ROOT / "day17_testing" / "results" / CANDIDATE_ID
    )

    day18_candidate_dir = (
        ROOT / "day18_optimization" / "results" / CANDIDATE_ID
    )

    eligibility_candidate_dir = (
        ROOT / "eligibility_engine" / "results" / CANDIDATE_ID
    )

    hr_path = (
        ROOT / "day37_hr_interview_scoring" / "results"
        / "hr_interview_score.json"
    )

    logical_path = (
        ROOT / "day38_aptitude_logic" / "results"
        / "logical_reasoning_results.json"
    )

    scenario_path = (
        ROOT / "day38_aptitude_logic" / "results"
        / "scenario_evaluation_results.json"
    )

    cross_candidate_dir = (
        ROOT / "day41_cross_round_scoring" / "results"
        / CANDIDATE_ID
    )

    semantic_path = (
        day17_candidate_dir / "day17_semantic_similarity.json"
    )

    # --------------------------------------------------------
    # 9. Validate JSON output files
    # --------------------------------------------------------

    output_paths = [
        ("Day 17 semantic matching output", semantic_path),
        (
            "Day 17 final ATS output",
            day17_candidate_dir / "day17_final_ats_score.json"
        ),
        (
            "Day 18 optimized ATS output",
            day18_candidate_dir / "day18_optimized_ats_score.json"
        ),
        (
            "Eligibility output",
            eligibility_candidate_dir / "eligibility_result.json"
        ),
        ("HR interview output", hr_path),
        ("Logical reasoning output", logical_path),
        ("Scenario evaluation output", scenario_path),
        (
            "Cross-round output",
            cross_candidate_dir / "cross_round_score.json"
        )
    ]

    output_checks = [
        check_json_output(name, path)
        for name, path in output_paths
    ]

    # --------------------------------------------------------
    # 10. Validate assessment scores
    # --------------------------------------------------------

    semantic_fields = [
        "semantic_similarity_score",
        "semantic_similarity",
        "similarity_score",
        "score"
    ]

    score_checks = [
        check_numeric_score(
            "Day 17 semantic similarity score",
            semantic_path,
            semantic_fields
        ),
        check_numeric_score(
            "Day 17 final ATS score",
            day17_candidate_dir / "day17_final_ats_score.json",
            ["final_ats_score", "ats_score"]
        ),
        check_numeric_score(
            "Day 18 optimized ATS score",
            day18_candidate_dir / "day18_optimized_ats_score.json",
            ["final_ats_score", "optimized_ats_score", "ats_score"]
        ),
        check_numeric_score(
            "HR interview score",
            hr_path,
            ["final_hr_interview_score", "hr_interview_score", "hr_score"]
        ),
        check_numeric_score(
            "Logical reasoning score",
            logical_path,
            ["logical_reasoning_score"]
        ),
        check_numeric_score(
            "Scenario evaluation score",
            scenario_path,
            ["scenario_evaluation_score"]
        ),
        check_numeric_score(
            "Cross-round score",
            cross_candidate_dir / "cross_round_score.json",
            ["cross_round_score", "final_score"]
        )
    ]

    # --------------------------------------------------------
    # 11. Validate candidate identity
    # --------------------------------------------------------

    identity_checks = [
        check_candidate_identity(
            "Day 17 semantic matching",
            semantic_path
        ),
        check_candidate_identity(
            "HR interview",
            hr_path
        ),
        check_candidate_identity(
            "Logical reasoning",
            logical_path
        ),
        check_candidate_identity(
            "Scenario evaluation",
            scenario_path
        )
    ]

    # --------------------------------------------------------
    # 12. Extract scores and eligibility result
    # --------------------------------------------------------

    score_sources = {
        "Semantic similarity": (
            semantic_path,
            semantic_fields
        ),
        "ATS": (
            day17_candidate_dir / "day17_final_ats_score.json",
            ["final_ats_score", "ats_score"]
        ),
        "Optimized ATS": (
            day18_candidate_dir / "day18_optimized_ats_score.json",
            ["final_ats_score", "optimized_ats_score", "ats_score"]
        ),
        "HR interview": (
            hr_path,
            ["final_hr_interview_score", "hr_interview_score", "hr_score"]
        ),
        "Logical reasoning": (
            logical_path,
            ["logical_reasoning_score"]
        ),
        "Scenario evaluation": (
            scenario_path,
            ["scenario_evaluation_score"]
        ),
        "Cross-round": (
            cross_candidate_dir / "cross_round_score.json",
            ["cross_round_score", "final_score"]
        )
    }

    scores = {}

    for name, (path, fields) in score_sources.items():
        data = read_json(path) if path.is_file() else None
        scores[name] = find_number(data, fields)

    eligibility_path = (
        eligibility_candidate_dir / "eligibility_result.json"
    )

    eligibility_data = read_json(eligibility_path)

    eligibility_decision = find_value(
        eligibility_data,
        ["status", "eligibility_status", "decision"]
    )

    cross_data = read_json(
        cross_candidate_dir / "cross_round_score.json"
    )

    cross_status = find_value(
        cross_data,
        ["status", "candidate_status"]
    )

    # --------------------------------------------------------
    # 13. Count actual test results
    # --------------------------------------------------------

    elapsed_total = round(time.perf_counter() - total_started, 4)

    passed_stages = [
        item for item in execution_results
        if item["execution_status"] == "PASS"
    ]

    failed_stages = [
        item for item in execution_results
        if item["execution_status"] == "FAIL"
    ]

    failed_outputs = [
        item for item in output_checks
        if item["status"] == "FAIL"
    ]

    failed_scores = [
        item for item in score_checks
        if item["status"] == "FAIL"
    ]

    failed_identity_checks = [
        item for item in identity_checks
        if item["status"] == "FAIL"
    ]

    if (
        failed_stages
        or failed_outputs
        or failed_scores
        or failed_identity_checks
    ):
        overall_status = "FAIL"
    elif (
        any(
            item["execution_status"] != "PASS"
            for item in execution_results
        )
        or cross_status != "Complete"
    ):
        overall_status = "REVIEW_REQUIRED"
    else:
        overall_status = "PASS_WITH_DEMO_DATA"

    # --------------------------------------------------------
    # 14. Construct final JSON report
    # --------------------------------------------------------

    report = {
        "report_title": (
            "ZecPath Day 56 - End-to-End AI Test Report"
        ),
        "candidate_id": CANDIDATE_ID,
        "target_role": target_role,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "test_scope": (
            "Candidate-specific pipeline execution, output validation, "
            "and demonstration assessment scoring"
        ),
        "full_pipeline_execution_attempted": True,
        "human_vs_ai_comparison_performed": False,
        "demo_data_used": True,
        "input_validation": input_checks,
        "execution_results": execution_results,
        "output_validation": output_checks,
        "score_validation": score_checks,
        "candidate_identity_checks": identity_checks,
        "scores_found": scores,
        "eligibility_decision": eligibility_decision,
        "cross_round_status": cross_status,
        "summary": {
            "stages_attempted": len(execution_results),
            "stages_passed": len(passed_stages),
            "stages_failed": len(failed_stages),
            "output_checks_passed": sum(
                item["status"] == "PASS"
                for item in output_checks
            ),
            "output_checks_failed": len(failed_outputs),
            "score_checks_passed": sum(
                item["status"] == "PASS"
                for item in score_checks
            ),
            "score_checks_failed": len(failed_scores),
            "identity_checks_passed": sum(
                item["status"] == "PASS"
                for item in identity_checks
            ),
            "identity_checks_failed": len(failed_identity_checks),
            "total_execution_time_seconds": elapsed_total
        },
        "limitations": [
            "The Day 18 batch and eligibility runners process multiple candidates.",
            "HR, logical reasoning, and scenario assessment use demonstration inputs.",
            "A valid output does not by itself prove that the scoring result is accurate.",
            "Human-versus-AI comparison has not been performed.",
            "The optimized semantic batch processes configured candidates in one run; its stage time is the batch process duration.",
            "Model loading and network activity may affect execution time.",
            "Final hiring decisions require appropriate human review."
        ]
    }

    # Save JSON report
    with JSON_REPORT.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    # --------------------------------------------------------
    # 15. Generate readable Markdown report
    # --------------------------------------------------------

    lines = [
        "# ZecPath Day 56 - End-to-End AI Test Report",
        "",
        f"- Candidate ID: `{CANDIDATE_ID}`",
        f"- Target role: {target_role}",
        f"- Generated UTC: {report['generated_at_utc']}",
        f"- Overall status: **{overall_status}**",
        "- Demonstration assessment data used: **Yes**",
        "- AI versus human comparison: **Not performed**",
        "",
        "## 1. Test summary",
        "",
        f"- Stages attempted: {len(execution_results)}",
        f"- Stages passed: {len(passed_stages)}",
        f"- Stages failed: {len(failed_stages)}",
        f"- Output checks passed: {len(output_checks) - len(failed_outputs)}",
        f"- Output checks failed: {len(failed_outputs)}",
        f"- Score checks passed: {len(score_checks) - len(failed_scores)}",
        f"- Score checks failed: {len(failed_scores)}",
        f"- Total execution time: {elapsed_total} seconds",
        "",
        "## 2. Stage execution results",
        "",
        "| Stage | Status | Time (seconds) | Demo data |",
        "|---|---|---:|---|"
    ]

    for item in execution_results:
        lines.append(
            f"| {item['stage']} "
            f"| {item['execution_status']} "
            f"| {item['execution_time_seconds']} "
            f"| {'Yes' if item['demo_data_used'] else 'No'} |"
        )

    lines.extend([
        "",
        "## 3. Output file validation",
        "",
        "| Check | Status | Details |",
        "|---|---|---|"
    ])

    for item in output_checks:
        lines.append(
            f"| {item['check']} | {item['status']} "
            f"| {item['details']} |"
        )

    lines.extend([
        "",
        "## 4. Score validation",
        "",
        "| Assessment | Status | Score |",
        "|---|---|---:|"
    ])

    for item in score_checks:
        score = item.get("score")
        display_score = f"{score:.2f}" if score is not None else "Not found"

        lines.append(
            f"| {item['check']} | {item['status']} "
            f"| {display_score} |"
        )

    lines.extend([
        "",
        "## 5. Candidate assessment scores",
        "",
        "| Assessment | Score |",
        "|---|---:|"
    ])

    for name, score in scores.items():
        display_score = f"{score:.2f}" if score is not None else "Not found"
        lines.append(f"| {name} | {display_score} |")

    lines.extend([
        "",
        f"- Eligibility decision: {eligibility_decision or 'Not found'}",
        f"- Cross-round status: {cross_status or 'Not found'}",
        "",
        "## 6. Candidate identity checks",
        "",
        "| Assessment | Expected ID | Actual ID | Status |",
        "|---|---|---|---|"
    ])

    for item in identity_checks:
        actual = item["actual_candidate_id"] or "Not found"

        lines.append(
            f"| {item['assessment']} "
            f"| {item['expected_candidate_id']} "
            f"| {actual} | {item['status']} |"
        )

    lines.extend([
        "",
        "## 7. Limitations",
        ""
    ])

    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")

    lines.extend([
        "",
        "## 8. Conclusion",
        "",
        f"The recorded test status is **{overall_status}**. "
        "Review every failed stage and validation check before claiming "
        "that the entire pipeline passed. Demonstration assessments "
        "support integration testing but do not establish real-world "
        "hiring accuracy.",
        ""
    ])

    MD_REPORT.write_text("\n".join(lines), encoding="utf-8")

    # --------------------------------------------------------
    # 16. Final terminal summary
    # --------------------------------------------------------

    print("\n" + "=" * 68)
    print("DAY 56 - END-TO-END TEST SUMMARY")
    print("=" * 68)
    print(f"Candidate: {CANDIDATE_ID}")
    print(f"Target role: {target_role}")
    print(f"Overall status: {overall_status}")
    print(f"Stages attempted: {len(execution_results)}")
    print(f"Stages passed: {len(passed_stages)}")
    print(f"Stages failed: {len(failed_stages)}")
    print(f"Output checks failed: {len(failed_outputs)}")
    print(f"Score checks failed: {len(failed_scores)}")
    print(f"Identity checks failed: {len(failed_identity_checks)}")
    print(f"Cross-round status: {cross_status}")
    print(f"Total execution time: {elapsed_total} seconds")
    print()
    print(f"JSON report: {JSON_REPORT}")
    print(f"Markdown report: {MD_REPORT}")
    print("=" * 68)


if __name__ == "__main__":
    main()
