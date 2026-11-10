
import os
import sys
import json
import subprocess


# ==========================================================
# ZecPath - Day 17 Batch Testing Runner
# Day 57: Optimized Batch Semantic Matching
# ==========================================================
#
# Pipeline:
# 1. Run semantic matching ONCE for all candidates
# 2. Input Validation
# 3. Skill Matching
# 4. Experience Matching
# 5. Education Matching
# 6. Final ATS Scoring
# 7. Save batch summary
#
# Run from the project root:
# python -m day17_testing.day17_batch_runner
# ==========================================================


# ==========================================================
# STEP 1: Project Paths
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

BASE_DIR = os.path.join(
    PROJECT_ROOT,
    "day17_testing"
)

TEST_CASE_FILE = os.path.join(
    BASE_DIR,
    "test_cases.json"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

SUMMARY_FILE = os.path.join(
    RESULTS_DIR,
    "day17_batch_summary.json"
)


# ==========================================================
# STEP 2: Load and Validate Test Cases
# ==========================================================

if not os.path.exists(TEST_CASE_FILE):
    print("\nERROR: test_cases.json not found.")
    print("Expected:", TEST_CASE_FILE)
    sys.exit(1)

try:
    with open(
        TEST_CASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

except json.JSONDecodeError as error:
    print("\nERROR: Invalid JSON in test_cases.json.")
    print(error)
    sys.exit(1)

if not isinstance(test_cases, dict):
    print(
        "\nERROR: test_cases.json must contain "
        "candidate IDs as keys."
    )
    sys.exit(1)

if not test_cases:
    print("\nERROR: No candidates found in test_cases.json.")
    sys.exit(1)

os.makedirs(RESULTS_DIR, exist_ok=True)


# ==========================================================
# STEP 3: Run One Candidate Module
# ==========================================================

def run_module(module_name, candidate_id, target_role):
    command = [
        sys.executable,
        "-m",
        module_name,
        candidate_id,
        target_role
    ]

    print("\n" + "=" * 75)
    print("Running Module:", module_name)
    print("Candidate:", candidate_id)
    print("Target Role:", target_role)
    print("=" * 75)

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

    except Exception as error:
        print("\nERROR while starting module:")
        print(error)
        return False

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print("\nERROR:")
        print(
            f"{module_name} failed for {candidate_id}"
        )
        return False

    return True


# ==========================================================
# STEP 4: Optimized Semantic Batch Runner
# ==========================================================

def run_semantic_batch():
    """
    Run the optimized semantic engine once for all candidates.
    Stop the ATS pipeline if semantic matching fails.
    """

    module_name = "day17_testing.day17_semantic_batch"

    print("\n" + "=" * 80)
    print("STARTING OPTIMIZED BATCH SEMANTIC MATCHING")
    print("The semantic model should load once for this batch.")
    print("=" * 80)

    command = [
        sys.executable,
        "-m",
        module_name
    ]

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

    except Exception as error:
        print("\nERROR: Could not start semantic batch.")
        print(error)
        return False

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print("\nERROR: Batch semantic matching failed.")
        print(
            "Stopping to avoid using stale semantic scores."
        )
        return False

    print("\nOptimized semantic batch completed.")

    return True


# ==========================================================
# STEP 5: Define Remaining ATS Pipeline
# ==========================================================
#
# IMPORTANT:
# Semantic matching is intentionally NOT listed here.
# It is run once by run_semantic_batch() above.
# ==========================================================

pipeline = [
    (
        "day17_testing.run_day17_test",
        "Input Validation"
    ),
    (
        "day17_testing.day17_skill_matching",
        "Skill Matching"
    ),
    (
        "day17_testing.day17_experience",
        "Experience Matching"
    ),
    (
        "day17_testing.day17_education",
        "Education Matching"
    ),
    (
        "day17_testing.day17_final_scoring",
        "Final ATS Scoring"
    )
]


# ==========================================================
# STEP 6: Start Batch Processing
# ==========================================================

print("\n" + "#" * 80)
print("#             ZecPath DAY 17 BATCH TESTING")
print("#             DAY 57 SEMANTIC OPTIMIZATION")
print("#" * 80)

print(f"\nTotal Test Cases: {len(test_cases)}")


# Run semantic matching exactly once, before the loop.
semantic_success = run_semantic_batch()

if not semantic_success:
    print("\nBatch stopped because semantic matching failed.")
    sys.exit(1)


# Verify that the batch produced a valid semantic result for every candidate.
# This prevents continuing with missing or invalid semantic scores.
print("\nVerifying semantic outputs for all candidates...")

semantic_errors = []

for candidate_id in test_cases:
    semantic_file = os.path.join(
        RESULTS_DIR,
        candidate_id,
        "day17_semantic_similarity.json"
    )

    if not os.path.isfile(semantic_file):
        semantic_errors.append(
            f"{candidate_id}: semantic output file is missing: {semantic_file}"
        )
        continue

    try:
        with open(semantic_file, "r", encoding="utf-8") as file:
            semantic_result = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        semantic_errors.append(
            f"{candidate_id}: could not read semantic output ({error})"
        )
        continue

    if semantic_result.get("candidate_id") != candidate_id:
        semantic_errors.append(
            f"{candidate_id}: candidate_id in semantic output does not match"
        )
        continue

    score = semantic_result.get("semantic_similarity_score")
    percentage = semantic_result.get("semantic_similarity_percentage")

    if not isinstance(score, (int, float)) or not 0 <= score <= 1:
        semantic_errors.append(
            f"{candidate_id}: semantic_similarity_score must be between 0 and 1"
        )

    if not isinstance(percentage, (int, float)) or not 0 <= percentage <= 100:
        semantic_errors.append(
            f"{candidate_id}: semantic_similarity_percentage must be between 0 and 100"
        )

if semantic_errors:
    print("\nERROR: Semantic output verification failed.")
    for error in semantic_errors:
        print(" -", error)
    print("Stopping to avoid using missing or invalid semantic results.")
    sys.exit(1)

print(f"Semantic output verification passed: {len(test_cases)} candidates checked.")


# ==========================================================
# STEP 7: Process Each Candidate
# ==========================================================

batch_results = []

for candidate_id, test_case in test_cases.items():

    print("\n\n" + "#" * 80)
    print(f"# Candidate ID : {candidate_id}")

    target_role = test_case.get("target_role")
    job_description = test_case.get("job_description")

    print(f"# Target Role  : {target_role}")
    print(f"# Job File     : {job_description}")
    print("#" * 80)

    # ------------------------------------------------------
    # Validate candidate configuration
    # ------------------------------------------------------

    if not target_role:
        print("\nERROR: target_role is missing.")

        batch_results.append({
            "candidate_id": candidate_id,
            "target_role": None,
            "job_description": job_description,
            "pipeline_status": "FAILED",
            "failed_stage": "Configuration",
            "final_ats_score": None,
            "matching_status": None,
            "shortlisting_status": None,
            "recommendation": None
        })

        continue

    if not job_description:
        print("\nERROR: job_description is missing.")

        batch_results.append({
            "candidate_id": candidate_id,
            "target_role": target_role,
            "job_description": None,
            "pipeline_status": "FAILED",
            "failed_stage": "Configuration",
            "final_ats_score": None,
            "matching_status": None,
            "shortlisting_status": None,
            "recommendation": None
        })

        continue

    # ------------------------------------------------------
    # Run remaining ATS modules
    # ------------------------------------------------------

    candidate_success = True
    failed_stage = None

    for module_name, stage_name in pipeline:

        print(f"\n>>> STARTING {stage_name}")

        success = run_module(
            module_name,
            candidate_id,
            target_role
        )

        if not success:
            candidate_success = False
            failed_stage = stage_name

            print("\n" + "!" * 70)
            print(f"Pipeline FAILED for {candidate_id}")
            print(f"Failed Stage: {stage_name}")
            print("!" * 70)

            break

    # ------------------------------------------------------
    # Read final ATS result
    # ------------------------------------------------------

    final_file = os.path.join(
        RESULTS_DIR,
        candidate_id,
        "day17_final_ats_score.json"
    )

    final_result = None

    if candidate_success:
        if not os.path.exists(final_file):
            print("\nERROR: Final ATS result file not found.")
            print(final_file)

            candidate_success = False
            failed_stage = "Final ATS Result Verification"

        else:
            try:
                with open(
                    final_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    final_result = json.load(file)

            except (json.JSONDecodeError, OSError) as error:
                print("\nERROR: Could not read final ATS JSON.")
                print(error)

                candidate_success = False
                failed_stage = "Final ATS Result Reading"

    # ------------------------------------------------------
    # Create candidate summary
    # ------------------------------------------------------

    candidate_summary = {
        "candidate_id": candidate_id,
        "target_role": target_role,
        "job_description": job_description,
        "pipeline_status": (
            "SUCCESS" if candidate_success else "FAILED"
        ),
        "failed_stage": failed_stage,
        "final_ats_score": (
            final_result.get("final_ats_score")
            if final_result else None
        ),
        "matching_status": (
            final_result.get("matching_status")
            if final_result else None
        ),
        "shortlisting_status": (
            final_result.get("shortlisting_status")
            if final_result else None
        ),
        "recommendation": (
            final_result.get("recommendation")
            if final_result else None
        )
    }

    batch_results.append(candidate_summary)


# ==========================================================
# STEP 8: Save Batch Summary
# ==========================================================

with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        batch_results,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==========================================================
# STEP 9: Display Final Summary
# ==========================================================

print("\n\n" + "=" * 95)
print("                 ZecPath DAY 17 BATCH SUMMARY")
print("=" * 95)

print()
print(
    f"{'Candidate':<16}"
    f"{'Target Role':<32}"
    f"{'ATS Score':<12}"
    f"{'Status':<12}"
)
print("-" * 95)

for result in batch_results:

    candidate = result.get("candidate_id", "N/A")
    role = result.get("target_role") or "N/A"
    score = result.get("final_ats_score")
    status = result.get("pipeline_status", "FAILED")

    if isinstance(score, (int, float)):
        score_text = f"{score:.2f}%"
    else:
        score_text = "N/A"

    print(
        f"{candidate:<16}"
        f"{role:<32}"
        f"{score_text:<12}"
        f"{status:<12}"
    )


# ==========================================================
# STEP 10: Calculate Statistics
# ==========================================================

total_candidates = len(batch_results)

successful_candidates = sum(
    1
    for result in batch_results
    if result.get("pipeline_status") == "SUCCESS"
)

failed_candidates = (
    total_candidates - successful_candidates
)

print("\n")
print("Total Candidates :", total_candidates)
print("Successful Tests :", successful_candidates)
print("Failed Tests     :", failed_candidates)

print("\nBatch summary saved to:")
print(SUMMARY_FILE)

print("\nDay 17 batch testing completed.")
print("=" * 95)
