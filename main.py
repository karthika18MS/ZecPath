from parsers.extractor import extract_resume
from parsers.save_output import save_cleaned_text
from utils.logger import logger

# Path to the resume file
resume_path = "data/resumes/sample_resume.pdf"


def main():
    try:
        logger.info("========== Resume Extraction Started ==========")

        # Extract and clean resume text
        cleaned_text = extract_resume(resume_path)

        print("\n========== Extracted Resume ==========\n")
        print(cleaned_text)

        # Save cleaned resume text
        save_cleaned_text("resume.txt", cleaned_text)

        logger.info("Resume Extraction Completed Successfully")

        print("\nResume Extraction Completed Successfully.")

    except Exception as error:
        logger.error(f"Error occurred: {error}")
        print(f"\nError: {error}")

    finally:
        logger.info("========== Resume Extraction Finished ==========")


if __name__ == "__main__":
    main()