import json
import time
from pathlib import Path


# Day 54 - D1: Improved AI Accuracy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "day54" / "results" / "accuracy_evaluation.json"

# Demo records only.
# Replace these with verified evaluation records.
EVALUATION_DATA = [
    {"actual": "SELECTED", "predicted": "SELECTED"},
    {"actual": "REJECTED", "predicted": "REJECTED"},
    {"actual": "SELECTED", "predicted": "HOLD / REVIEW"},
    {"actual": "REJECTED", "predicted": "REJECTED"},
    {"actual": "HOLD / REVIEW", "predicted": "HOLD / REVIEW"},
]

VALID_DECISIONS = {
    "SELECTED",
    "HOLD / REVIEW",
    "REJECTED"
}


def analyze_predictions(records):
    if not records:
        raise ValueError("Evaluation data cannot be empty.")

    started = time.perf_counter()
    correct = 0
    false_positives = 0
    false_negatives = 0
    mismatches = []

    for index, record in enumerate(records, start=1):
        actual = record.get("actual")
        predicted = record.get("predicted")

        if actual not in VALID_DECISIONS:
            raise ValueError(f"Invalid actual decision at row {index}")

        if predicted not in VALID_DECISIONS:
            raise ValueError(f"Invalid predicted decision at row {index}")

        if actual == predicted:
            correct += 1
        else:
            mismatches.append({
                "row": index,
                "actual": actual,
                "predicted": predicted
            })

        # Treat SELECTED as the positive class for this analysis.
        if predicted == "SELECTED" and actual != "SELECTED":
            false_positives += 1

        if actual == "SELECTED" and predicted != "SELECTED":
            false_negatives += 1

    elapsed_seconds = round(time.perf_counter() - started, 6)

    total = len(records)
    accuracy = round((correct / total) * 100, 2)

    return {
        "evaluation_type": "DEMO" if EVALUATION_DATA == records else "INPUT",
        "total_records": total,
        "correct_predictions": correct,
        "incorrect_predictions": total - correct,
        "accuracy_percent": accuracy,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "mismatches": mismatches,
        "processing_time_seconds": elapsed_seconds,
        "note": (
            "False positives and false negatives treat SELECTED "
            "as the positive class. Accuracy is meaningful only "
            "when actual labels are verified."
        )
    }


if __name__ == "__main__":
    result = analyze_predictions(EVALUATION_DATA)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)

    print("DAY 54 - ACCURACY ANALYSIS")
    print(json.dumps(result, indent=4))
    print("Saved to:", OUTPUT_FILE)
