import pytest

from parsers.extractor import extract_resume


def test_pdf_parser():
    """
    Test PDF resume extraction.
    """
    text = extract_resume("data/resumes/sample_resume.pdf")
    assert len(text) > 0


def test_docx_parser():
    """
    Test DOCX resume extraction.
    """
    text = extract_resume("data/resumes/sample_resume.docx")
    assert len(text) > 0


def test_pdf_returns_string():
    """
    Ensure PDF parser returns a string.
    """
    text = extract_resume("data/resumes/sample_resume.pdf")
    assert isinstance(text, str)


def test_docx_returns_string():
    """
    Ensure DOCX parser returns a string.
    """
    text = extract_resume("data/resumes/sample_resume.docx")
    assert isinstance(text, str)