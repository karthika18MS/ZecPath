#Since your project already contains DOCX/PDF parsers, this benchmark measures actual extraction using
#common libraries while avoiding assumptions about the function names inside your existing parser files.
import os
import sys
import time


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================================
# TEST FILE
# ==========================================================

RESUME_PATH = os.path.join(
    PROJECT_ROOT,
    "day17_testing",
    "resumes",
    "candidate_006.docx"
)


# ==========================================================
# DOCX EXTRACTION
# ==========================================================

def extract_docx(file_path):

    from docx import Document

    document = Document(
        file_path
    )

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:

            paragraphs.append(
                text
            )

    return "\n".join(
        paragraphs
    )


# ==========================================================
# BENCHMARK
# ==========================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "       ZecPath DAY 18 EXTRACTION BENCHMARK"
    )
    print("=" * 70)

    if not os.path.exists(
        RESUME_PATH
    ):

        print(
            f"\nERROR: Resume not found:"
        )

        print(
            RESUME_PATH
        )

        return

    print(
        f"\nTest Resume:"
    )

    print(
        RESUME_PATH
    )

    file_size = os.path.getsize(
        RESUME_PATH
    )

    print(
        f"File Size: {file_size:,} bytes"
    )

    # ------------------------------------------------------
    # Extraction timing
    # ------------------------------------------------------

    start = time.perf_counter()

    extracted_text = extract_docx(
        RESUME_PATH
    )

    end = time.perf_counter()

    extraction_time = (
        end - start
    )

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    character_count = len(
        extracted_text
    )

    word_count = len(
        extracted_text.split()
    )

    line_count = len(
        extracted_text.splitlines()
    )

    print("\n")
    print("-" * 70)
    print("EXTRACTION PERFORMANCE")
    print("-" * 70)

    print(
        f"Extraction Time : "
        f"{extraction_time:.6f} seconds"
    )

    print(
        f"Characters      : "
        f"{character_count}"
    )

    print(
        f"Words           : "
        f"{word_count}"
    )

    print(
        f"Lines           : "
        f"{line_count}"
    )

    print("\n")
    print(
        "Extraction benchmark completed."
    )


if __name__ == "__main__":

    main()
