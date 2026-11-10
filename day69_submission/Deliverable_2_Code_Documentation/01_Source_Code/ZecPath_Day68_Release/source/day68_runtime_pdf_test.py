
from pathlib import Path

import education_parser as ep
import experience_parser as xp
import pdf_reader
from parsers import pdf_parser


# ==========================================================
# Resume PDF Files
# ==========================================================

RESUME_FILES = [
    Path("data/resumes/samplee_resume.pdf"),
    Path("data/resumes/sample_resume.pdf"),
]


# ==========================================================
# PDF Runtime Integration Test
# ==========================================================

def test_pdf_runtime():

    # Correct function names from the four source files
    extractors = {
        "Education Parser": ep.read_pdf,
        "Experience Parser": xp.read_pdf,
        "PDF Reader": pdf_reader.extract_text_from_pdf,
        "PDF Parser": pdf_parser.extract_pdf_text,
    }

    total_checks = 0

    print("\n========================================")
    print("ZECPath DAY 68 PDF RUNTIME TEST")
    print("========================================")

    # ------------------------------------------------------
    # Test Each Resume
    # ------------------------------------------------------

    for resume_path in RESUME_FILES:

        print("\n----------------------------------------")
        print("Testing:", resume_path)
        print("----------------------------------------")

        if not resume_path.exists():
            raise FileNotFoundError(
                f"Resume PDF not found: {resume_path}"
            )

        extracted_text = {}

        # --------------------------------------------------
        # Test All Four PDF Extraction Modules
        # --------------------------------------------------

        for name, extractor in extractors.items():

            text = extractor(str(resume_path))

            if not isinstance(text, str) or not text.strip():
                raise AssertionError(
                    f"{name} failed to extract text "
                    f"from {resume_path}"
                )

            extracted_text[name] = text

            total_checks += 1

            print(
                f"{name}: PASSED | "
                f"Characters extracted: {len(text)}"
            )

        # --------------------------------------------------
        # Education Section Processing
        # --------------------------------------------------

        print("\nEDUCATION PROCESSING")

        normalized_education = ep.normalize_text(
            extracted_text["Education Parser"]
        )

        education_section = ep.extract_education_section(
            normalized_education
        )

        education_records = ep.parse_education(
            education_section
        )

        print(
            "Education parsing: PASSED | "
            f"Records: {len(education_records)}"
        )

        certification_section = ep.extract_certification_section(
            normalized_education
        )

        certifications = ep.parse_certifications(
            certification_section
        )

        print(
            "Certification parsing: PASSED | "
            f"Records: {len(certifications)}"
        )

        total_checks += 2

        # --------------------------------------------------
        # Experience Section Processing
        # --------------------------------------------------

        print("\nEXPERIENCE PROCESSING")

        normalized_experience = xp.normalize_text(
            extracted_text["Experience Parser"]
        )

        experience_section = xp.extract_experience_section(
            normalized_experience
        )

        print(
            "Experience section extraction: PASSED | "
            f"Lines: {len(experience_section)}"
        )

        parsed_experience = xp.parse_experience(
            experience_section
        )

        print(
            "Experience parsing: PASSED | "
            f"Records: {len(parsed_experience)}"
        )

        total_experience = xp.calculate_total_experience(
            parsed_experience
        )

        print(
            "Total experience calculation: PASSED | "
            f"Result: {total_experience}"
        )

        total_checks += 3

        # --------------------------------------------------
        # Resume Processing Summary
        # --------------------------------------------------

        print("\nRESUME SUMMARY")

        print(
            "Extracted text length:",
            len(extracted_text["Education Parser"])
        )

        print(
            "Education records:",
            len(education_records)
        )

        print(
            "Certification records:",
            len(certifications)
        )

        print(
            "Experience records:",
            len(parsed_experience)
        )

        print(
            "Total experience:",
            total_experience
        )

    # ------------------------------------------------------
    # Final Test Result
    # ------------------------------------------------------

    print("\n========================================")
    print("PDF RUNTIME INTEGRATION TEST PASSED")
    print("========================================")

    print("Total resumes tested:", len(RESUME_FILES))
    print("Total successful checks:", total_checks)

    print("\nALL PDF RUNTIME CHECKS COMPLETED SUCCESSFULLY")


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    test_pdf_runtime()
