
from pathlib import Path
from resume_adapter import ResumeAdapter

PROJECT_ROOT = Path(__file__).resolve().parents[3]

resume_path = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "02_sample_resumes"
    / "excellent"
    / "candidate_001_resume.pdf"
)

adapter = ResumeAdapter()

result = adapter.process_resume(
    "CAND001",
    resume_path
)

print("\nCLEANED TEXT TEST")
print("-" * 50)

print("Status:", result.get("resume_status"))
print("Result keys:", list(result.keys()))

cleaned_text = result.get("cleaned_text")

print("Cleaned text type:", type(cleaned_text).__name__)
print("Cleaned text length:", len(cleaned_text) if cleaned_text else 0)

if cleaned_text:
    print("\nFirst 500 characters:")
    print(cleaned_text[:500])
else:
    print("\nERROR: Cleaned text was not returned.")
