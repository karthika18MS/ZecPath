import os

from parsers.pdf_parser import extract_pdf_text
from parsers.docx_parser import extract_docx_text
from parsers.text_cleaner import clean_text
from utils.logger import logger


def extract_resume(file_path):
    """
    Extracts and cleans text from PDF or DOCX resumes.
    """

    logger.info(f"Reading Resume: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        logger.info("PDF Resume Detected")
        text = extract_pdf_text(file_path)

    elif extension == ".docx":
        logger.info("DOCX Resume Detected")
        text = extract_docx_text(file_path)

    else:
        logger.error(f"Unsupported File Format: {extension}")
        raise ValueError(
            "Unsupported File Format. Only PDF and DOCX files are supported."
        )

    logger.info("Cleaning Resume Text")

    cleaned_text = clean_text(text)

    logger.info("Resume Text Cleaned Successfully")

    return cleaned_text