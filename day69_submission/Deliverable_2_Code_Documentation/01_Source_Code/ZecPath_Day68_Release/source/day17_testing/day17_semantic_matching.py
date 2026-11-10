
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# ZecPath Day 57 - Optimized Batch Semantic Matching
# ============================================================
# Preserves the original Day 17 semantic scoring behavior.
# Main optimization: load SentenceTransformer only once.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT / "day17_testing"
TEST_CASE_FILE = BASE_DIR / "test_cases.json"
RESULTS_DIR = BASE_DIR / "results"

MODEL_NAME = "all-MiniLM-L6-v2"


def normalize_text(text):
    """Keep the same normalization as the original Day 17 module."""
    text = str(text)
    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def run_input_validation(candidate_id, target_role):
    """
    Generate/refresh cleaned resume and job-description files
    using the existing Day 17 input-validation module.
    """
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
        print(f"\nERROR: Input validation failed for {candidate_id}.")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False

    return True


def load_candidate_text(candidate_id):
    """Read and normalize the existing cleaned resume and JD."""
    candidate_dir = RESULTS_DIR / candidate_id
    resume_file = candidate_dir / "cleaned_resume.txt"
    jd_file = candidate_dir / "job_description.txt"

    if not resume_file.exists():
        raise FileNotFoundError(
            f"Cleaned resume not found: {resume_file}"
        )

    if not jd_file.exists():
        raise FileNotFoundError(
            f"Job description not found: {jd_file}"
        )

    resume_text = normalize_text(
        resume_file.read_text(encoding="utf-8")
    )
    jd_text = normalize_text(
        jd_file.read_text(encoding="utf-8")
    )

    if not resume_text:
        raise ValueError(f"Resume text is empty for {candidate_id}.")

    if not jd_text:
        raise ValueError(
            f"Job description text is empty for {candidate_id}."
        )

    return resume_text, jd_text


def determine_status(similarity_percentage):
    """Keep the original Day 17 thresholds and labels."""
    if similarity_percentage >= 80:
        return "Very Strong Semantic Match"
    elif similarity_percentage >= 70:
        return "Strong Semantic Match"
    elif similarity_percentage >= 60:
        return "Good Semantic Match"
    elif similarity_percentage >= 50:
        return "Moderate Semantic Match"
    else:
        return "Low Semantic Match"


def save_result(candidate_id, target_role, similarity_score,
                similarity_percentage, semantic_status):
    """Save the original five-field JSON schema."""
    output_file = (
        RESULTS_DIR
        / candidate_id
        / "day17_semantic_similarity.json"
    )

    output = {
        "candidate_id": candidate_id,
        "target_role": target_role,
        "semantic_similarity_score": similarity_score,
        "semantic_similarity_percentage": similarity_percentage,
        "semantic_status": semantic_status,
    }

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return output_file


def main():
    start_time = time.perf_counter()

    if not TEST_CASE_FILE.exists():
        print(f"ERROR: Test cases file not found: {TEST_CASE_FILE}")
        return 1

    try:
        with TEST_CASE_FILE.open("r", encoding="utf-8") as file:
            test_cases = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"ERROR: Cannot read test_cases.json: {error}")
        return 1

    if not isinstance(test_cases, dict) or not test_cases:
        print("ERROR: test_cases.json must contain candidate entries.")
        return 1

    print("=" * 70)
    print("ZecPath Day 57 - Optimized Batch Semantic Matching")
    print(f"Candidates configured: {len(test_cases)}")
    print("=" * 70)

    # Phase 1: Prepare fresh inputs for every candidate.
    valid_candidates = []

    for candidate_id, details in test_cases.items():
        if not isinstance(details, dict):
            print(f"ERROR: Invalid configuration for {candidate_id}.")
            continue

        target_role = details.get("target_role")
        if not isinstance(target_role, str) or not target_role.strip():
            print(f"ERROR: Missing target_role for {candidate_id}.")
            continue

        print(f"\nPreparing inputs: {candidate_id} - {target_role}")

        if run_input_validation(candidate_id, target_role):
            valid_candidates.append((candidate_id, target_role))
        else:
            print(f"Skipping semantic matching for {candidate_id}.")

    if not valid_candidates:
        print("\nERROR: No candidates have valid input files.")
        return 1

    # Phase 2: Load the model once for the entire batch.
    print(f"\nLoading model once: {MODEL_NAME}")
    model_start = time.perf_counter()

    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as error:
        print(f"ERROR: Could not load SentenceTransformer: {error}")
        print(
            "Check that the model is available locally or that "
            "your network permits downloading it."
        )
        return 1

    model_load_seconds = time.perf_counter() - model_start
    print(f"Model load time: {model_load_seconds:.2f} seconds")

    # Phase 3: Process each candidate using the same loaded model.
    successful = 0
    failed = 0

    for candidate_id, target_role in valid_candidates:
        candidate_start = time.perf_counter()

        try:
            resume_text, jd_text = load_candidate_text(candidate_id)

            # Keep separate encode calls, as in the original module.
            resume_embedding = model.encode(resume_text)
            jd_embedding = model.encode(jd_text)

            similarity = cosine_similarity(
                [resume_embedding],
                [jd_embedding],
            )

            similarity_score = float(similarity[0][0])
            similarity_percentage = similarity_score * 100

            # Preserve the original rounding order.
            similarity_score = round(similarity_score, 4)
            similarity_percentage = round(similarity_percentage, 2)

            semantic_status = determine_status(similarity_percentage)

            output_file = save_result(
                candidate_id,
                target_role,
                similarity_score,
                similarity_percentage,
                semantic_status,
            )

            elapsed = time.perf_counter() - candidate_start
            successful += 1

            print(f"\nCandidate: {candidate_id}")
            print(f"Target role: {target_role}")
            print(f"Semantic score: {similarity_score:.4f}")
            print(f"Semantic percentage: {similarity_percentage:.2f}%")
            print(f"Semantic status: {semantic_status}")
            print(f"Saved: {output_file}")
            print(f"Candidate processing time: {elapsed:.2f} seconds")

        except Exception as error:
            failed += 1
            print(f"\nERROR processing {candidate_id}: {error}")

    total_seconds = time.perf_counter() - start_time

    print("\n" + "=" * 70)
    print("BATCH SEMANTIC MATCHING SUMMARY")
    print(f"Configured candidates: {len(test_cases)}")
    print(f"Prepared candidates: {len(valid_candidates)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Model load time: {model_load_seconds:.2f} seconds")
    print(f"Total elapsed time: {total_seconds:.2f} seconds")
    print("=" * 70)

    return 0 if failed == 0 and successful == len(test_cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
