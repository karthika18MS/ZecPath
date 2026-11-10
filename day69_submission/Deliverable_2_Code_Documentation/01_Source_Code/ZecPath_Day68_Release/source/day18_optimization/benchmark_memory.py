import os
import gc
import sys
import time
import psutil


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
# PROCESS
# ==========================================================

PROCESS = psutil.Process(
    os.getpid()
)


# ==========================================================
# MEMORY FUNCTION
# ==========================================================

def memory_mb():

    return (
        PROCESS.memory_info().rss
        / (1024 * 1024)
    )


def print_memory(label):

    print(
        f"{label:<35}: "
        f"{memory_mb():.2f} MB"
    )


# ==========================================================
# LOAD TEXT
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
# MAIN
# ==========================================================

def main():

    print()
    print("=" * 70)
    print(
        "       ZecPath DAY 18 MEMORY BENCHMARK"
    )
    print("=" * 70)

    # ======================================================
    # STAGE 1 — INITIAL MEMORY
    # ======================================================

    print()
    print("MEMORY STAGE 1")

    print_memory(
        "Before Model Load"
    )

    # ======================================================
    # STAGE 2 — MODEL LOADING
    # ======================================================

    start_time = time.perf_counter()

    model = get_semantic_model()

    end_time = time.perf_counter()

    model_load_time = (
        end_time - start_time
    )

    print()
    print(
        f"Model Load Time: "
        f"{model_load_time:.6f} seconds"
    )

    print_memory(
        "After Model Load"
    )

    # ======================================================
    # FILE PATHS
    # ======================================================

    # Candidate 006 cleaned resume
    resume_path = os.path.join(
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

    jd_path = os.path.join(
        PROJECT_ROOT,
        "day17_testing",
        "job_descriptions",
        "backend_developer.txt"
    )

    # ======================================================
    # CHECK FILES
    # ======================================================

    print()
    print("Checking input files...")

    print()
    print("Resume:")
    print(resume_path)

    print()
    print("Job Description:")
    print(jd_path)

    if not os.path.exists(resume_path):

        print()
        print("ERROR: Resume file not found.")

        print(
            resume_path
        )

        return

    if not os.path.exists(jd_path):

        print()
        print(
            "ERROR: Job description file not found."
        )

        print(
            jd_path
        )

        return

    print()
    print(
        "Input files found successfully."
    )

    # ======================================================
    # STAGE 3 — TEXT LOADING
    # ======================================================

    resume_text = load_text(
        resume_path
    )

    jd_text = load_text(
        jd_path
    )

    print_memory(
        "After Text Loading"
    )

    # ======================================================
    # STAGE 4 — RESUME EMBEDDING
    # ======================================================

    print()
    print(
        "Generating resume embedding..."
    )

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
        f"Resume Embedding Time: "
        f"{resume_embedding_time:.6f} seconds"
    )

    print_memory(
        "After Resume Embedding"
    )

    # ======================================================
    # STAGE 5 — JD EMBEDDING
    # ======================================================

    print()
    print(
        "Generating JD embedding..."
    )

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
        f"JD Embedding Time: "
        f"{jd_embedding_time:.6f} seconds"
    )

    print_memory(
        "After JD Embedding"
    )

    # ======================================================
    # STAGE 6 — EMBEDDING CLEANUP
    # ======================================================

    print()
    print(
        "Cleaning temporary embeddings..."
    )

    del resume_embedding
    del jd_embedding

    gc.collect()

    print_memory(
        "After Embedding Cleanup"
    )

    # ======================================================
    # STAGE 7 — TEXT CLEANUP
    # ======================================================

    del resume_text
    del jd_text

    gc.collect()

    print_memory(
        "After Text Cleanup"
    )

    # ======================================================
    # FINAL REPORT
    # ======================================================

    print()
    print("=" * 70)
    print(
        "       DAY 18 MEMORY PERFORMANCE REPORT"
    )
    print("=" * 70)

    print()
    print(
        f"Model Load Time       : "
        f"{model_load_time:.6f} sec"
    )

    print(
        f"Resume Embedding Time : "
        f"{resume_embedding_time:.6f} sec"
    )

    print(
        f"JD Embedding Time     : "
        f"{jd_embedding_time:.6f} sec"
    )

    print()
    print(
        f"Initial Memory        : "
        f"{memory_mb():.2f} MB"
    )

    print()
    print(
        "Memory benchmark completed successfully."
    )

    print()
    print(
        "The Sentence Transformer model remains "
        "loaded intentionally for reuse."
    )

    print("=" * 70)


# ==========================================================
# PROGRAM ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()