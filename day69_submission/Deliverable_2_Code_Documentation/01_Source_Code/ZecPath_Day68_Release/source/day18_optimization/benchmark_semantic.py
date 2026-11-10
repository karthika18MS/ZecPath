import os
import time
import sys


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================================
# MAKE PROJECT ROOT AVAILABLE
# ==========================================================

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================================
# IMPORT OPTIMIZED SEMANTIC MODEL
# ==========================================================

from models.semantic_model import get_semantic_model


# ==========================================================
# FILE PATHS
# ==========================================================

# Candidate 006 cleaned resume
RESUME_PATH = os.path.join(
    PROJECT_ROOT,
    "day17_testing",
    "results",
    "candidate_006",
    "cleaned_resume.txt"
)


# IMPORTANT:
# Your job_descriptions folder is FLAT.
#
# Correct:
# day17_testing/job_descriptions/backend_developer.txt
#
# NOT:
# day17_testing/job_descriptions/backend/backend_developer.txt

JD_PATH = os.path.join(
    PROJECT_ROOT,
    "day17_testing",
    "job_descriptions",
    "backend_developer.txt"
)


# ==========================================================
# LOAD TEXT FILE
# ==========================================================

def load_text(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==========================================================
# MAIN BENCHMARK
# ==========================================================

def main():

    print()
    print("=" * 70)
    print(
        "       ZecPath DAY 18 SEMANTIC BENCHMARK"
    )
    print("=" * 70)

    print()
    print("Candidate : candidate_006")
    print("Role      : Backend Developer")

    print()
    print("Resume:")
    print(RESUME_PATH)

    print()
    print("Job Description:")
    print(JD_PATH)

    # ======================================================
    # CHECK FILES
    # ======================================================

    if not os.path.exists(RESUME_PATH):

        print()
        print("ERROR: Resume file not found.")
        print(RESUME_PATH)

        return

    if not os.path.exists(JD_PATH):

        print()
        print("ERROR: Job description file not found.")
        print(JD_PATH)

        return

    # ======================================================
    # LOAD RESUME
    # ======================================================

    try:

        resume_text = load_text(
            RESUME_PATH
        )

    except Exception as error:

        print()
        print(
            f"ERROR loading resume: {error}"
        )

        return

    # ======================================================
    # LOAD JOB DESCRIPTION
    # ======================================================

    try:

        jd_text = load_text(
            JD_PATH
        )

    except Exception as error:

        print()
        print(
            f"ERROR loading job description: {error}"
        )

        return

    print()
    print(
        "Resume and job description loaded successfully."
    )

    # ======================================================
    # MODEL LOADING BENCHMARK
    # ======================================================

    print()
    print("-" * 70)
    print("STEP 1: MODEL LOADING")
    print("-" * 70)

    start_time = time.perf_counter()

    model = get_semantic_model()

    end_time = time.perf_counter()

    model_load_time = (
        end_time - start_time
    )

    print()
    print(
        f"Model loading time: "
        f"{model_load_time:.6f} seconds"
    )

    # ======================================================
    # RESUME EMBEDDING
    # ======================================================

    print()
    print("-" * 70)
    print("STEP 2: RESUME EMBEDDING")
    print("-" * 70)

    start_time = time.perf_counter()

    resume_embedding = model.encode(
        resume_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    end_time = time.perf_counter()

    resume_embedding_time = (
        end_time - start_time
    )

    print()
    print(
        f"Resume embedding time: "
        f"{resume_embedding_time:.6f} seconds"
    )

    print(
        f"Resume embedding length: "
        f"{len(resume_embedding)}"
    )

    # ======================================================
    # JOB DESCRIPTION EMBEDDING
    # ======================================================

    print()
    print("-" * 70)
    print("STEP 3: JOB DESCRIPTION EMBEDDING")
    print("-" * 70)

    start_time = time.perf_counter()

    jd_embedding = model.encode(
        jd_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    end_time = time.perf_counter()

    jd_embedding_time = (
        end_time - start_time
    )

    print()
    print(
        f"JD embedding time: "
        f"{jd_embedding_time:.6f} seconds"
    )

    print(
        f"JD embedding length: "
        f"{len(jd_embedding)}"
    )

    # ======================================================
    # SEMANTIC SIMILARITY
    # ======================================================

    print()
    print("-" * 70)
    print("STEP 4: SEMANTIC SIMILARITY")
    print("-" * 70)

    from sentence_transformers import util

    start_time = time.perf_counter()

    similarity_score = util.cos_sim(
        resume_embedding,
        jd_embedding
    ).item()

    end_time = time.perf_counter()

    similarity_time = (
        end_time - start_time
    )

    similarity_percentage = (
        similarity_score * 100
    )

    print()
    print(
        f"Similarity calculation time: "
        f"{similarity_time:.6f} seconds"
    )

    print()
    print(
        f"Semantic Similarity Score: "
        f"{similarity_score:.4f}"
    )

    print(
        f"Semantic Similarity Percentage: "
        f"{similarity_percentage:.2f}%"
    )

    # ======================================================
    # TOTAL PROCESSING TIME
    # ======================================================

    total_time = (
        model_load_time
        + resume_embedding_time
        + jd_embedding_time
        + similarity_time
    )

    # ======================================================
    # PERFORMANCE REPORT
    # ======================================================

    print()
    print("=" * 70)
    print("       DAY 18 SEMANTIC PERFORMANCE REPORT")
    print("=" * 70)

    print()
    print(
        f"Model Loading       : "
        f"{model_load_time:.6f} sec"
    )

    print(
        f"Resume Embedding    : "
        f"{resume_embedding_time:.6f} sec"
    )

    print(
        f"JD Embedding        : "
        f"{jd_embedding_time:.6f} sec"
    )

    print(
        f"Similarity          : "
        f"{similarity_time:.6f} sec"
    )

    print(
        f"Total Processing    : "
        f"{total_time:.6f} sec"
    )

    print()
    print(
        f"Semantic Score      : "
        f"{similarity_score:.4f}"
    )

    print(
        f"Semantic Percentage : "
        f"{similarity_percentage:.2f}%"
    )

    # ======================================================
    # MEMORY CLEANUP
    # ======================================================

    del resume_embedding
    del jd_embedding

    print()
    print(
        "Temporary embeddings released."
    )

    print()
    print(
        "Semantic benchmark completed successfully."
    )

    print("=" * 70)


# ==========================================================
# PROGRAM ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()