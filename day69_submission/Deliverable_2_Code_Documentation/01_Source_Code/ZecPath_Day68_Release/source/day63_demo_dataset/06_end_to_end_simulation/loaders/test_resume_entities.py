
import sys
from pathlib import Path


# ==========================================================
# PROJECT PATH CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Add project root to Python module search path.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================================
# EXISTING ZECPath MODULE IMPORTS
# ==========================================================

from parsers.pdf_parser import extract_pdf_text
from parsers.noisy_text_cleaner import clean_noisy_resume_text
from parsers.entity_detector import extract_entities


# ==========================================================
# DATASET PATH
# ==========================================================

RESUME_ROOT = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "02_sample_resumes"
)


# ==========================================================
# TEST ALL RESUMES
# ==========================================================

def test_all_resumes():

    resume_files = sorted(
        RESUME_ROOT.rglob("*.pdf")
    )

    print("\nZecPath Day 63 Resume Entity Validation")
    print("=" * 75)

    print("Project root:", PROJECT_ROOT)
    print("Resume directory:", RESUME_ROOT)
    print("Total PDF resumes:", len(resume_files))

    successful = 0
    failed = 0

    for resume_path in resume_files:

        print("\nRESUME:", resume_path.name)

        try:

            # Step 1: Extract PDF text
            raw_text = extract_pdf_text(
                str(resume_path)
            )

            # Step 2: Clean extracted text
            cleaned_text = clean_noisy_resume_text(
                raw_text
            )

            if not cleaned_text.strip():
                raise ValueError(
                    "No extractable resume text"
                )

            # Step 3: Extract entities
            entities = extract_entities(
                cleaned_text
            )

            # Step 4: Display extracted information
            print(
                "Characters:",
                len(cleaned_text)
            )

            print(
                "Name:",
                entities["name"]
            )

            print(
                "Job Titles:",
                entities["job_titles"]
            )

            print(
                "Experience:",
                entities["experience_years"]
            )

            print(
                "Degrees:",
                entities["degrees"]
            )

            print(
                "Skills:",
                entities["skills"]
            )

            print(
                "Sections:",
                list(entities["sections"].keys())
            )

            successful += 1

            print("Status: EXTRACTION SUCCESS")

        except Exception as error:

            failed += 1

            print("Status: FAILED")
            print("Error:", str(error))

        print("-" * 75)

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print("\nFINAL SUMMARY")
    print("=" * 75)

    print("Total resumes:", len(resume_files))
    print("Successful:", successful)
    print("Failed:", failed)

    if failed == 0 and len(resume_files) > 0:

        print(
            "RESULT: ALL RESUME EXTRACTIONS SUCCESSFUL"
        )

    else:

        print(
            "RESULT: SOME RESUMES NEED INVESTIGATION"
        )


# ==========================================================
# EXECUTION
# ==========================================================

if __name__ == "__main__":
    test_all_resumes()
