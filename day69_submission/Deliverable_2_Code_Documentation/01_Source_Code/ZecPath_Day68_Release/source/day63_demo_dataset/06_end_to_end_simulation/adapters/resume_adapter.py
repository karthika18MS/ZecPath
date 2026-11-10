import sys
from pathlib import Path
from typing import Any, Dict, Optional


# The adapter lives at:
# day63_demo_dataset/06_end_to_end_simulation/adapters/resume_adapter.py
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from parsers.docx_parser import extract_docx_text
from parsers.entity_detector import extract_entities
from parsers.noisy_text_cleaner import clean_noisy_resume_text
from parsers.pdf_parser import extract_pdf_text


class ResumeAdapter:
    """Adapt existing resume parsers and entity detection to the Day 63 pipeline."""

    def process_resume(
        self,
        candidate_id: str,
        resume_path: Optional[str],
    ) -> Dict[str, Any]:
        result = {
            "candidate_id": candidate_id,
            "resume_status": "NOT_PROCESSED",
            "resume_source": str(resume_path) if resume_path else None,
            "raw_text_characters": 0,
            "cleaned_text_characters": 0,
            # Resume-derived experience stays separate from profile data.
            "resume_experience_years": None,
            "resume_experience_source": None,
            "entities": {},
            "missing_fields": [],
            "warnings": [],
            "error": None,
        }

        if not resume_path:
            result["resume_status"] = "MISSING"
            result["error"] = "No resume path was provided by the dataset loader."
            return result

        path = Path(resume_path)

        if not path.is_file():
            result["resume_status"] = "MISSING"
            result["error"] = f"Resume file does not exist: {path}"
            return result

        try:
            suffix = path.suffix.lower()

            if suffix == ".pdf":
                raw_text = extract_pdf_text(str(path))
            elif suffix == ".docx":
                raw_text = extract_docx_text(str(path))
            else:
                result["resume_status"] = "UNSUPPORTED"
                result["error"] = f"Unsupported resume format: {suffix or '(no extension)'}"
                return result

            if not isinstance(raw_text, str):
                raise TypeError(
                    "The resume parser did not return text. "
                    f"Received {type(raw_text).__name__}."
                )

            result["raw_text_characters"] = len(raw_text)

            cleaned_text = clean_noisy_resume_text(raw_text)
            if not isinstance(cleaned_text, str):
                raise TypeError(
                    "The text cleaner did not return text. "
                    f"Received {type(cleaned_text).__name__}."
                )

            result["cleaned_text_characters"] = len(cleaned_text)
            result["cleaned_text"] = cleaned_text

            entities = extract_entities(cleaned_text)
            if not isinstance(entities, dict):
                raise TypeError(
                    "The entity detector did not return a dictionary. "
                    f"Received {type(entities).__name__}."
                )

            result["entities"] = entities
            result["resume_experience_years"] = entities.get("experience_years")
            if result["resume_experience_years"] is not None:
                result["resume_experience_source"] = "resume_extracted"
            result["resume_status"] = "PROCESSED"

            # Match the field names returned by the existing entity detector.
            for field in ("name", "skills", "degrees", "experience_years"):
                value = entities.get(field)
                if value is None or value == [] or value == "":
                    result["missing_fields"].append(field)

            if entities.get("experience_years") is None:
                result["warnings"].append(
                    "Experience could not be detected. "
                    "This does not necessarily mean the candidate has no experience."
                )

        except Exception as error:
            result["resume_status"] = "ERROR"
            result["error"] = f"{type(error).__name__}: {error}"

        return result


def _print_result(result: Dict[str, Any]) -> None:
    """Print a compact, readable result for one candidate."""
    print(f"\nCandidate: {result['candidate_id']}")
    print(f"Resume Status: {result['resume_status']}")
    print(f"Resume Source: {result['resume_source'] or 'None'}")
    print(f"Raw Text Characters: {result['raw_text_characters']}")
    print(f"Cleaned Text Characters: {result['cleaned_text_characters']}")
    print(f"Missing Fields: {result['missing_fields']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Error: {result['error']}")


if __name__ == "__main__":
    # A single-candidate smoke run, preserving the original direct-run behavior.
    sample_resume = (
        PROJECT_ROOT
        / "day63_demo_dataset"
        / "02_sample_resumes"
        / "excellent"
        / "candidate_001_resume.pdf"
    )

    adapter = ResumeAdapter()
    single_result = adapter.process_resume("CAND001", str(sample_resume))

    print("ZecPath Day 63 Resume Adapter")
    print("=" * 65)
    _print_result(single_result)

    if single_result["resume_status"] == "PROCESSED":
        print("\nDetected Entities:")
        for name, value in single_result["entities"].items():
            print(f"{name}: {value}")
