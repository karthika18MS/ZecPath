
import json
from pathlib import Path
import math


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "06_end_to_end_simulation"
    / "outputs"
    / "cross_round_scoring_results.json"
)

OUTPUT_DIR = PROJECT_ROOT / "day65_final_enhancements" / "09_final_outputs"
REPORT_FILE = OUTPUT_DIR / "unified_score_consistency_report.json"

TOLERANCE = 0.01


def calculate_expected_score(candidate, weights):
    """Independently calculate the weighted normalized score."""

    round_details = candidate.get("round_details", {})

    weighted_total = 0.0
    available_weight = 0.0
    available_rounds = []

    for round_name, weight in weights.items():
        round_data = round_details.get(round_name, {})
        score = round_data.get("score")

        if score is None:
            continue

        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(score)
            or not 0 <= score <= 100
        ):
            raise ValueError(
                f"Invalid score for {round_name}: {score}"
            )

        weighted_total += score * weight
        available_weight += weight
        available_rounds.append(round_name)

    if available_weight == 0:
        return None, 0.0, available_rounds

    expected_score = round(
        weighted_total / available_weight, 2
    )

    return expected_score, available_weight, available_rounds


def main():
    print("=" * 70)
    print("ZECPath DAY 65 - UNIFIED SCORE CONSISTENCY TEST")
    print("=" * 70)

    if not INPUT_FILE.is_file():
        print("ERROR: Cross-round scoring output not found.")
        return

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    weights = data.get("weights", {})
    candidates = data.get("candidate_results", [])

    if not weights or not candidates:
        print("ERROR: Missing weights or candidate records.")
        return

    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9):
        print("ERROR: Scoring weights do not total 1.0.")
        return

    results = []

    for candidate in candidates:
        candidate_id = candidate.get("candidate_id")
        actual_score = candidate.get("unified_score")

        try:
            expected_score, available_weight, rounds = (
                calculate_expected_score(candidate, weights)
            )

            if expected_score is None:
                matched = actual_score is None
                difference = None
            elif (
                isinstance(actual_score, bool)
                or not isinstance(actual_score, (int, float))
                or not math.isfinite(actual_score)
            ):
                matched = False
                difference = None
            else:
                difference = round(
                    abs(actual_score - expected_score), 4
                )
                matched = difference <= TOLERANCE

            results.append({
                "candidate_id": candidate_id,
                "actual_score": actual_score,
                "expected_score": expected_score,
                "score_difference": difference,
                "available_weight": round(available_weight, 4),
                "available_rounds": rounds,
                "status": "PASS" if matched else "FAIL"
            })

        except (ValueError, TypeError) as error:
            results.append({
                "candidate_id": candidate_id,
                "actual_score": actual_score,
                "expected_score": None,
                "score_difference": None,
                "available_weight": None,
                "available_rounds": [],
                "status": "ERROR",
                "error": str(error)
            })

    passed = sum(r["status"] == "PASS" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)
    errors = sum(r["status"] == "ERROR" for r in results)

    print("\nCANDIDATE SCORE COMPARISON")
    print("-" * 70)

    for result in results:
        print(
            f'{result["candidate_id"]}: '
            f'Actual={result["actual_score"]}, '
            f'Expected={result["expected_score"]}, '
            f'Status={result["status"]}'
        )

    report = {
        "module": "ZecPath Day 65 Unified Score Consistency",
        "source_file": str(INPUT_FILE),
        "formula": "Weighted normalized score using available rounds",
        "tolerance": TOLERANCE,
        "summary": {
            "total_candidates": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "overall_status": (
                "PASS" if failed == 0 and errors == 0 else "FAIL"
            )
        },
        "candidate_results": results
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\nSUMMARY")
    print("-" * 70)
    print("Total candidates:", len(results))
    print("Passed:", passed)
    print("Failed:", failed)
    print("Errors:", errors)
    print("Overall status:", report["summary"]["overall_status"])
    print("\nReport saved:", REPORT_FILE)


if __name__ == "__main__":
    main()
