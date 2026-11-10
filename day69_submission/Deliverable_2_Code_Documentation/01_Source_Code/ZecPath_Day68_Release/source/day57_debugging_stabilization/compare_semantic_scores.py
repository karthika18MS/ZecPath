
import json
from pathlib import Path

# ============================================================
# ZecPath Day 57 - Semantic Score Comparison
# ============================================================
# Compare original semantic scores against optimized scores.
# This script only reads files; it does not modify any scores.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASELINE_DIR = (
    PROJECT_ROOT
    / "day57_debugging_stabilization"
    / "baseline_semantic"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "day17_testing"
    / "results"
)

TEST_CASE_FILE = (
    PROJECT_ROOT
    / "day17_testing"
    / "test_cases.json"
)

SCORE_TOLERANCE = 0.0001
PERCENTAGE_TOLERANCE = 0.01

REQUIRED_FIELDS = {
    "candidate_id",
    "target_role",
    "semantic_similarity_score",
    "semantic_similarity_percentage",
    "semantic_status",
}


def load_json(file_path):
    """Read and return JSON data."""
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_score(value, field_name):
    """Ensure a score is numeric and between 0 and 100."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")

    if not 0 <= value <= 100:
        raise ValueError(f"{field_name} must be between 0 and 100.")

    return float(value)


def compare_candidate(candidate_id):
    """Compare one candidate's original and optimized results."""

    baseline_file = BASELINE_DIR / f"{candidate_id}.json"

    optimized_file = (
        RESULTS_DIR
        / candidate_id
        / "day17_semantic_similarity.json"
    )

    if not baseline_file.exists():
        return False, f"Baseline file missing: {baseline_file}"

    if not optimized_file.exists():
        return False, f"Optimized file missing: {optimized_file}"

    try:
        old = load_json(baseline_file)
        new = load_json(optimized_file)

        if not isinstance(old, dict) or not isinstance(new, dict):
            raise ValueError("Both JSON outputs must be objects.")

        if set(old.keys()) != REQUIRED_FIELDS:
            raise ValueError("Baseline JSON schema has changed.")

        if set(new.keys()) != REQUIRED_FIELDS:
            raise ValueError("Optimized JSON schema has changed.")

        # Validate candidate identity.
        if old["candidate_id"] != candidate_id:
            raise ValueError("Baseline candidate ID mismatch.")

        if new["candidate_id"] != candidate_id:
            raise ValueError("Optimized candidate ID mismatch.")

        # Validate target role.
        if old["target_role"] != new["target_role"]:
            raise ValueError("Target role differs from baseline.")

        old_score = validate_score(
            old["semantic_similarity_score"],
            "Baseline similarity score",
        )
        new_score = validate_score(
            new["semantic_similarity_score"],
            "Optimized similarity score",
        )

        old_percentage = validate_score(
            old["semantic_similarity_percentage"],
            "Baseline similarity percentage",
        )
        new_percentage = validate_score(
            new["semantic_similarity_percentage"],
            "Optimized similarity percentage",
        )

        score_difference = abs(old_score - new_score)
        percentage_difference = abs(
            old_percentage - new_percentage
        )

        status_matches = (
            old["semantic_status"] == new["semantic_status"]
        )

        passed = (
            score_difference <= SCORE_TOLERANCE
            and percentage_difference <= PERCENTAGE_TOLERANCE
            and status_matches
        )

        result = "PASS" if passed else "FAIL"

        details = (
            f"Old score: {old_score:.4f} | "
            f"New score: {new_score:.4f}\n"
            f"Old percentage: {old_percentage:.2f}% | "
            f"New percentage: {new_percentage:.2f}%\n"
            f"Old status: {old['semantic_status']} | "
            f"New status: {new['semantic_status']}\n"
            f"Score difference: {score_difference:.4f}\n"
            f"Percentage difference: {percentage_difference:.2f}\n"
            f"Result: {result}"
        )

        return passed, details

    except (
        OSError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        return False, f"Invalid or unreadable output: {error}"


def main():
    print("=" * 75)
    print("ZecPath Day 57 - Semantic Score Comparison")
    print("=" * 75)

    if not TEST_CASE_FILE.exists():
        print(f"ERROR: Test cases file not found: {TEST_CASE_FILE}")
        return 1

    if not BASELINE_DIR.exists():
        print(f"ERROR: Baseline directory not found: {BASELINE_DIR}")
        return 1

    try:
        test_cases = load_json(TEST_CASE_FILE)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR reading test_cases.json: {error}")
        return 1

    if not isinstance(test_cases, dict) or not test_cases:
        print("ERROR: test_cases.json contains no valid candidates.")
        return 1

    passed_count = 0
    failed_count = 0

    for candidate_id in test_cases:
        print(f"\nCandidate: {candidate_id}")

        passed, details = compare_candidate(candidate_id)
        print(details)

        if passed:
            passed_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 75)
    print("COMPARISON SUMMARY")
    print(f"Total candidates: {len(test_cases)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print("=" * 75)

    if failed_count == 0 and passed_count == len(test_cases):
        print("RESULT: PASS - all semantic outputs match the baseline.")
        return 0

    print("RESULT: REVIEW REQUIRED - investigate failures before proceeding.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
