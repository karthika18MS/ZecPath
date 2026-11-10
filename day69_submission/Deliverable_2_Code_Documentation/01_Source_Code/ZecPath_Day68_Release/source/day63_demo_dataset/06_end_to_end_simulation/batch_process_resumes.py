import json
import sys
from pathlib import Path
from typing import Any, Dict, List


# This script lives directly inside 06_end_to_end_simulation.
SIMULATION_ROOT = Path(__file__).resolve().parent
DATASET_ROOT = SIMULATION_ROOT.parent
PROJECT_ROOT = DATASET_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))


from adapters.resume_adapter import ResumeAdapter
from loaders.dataset_loader import DatasetLoader


def process_all_resumes() -> Dict[str, Any]:
    loader = DatasetLoader(DATASET_ROOT)
    dataset = loader.load_dataset()
    adapter = ResumeAdapter()

    results: List[Dict[str, Any]] = []

    for candidate in dataset["candidates"]:
        candidate_id = candidate.get("candidate_id")

        # Preserve invalid profile information in the consolidated output.
        if candidate.get("load_status") != "LOADED" or not candidate_id:
            results.append({
                "candidate_id": candidate_id,
                "resume_status": "INVALID_PROFILE",
                "resume_source": None,
                "raw_text_characters": 0,
                "cleaned_text_characters": 0,
                "entities": {},
                "missing_fields": [],
                "warnings": [],
                "error": candidate.get("load_error", "Candidate profile could not be loaded."),
                "profile_file": candidate.get("profile_file"),
            })
            continue

        results.append(
            adapter.process_resume(
                candidate_id=candidate_id,
                resume_path=candidate.get("resume"),
            )
        )

    counts: Dict[str, int] = {}
    for result in results:
        status = result["resume_status"]
        counts[status] = counts.get(status, 0) + 1

    return {
        "dataset_name": dataset.get("dataset_name", DATASET_ROOT.name),
        "total_candidates": dataset.get("total_candidates", len(results)),
        "processed_count": counts.get("PROCESSED", 0),
        "missing_count": counts.get("MISSING", 0),
        "error_count": counts.get("ERROR", 0),
        "status_counts": counts,
        "results": results,
    }


def main() -> None:
    consolidated = process_all_resumes()

    print("=" * 72)
    print("ZecPath Day 63 — Batch Resume Processing")
    print("=" * 72)
    print(f"Dataset: {consolidated['dataset_name']}")
    print(f"Total Candidates: {consolidated['total_candidates']}")
    print(f"Processed: {consolidated['processed_count']}")
    print(f"Missing: {consolidated['missing_count']}")
    print(f"Errors: {consolidated['error_count']}")

    for result in consolidated["results"]:
        print(
            f"{result['candidate_id']}: "
            f"{result['resume_status']}"
        )

    output_dir = SIMULATION_ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "resume_processing_results.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(consolidated, file, indent=2, ensure_ascii=False)

    print("-" * 72)
    print(f"Saved consolidated result: {output_file}")


if __name__ == "__main__":
    main()