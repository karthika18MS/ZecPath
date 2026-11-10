"""Score READY_FOR_ATS Day 63 records with the existing Day 18 components."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DAY63_ROOT = PROJECT_ROOT / "day63_demo_dataset" / "06_end_to_end_simulation"
INPUT_FILE = DAY63_ROOT / "outputs" / "ats_input_results.json"
OUTPUT_FILE = DAY63_ROOT / "outputs" / "ats_scoring_results.json"
DAY17_SKILL_SCRIPT = PROJECT_ROOT / "day17_testing" / "day17_skill_matching.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day18_optimization import optimized_ats_engine as engine


# Explicit spelling aliases only. A skill is counted only when one of these
# literal forms appears in the cleaned resume text.
SKILL_ALIASES = {
    "react.js": ("react.js", "reactjs", "react"),
    "node.js": ("node.js", "nodejs", "node"),
    "express.js": ("express.js", "expressjs", "express"),
    "mongodb": ("mongodb", "mongo db"),
    "javascript": ("javascript", "java script"),
    "rest api development": ("rest api development", "rest apis", "rest api"),
    "github": ("github",),
    "html5": ("html5", "html 5"),
    "css3": ("css3", "css 3"),
}


def _skill_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def _contains_skill(text: str, skill: str) -> bool:
    key = _skill_key(skill)
    aliases = SKILL_ALIASES.get(key, (key,))
    folded_text = text.casefold()
    for alias in aliases:
        # Treat punctuation in known aliases literally; allow whitespace
        # variation, and require token boundaries to avoid partial matches.
        pieces = [re.escape(piece) for piece in re.split(r"\s+", alias)]
        pattern = r"(?<![\w])" + r"\s+".join(pieces) + r"(?![\w])"
        if re.search(pattern, folded_text):
            return True
    return False


def evaluate_jd_skills(jd: dict, resume_text: str) -> dict:
    """Evaluate every structured JD skill against literal resume evidence."""
    mandatory = jd.get("mandatory_skills")
    preferred = jd.get("preferred_skills")
    if not isinstance(mandatory, list) or not mandatory:
        raise ValueError("Job information must contain a non-empty mandatory_skills list.")
    if not isinstance(preferred, list):
        raise ValueError("Job information must contain a preferred_skills list.")
    if not all(isinstance(skill, str) and skill.strip() for skill in mandatory + preferred):
        raise ValueError("Mandatory and preferred skills must be non-empty strings.")

    def evaluate(skills: list[str]) -> tuple[list[str], list[str]]:
        matched = [skill for skill in skills if _contains_skill(resume_text, skill)]
        missing = [skill for skill in skills if skill not in matched]
        return matched, missing

    matched_mandatory, missing_mandatory = evaluate(mandatory)
    matched_preferred, missing_preferred = evaluate(preferred)
    score = round(100.0 * len(matched_mandatory) / len(mandatory), 2)
    return {
        "score": score,
        "required_skills": mandatory,
        "matched_skills": matched_mandatory,
        "missing_skills": missing_mandatory,
        "total_required_skills": len(mandatory),
        "total_matched_skills": len(matched_mandatory),
        "preferred_skills": preferred,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "total_preferred_skills": len(preferred),
        "total_matched_preferred_skills": len(matched_preferred),
        "source": "Day 63 JD skill adapter (literal resume evidence; Day 17 retained for role-specific detail)",
    }


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=4, ensure_ascii=False)


def run_day17_skill_match(candidate: dict, scratch_root: Path) -> dict:
    """Run the existing Day 17 role-aware matcher against staged Day 63 text."""
    candidate_id = candidate["candidate_id"]
    target_role = candidate["candidate_information"].get("target_role") or ""
    resume_text = candidate["resume_information"].get("cleaned_text")
    jd = candidate["job_information"]
    jd_source = jd.get("jd_source")

    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("The ready candidate has no cleaned resume text.")
    if not jd_source or not Path(jd_source).is_file():
        raise FileNotFoundError(f"Job description source not found: {jd_source}")

    job_description = Path(jd_source).read_text(encoding="utf-8")
    scratch_id = f"day63_{candidate_id}"
    result_dir = scratch_root / "day17_testing" / "results" / scratch_id
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "cleaned_resume.txt").write_text(resume_text, encoding="utf-8")
    (result_dir / "job_description.txt").write_text(job_description, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(DAY17_SKILL_SCRIPT), scratch_id, target_role],
        cwd=scratch_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        raise RuntimeError((completed.stdout + "\n" + completed.stderr).strip())

    raw_result = load_json(result_dir / "day17_skill_match.json")
    return engine.convert_day17_skill_result(raw_result), job_description


def score_candidate(candidate: dict, scratch_root: Path) -> dict:
    day17_skill_result, job_description = run_day17_skill_match(candidate, scratch_root)
    candidate_info = candidate["candidate_information"]
    resume_info = candidate["resume_information"]
    resume_text = resume_info["cleaned_text"]
    # Day 17 remains in the flow, but its inferred/selected skill universe is
    # not authoritative for Day 63 scoring. Use all structured JD requirements.
    skill_result = evaluate_jd_skills(candidate["job_information"], resume_text)
    skill_result["day17_matcher_details"] = day17_skill_result
    entities = resume_info.get("extracted_entities") or {}

    # Keep profile claims and resume evidence separate. When resume extraction
    # is unavailable, use a valid profile value as an explicit scoring fallback.
    profile_experience_years = candidate_info.get("experience_years")
    resume_experience_years = entities.get("experience_years")
    scoring_entities = dict(entities)
    scoring_experience_years = resume_experience_years
    scoring_experience_source = (
        "resume_extracted" if resume_experience_years is not None else None
    )

    if (
        scoring_experience_years is None
        and isinstance(profile_experience_years, (int, float))
        and not isinstance(profile_experience_years, bool)
        and profile_experience_years >= 0
    ):
        scoring_experience_years = profile_experience_years
        scoring_experience_source = "candidate_profile_fallback"
        scoring_entities["experience_years"] = profile_experience_years

    experience = engine.calculate_experience_match(scoring_entities, job_description)
    education = engine.calculate_education_match(entities, resume_text, job_description)
    semantic = engine.calculate_semantic_similarity(resume_text, job_description)
    final = engine.calculate_final_score(
        skill_result["score"],
        experience["score"],
        education["score"],
        semantic["score"],
    )

    final_score = final["final_score"]

    # Evaluate mandatory skills independently of the weighted ATS score.
    mandatory_skill_check = engine.evaluate_mandatory_skill_check(
        skill_result
    )

    # Preserve the existing score-based decision when mandatory skills pass.
    shortlisting_status = engine.get_shortlisting_status(final_score)
    recommendation = engine.get_recommendation(final_score)

    # Missing any mandatory skill prevents automatic shortlisting.
    if not mandatory_skill_check["passed"]:
        shortlisting_status = "Not Shortlisted"
        recommendation = "Not Recommended"

    return {
        "candidate_id": candidate["candidate_id"],
        "job_id": candidate.get("job_id"),
        "target_role": candidate_info.get("target_role"),
        "input_status": candidate.get("input_status"),
        "experience_provenance": {
            "profile_experience_years": profile_experience_years,
            "profile_experience_source": (
                "candidate_profile"
                if profile_experience_years is not None
                else None
            ),
            "resume_experience_years": resume_experience_years,
            "resume_experience_source": (
                "resume_extracted"
                if resume_experience_years is not None
                else None
            ),
            "scoring_value": scoring_experience_years,
            "scoring_source": scoring_experience_source,
        },
        "ats_scoring_status": "COMPLETED",
        "engine": "ZecPath Day 18 Optimized ATS Engine",
        "scores": {
            "skill_matching": skill_result["score"],
            "experience_relevance": experience["score"],
            "education_alignment": education["score"],
            "semantic_similarity": semantic["score"],
            "final_ats_score": final_score,
        },
        "weights": {
            "skill_matching": engine.SKILL_WEIGHT,
            "experience_relevance": engine.EXPERIENCE_WEIGHT,
            "education_alignment": engine.EDUCATION_WEIGHT,
            "semantic_similarity": engine.SEMANTIC_WEIGHT,
        },
        "contributions": final,
        "matching_status": engine.get_matching_status(final_score),
        "shortlisting_status": shortlisting_status,
        "recommendation": recommendation,
        "mandatory_skill_check": mandatory_skill_check,
        "skill_details": skill_result,
        "experience_details": experience,
        "education_details": education,
        "semantic_details": semantic,
        "semantic_input": "Day 63 cleaned resume text",
    }


    return {
        "candidate_id": candidate["candidate_id"],
        "job_id": candidate.get("job_id"),
        "target_role": candidate_info.get("target_role"),
        "input_status": candidate.get("input_status"),
        "experience_provenance": {
            "profile_experience_years": profile_experience_years,
            "profile_experience_source": "candidate_profile" if profile_experience_years is not None else None,
            "resume_experience_years": resume_experience_years,
            "resume_experience_source": "resume_extracted" if resume_experience_years is not None else None,
            "scoring_value": scoring_experience_years,
            "scoring_source": scoring_experience_source,
        },
        "ats_scoring_status": "COMPLETED",
        "engine": "ZecPath Day 18 Optimized ATS Engine",
        "scores": {
            "skill_matching": skill_result["score"],
            "experience_relevance": experience["score"],
            "education_alignment": education["score"],
            "semantic_similarity": semantic["score"],
            "final_ats_score": final_score,
        },
        "weights": {
            "skill_matching": engine.SKILL_WEIGHT,
            "experience_relevance": engine.EXPERIENCE_WEIGHT,
            "education_alignment": engine.EDUCATION_WEIGHT,
            "semantic_similarity": engine.SEMANTIC_WEIGHT,
        },
        "contributions": final,
        "matching_status": engine.get_matching_status(final_score),
        "shortlisting_status": engine.get_shortlisting_status(final_score),
        "recommendation": engine.get_recommendation(final_score),
        "skill_details": skill_result,
        "experience_details": experience,
        "education_details": education,
        "semantic_details": semantic,
        "semantic_input": "Day 63 cleaned resume text",
    }


def main() -> None:
    source = load_json(INPUT_FILE)
    results = []
    errors = []

    with tempfile.TemporaryDirectory(prefix="zecpath_day63_ats_") as scratch:
        scratch_root = Path(scratch)
        for candidate in source.get("candidate_results", []):
            if candidate.get("input_status") != "READY_FOR_ATS":
                results.append({
                    "candidate_id": candidate.get("candidate_id"),
                    "job_id": candidate.get("job_id"),
                    "input_status": candidate.get("input_status"),
                    "ats_scoring_status": "BLOCKED",
                    "scores": None,
                    "reason": "Candidate is not READY_FOR_ATS; no score was calculated.",
                })
                continue

            try:
                results.append(score_candidate(candidate, scratch_root))
                print(f"Scored {candidate['candidate_id']}")
            except Exception as error:
                errors.append({
                    "candidate_id": candidate.get("candidate_id"),
                    "error": f"{type(error).__name__}: {error}",
                })
                results.append({
                    "candidate_id": candidate.get("candidate_id"),
                    "job_id": candidate.get("job_id"),
                    "input_status": candidate.get("input_status"),
                    "ats_scoring_status": "ERROR",
                    "scores": None,
                    "error": f"{type(error).__name__}: {error}",
                })

    output = {
        "engine": "ZecPath Day 63 ATS Scoring Pipeline using Day 18 Optimized ATS Engine",
        "pipeline_status": "COMPLETED_WITH_ERRORS" if errors else "COMPLETED",
        "source_file": str(INPUT_FILE),
        "generated_at": datetime.now().astimezone().isoformat(),
        "summary": {
            "total_candidates": len(results),
            "scored": sum(item["ats_scoring_status"] == "COMPLETED" for item in results),
            "blocked": sum(item["ats_scoring_status"] == "BLOCKED" for item in results),
            "errors": len(errors),
        },
        "candidate_results": results,
        "errors": errors,
        "notes": [
            "The existing Day 17 role-specific skill matcher and Day 18 component scoring functions are reused.",
            "Semantic similarity uses the Day 63 cleaned resume text because no validated Day 17 resume artifact exists for these candidate IDs.",
            "The original ats_input_results.json is not modified; blocked candidates receive no scores.",
        ],
    }
    save_json(output, OUTPUT_FILE)
    print(f"\nScoring summary: {output['summary']}")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
