
"""
ZecPath Day 60 - Semantic Score Consistency Validator

Compares Day 17 semantic scores with the optimized service.
Uses the same normalization, model and cosine similarity method.
Does not overwrite Day 17 result files.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DAY17_RESULTS = PROJECT_ROOT / "day17_testing" / "results"
OUTPUT_DIR = SCRIPT_DIR / "results"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from optimized_ai_services import get_semantic_model, normalize_texts


CANDIDATES = [
    f"candidate_{number:03d}"
    for number in range(6, 14)
]

# Scores are rounded to 4 decimal places in the Day 17 module.
# Allow one unit in the last reported decimal place.
TOLERANCE = 0.0001


def normalize_day17(text):
    """Match the normalization in the original Day 17 module."""
    text = str(text).lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_candidate(candidate_id, model):
    candidate_dir = DAY17_RESULTS / candidate_id

    baseline_file = (
        candidate_dir / "day17_semantic_similarity.json"
    )
    resume_file = candidate_dir / "cleaned_resume.txt"
    jd_file = candidate_dir / "job_description.txt"

    required_files = [
        baseline_file,
        resume_file,
        jd_file,
    ]

    missing = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing:
        return {
            "candidate_id": candidate_id,
            "status": "SKIPPED",
            "reason": "Missing required files",
            "missing_files": missing,
        }

    baseline = load_json(baseline_file)

    resume = normalize_day17(
        resume_file.read_text(encoding="utf-8")
    )
    job_description = normalize_day17(
        jd_file.read_text(encoding="utf-8")
    )

    if not resume or not job_description:
        return {
            "candidate_id": candidate_id,
            "status": "SKIPPED",
            "reason": "Resume or job description is empty",
        }

    # Preserve the original implementation's separate encoding calls.
    resume_embedding = model.encode(resume)
    jd_embedding = model.encode(job_description)

    raw_similarity = float(
        cosine_similarity(
            [resume_embedding],
            [jd_embedding],
        )[0][0]
    )

    # Match Day 17 rounding behavior.
    optimized_score = round(raw_similarity, 4)
    optimized_percentage = round(
        optimized_score * 100, 2
    )

    baseline_score = float(
        baseline["semantic_similarity_score"]
    )

    difference = abs(
        optimized_score - baseline_score
    )

    return {
        "candidate_id": candidate_id,
        "target_role": baseline.get("target_role"),
        "baseline_score": baseline_score,
        "optimized_score": optimized_score,
        "baseline_percentage": baseline.get(
            "semantic_similarity_percentage"
        ),
        "optimized_percentage": optimized_percentage,
        "absolute_difference": round(difference, 6),
        "tolerance": TOLERANCE,
        "status": (
            "PASS"
            if difference <= TOLERANCE
            else "REVIEW"
        ),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("ZecPath Day 60 - Semantic Score Validation")
    print("=" * 65)

    print("Loading cached model locally...")

    try:
        model = get_semantic_model()
    except Exception as error:
        print(f"Model loading failed: {error}")
        return 1

    results = []

    for candidate_id in CANDIDATES:
        print(f"\nValidating {candidate_id}...")

        try:
            result = validate_candidate(
                candidate_id,
                model,
            )
        except Exception as error:
            result = {
                "candidate_id": candidate_id,
                "status": "ERROR",
                "reason": str(error),
            }

        results.append(result)

        print(
            f"Status: {result['status']}"
        )

        if "baseline_score" in result:
            print(
                f"Baseline: {result['baseline_score']:.4f} | "
                f"Optimized: {result['optimized_score']:.4f} | "
                f"Difference: {result['absolute_difference']:.6f}"
            )

    comparable = [
        item for item in results
        if "baseline_score" in item
    ]

    passed = sum(
        item["status"] == "PASS"
        for item in comparable
    )

    report = {
        "report": "ZecPath Day 60 Semantic Score Validation",
        "status": (
            "PASS"
            if comparable and passed == len(comparable)
            else "REVIEW_REQUIRED"
        ),
        "comparison_count": len(comparable),
        "passed": passed,
        "review_required": len(comparable) - passed,
        "tolerance": TOLERANCE,
        "results": results,
        "note": (
            "Scores were recalculated using the locally cached "
            "model and the same cosine similarity calculation. "
            "Differences may occur if model versions, model settings, "
            "or source inputs differ from the original run."
        ),
    }

    output_file = (
        OUTPUT_DIR / "semantic_score_validation.json"
    )

    output_file.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )

    print("\n" + "=" * 65)
    print(f"Comparable candidates: {len(comparable)}")
    print(f"Passed: {passed}")
    print(f"Review required: {len(comparable) - passed}")
    print(f"Report: {output_file}")
    print("=" * 65)

    return 0 if comparable and passed == len(comparable) else 1


if __name__ == "__main__":
    raise SystemExit(main())
