
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SIMULATION_ROOT = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "06_end_to_end_simulation"
)

sys.path.insert(0, str(SIMULATION_ROOT))

from validators.score_validator import ScoreValidator


def main():

    output_file = (
        SIMULATION_ROOT
        / "outputs"
        / "cross_round_scoring_results.json"
    )

    print("=" * 65)
    print("ZECPath DAY 65 - DAY 63 SCORE VALIDATION")
    print("=" * 65)

    if not output_file.is_file():
        print("ERROR: Cross-round output file not found.")
        return

    with output_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    weights = data.get("weights")
    candidates = data.get("candidate_results")

    weight_result = ScoreValidator.validate_weights(weights)

    print("\n1. WEIGHT VALIDATION")
    print("Valid:", weight_result["valid"])
    print("Total weight:", weight_result["total_weight"])
    print("Errors:", weight_result["errors"])

    if not weight_result["valid"]:
        print("\nStopping because scoring weights are invalid.")
        return

    candidate_result = ScoreValidator.validate_candidate_records(
        candidates,
        weights,
    )

    print("\n2. CANDIDATE SCORE VALIDATION")
    print("Total candidates:", candidate_result["total_candidates"])
    print("Valid candidates:", candidate_result["valid_candidates"])
    print("Invalid candidates:", candidate_result["invalid_candidates"])

    print("\n3. VALIDATION ERRORS")

    if candidate_result["errors"]:
        for error in candidate_result["errors"]:
            print(json.dumps(error, indent=4))
    else:
        print("No validation errors.")

    report = {
        "module": "ZecPath Day 65 Score Validation",
        "source_file": str(output_file),
        "weights_validation": weight_result,
        "candidate_validation": candidate_result,
    }

    report_dir = (
        PROJECT_ROOT
        / "day65_final_enhancements"
        / "09_final_outputs"
    )

    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / "day63_score_validation_report.json"

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n4. REPORT SAVED")
    print(report_file)

    print("\nVALIDATION FINISHED")


if __name__ == "__main__":
    main()
