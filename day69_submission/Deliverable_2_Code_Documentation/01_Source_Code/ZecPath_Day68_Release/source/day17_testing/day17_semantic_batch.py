
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT / "day17_testing"
TEST_CASE_FILE = BASE_DIR / "test_cases.json"
RESULTS_DIR = BASE_DIR / "results"

MODEL_NAME = "all-MiniLM-L6-v2"


def normalize_text(text):
    text = str(text).lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prepare_inputs(candidate_id, target_role):
    command = [
        sys.executable,
        "-m",
        "day17_testing.run_day17_test",
        candidate_id,
        target_role,
    ]

    result = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR preparing {candidate_id}")
        print(result.stdout)
        print(result.stderr)
        return False

    return True


def load_text(candidate_id):
    folder = RESULTS_DIR / candidate_id

    resume_file = folder / "cleaned_resume.txt"
    jd_file = folder / "job_description.txt"

    if not resume_file.exists():
        raise FileNotFoundError(f"Missing file: {resume_file}")

    if not jd_file.exists():
        raise FileNotFoundError(f"Missing file: {jd_file}")

    resume = normalize_text(
        resume_file.read_text(encoding="utf-8")
    )
    job_description = normalize_text(
        jd_file.read_text(encoding="utf-8")
    )

    if not resume:
        raise ValueError(f"Empty resume: {candidate_id}")

    if not job_description:
        raise ValueError(f"Empty job description: {candidate_id}")

    return resume, job_description


def determine_status(percentage):
    if percentage >= 80:
        return "Very Strong Semantic Match"
    elif percentage >= 70:
        return "Strong Semantic Match"
    elif percentage >= 60:
        return "Good Semantic Match"
    elif percentage >= 50:
        return "Moderate Semantic Match"
    return "Low Semantic Match"


def save_result(candidate_id, target_role, score, percentage, status):
    output_file = (
        RESULTS_DIR
        / candidate_id
        / "day17_semantic_similarity.json"
    )

    output = {
        "candidate_id": candidate_id,
        "target_role": target_role,
        "semantic_similarity_score": score,
        "semantic_similarity_percentage": percentage,
        "semantic_status": status,
    }

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    return output_file


def main():
    start = time.perf_counter()

    if not TEST_CASE_FILE.exists():
        print(f"ERROR: Missing {TEST_CASE_FILE}")
        return 1

    with TEST_CASE_FILE.open("r", encoding="utf-8") as file:
        test_cases = json.load(file)

    if not isinstance(test_cases, dict) or not test_cases:
        print("ERROR: test_cases.json must contain candidate entries.")
        return 1

    print("=" * 65)
    print("ZecPath Day 57 - Optimized Batch Semantic Matching")
    print(f"Candidates configured: {len(test_cases)}")
    print("=" * 65)

    valid_candidates = []

    # Prepare each candidate's cleaned resume and job description.
    for candidate_id, details in test_cases.items():
        if not isinstance(details, dict):
            print(f"ERROR: Invalid configuration: {candidate_id}")
            continue

        target_role = details.get("target_role")

        if not isinstance(target_role, str) or not target_role.strip():
            print(f"ERROR: Missing target role: {candidate_id}")
            continue

        print(f"\nPreparing: {candidate_id} - {target_role}")

        if prepare_inputs(candidate_id, target_role):
            valid_candidates.append((candidate_id, target_role))

    if not valid_candidates:
        print("ERROR: No candidates could be prepared.")
        return 1

    # Load the semantic model only once.
    print(f"\nLoading model: {MODEL_NAME}")
    model_start = time.perf_counter()

    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as error:
        print(f"ERROR loading model: {error}")
        return 1

    model_load_time = time.perf_counter() - model_start
    print(f"Model load time: {model_load_time:.2f} seconds")

    successful = 0
    failed = 0

    # Process all candidates with the same loaded model.
    for candidate_id, target_role in valid_candidates:
        candidate_start = time.perf_counter()

        try:
            resume, job_description = load_text(candidate_id)

            # Preserve the original separate encoding operations.
            resume_embedding = model.encode(resume)
            jd_embedding = model.encode(job_description)

            similarity = cosine_similarity(
                [resume_embedding],
                [jd_embedding],
            )

            score = round(float(similarity[0][0]), 4)
            percentage = round(float(similarity[0][0]) * 100, 2)
            status = determine_status(percentage)

            output_file = save_result(
                candidate_id,
                target_role,
                score,
                percentage,
                status,
            )

            successful += 1

            print(f"\nCandidate: {candidate_id}")
            print(f"Semantic score: {score:.4f}")
            print(f"Semantic percentage: {percentage:.2f}%")
            print(f"Status: {status}")
            print(f"Saved: {output_file}")
            print(
                "Processing time: "
                f"{time.perf_counter() - candidate_start:.2f} seconds"
            )

        except Exception as error:
            failed += 1
            print(f"ERROR processing {candidate_id}: {error}")

    print("\n" + "=" * 65)
    print("BATCH SUMMARY")
    print(f"Configured: {len(test_cases)}")
    print(f"Prepared: {len(valid_candidates)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Model load time: {model_load_time:.2f} seconds")
    print(f"Total elapsed: {time.perf_counter() - start:.2f} seconds")
    print("=" * 65)

    if failed == 0 and successful == len(test_cases):
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
