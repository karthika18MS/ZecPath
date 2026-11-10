"""Apply Day 21 eligibility rules to Day 63 ATS results."""

from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Running this file directly or through unittest discovery can put this
# package directory first, shadowing the package import from the project root.
if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))
DAY63_RESULTS = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "06_end_to_end_simulation"
    / "outputs"
    / "ats_scoring_results.json"
)
RULES_FILE = PROJECT_ROOT / "eligibility_engine" / "eligibility_rules.json"
OUTPUT_DIR = PROJECT_ROOT / "eligibility_engine" / "day63_results"
JOB_ID_EXPERIENCE_RULES = {
    "JD001": {"experience": {"min_years": 2, "max_years": 4}},
    "JD002": {"experience": {"min_years": 1, "max_years": 3}},
    "JD003": {"experience": {"min_years": 3, "max_years": 6}},
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=4, ensure_ascii=False)


def normalize_role(role: str | None) -> str:
    return re.sub(r"[-\s]+", "_", str(role or "").strip().lower())


def get_role_rules(all_rules: dict, role: str | None) -> tuple[dict, str]:
    normalized = normalize_role(role)
    role_rules = all_rules.get("roles", {}).get(normalized)
    if role_rules is not None:
        return copy.deepcopy(role_rules), f"role: {normalized}"
    return copy.deepcopy(all_rules.get("default_rules", {})), "default_rules"


def merge_rule_overrides(base_rules: dict, overrides: dict) -> dict:
    """Recursively apply overrides while preserving unrelated rule checks."""
    merged = copy.deepcopy(base_rules)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_rule_overrides(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def prepare_day63_candidate(
    result: dict, recruiter_rules: dict
) -> tuple[dict, dict]:
    """Adapt Day63 output to the existing engine's input without re-scoring."""
    skill_details = result.get("skill_details") or {}
    mandatory = skill_details.get("required_skills")
    matched = skill_details.get("matched_skills")
    if not isinstance(mandatory, list) or not mandatory:
        raise ValueError("Day63 result has no JD mandatory skill list.")
    if not isinstance(matched, list):
        raise ValueError("Day63 result has no matched skill list.")

    scores = result.get("scores") or {}
    final_score = scores.get("final_ats_score")
    if not isinstance(final_score, (int, float)):
        raise ValueError("Completed Day63 result has no numeric final ATS score.")

    experience = result.get("experience_details") or {}
    adapted = {
        "candidate_id": result.get("candidate_id"),
        "target_role": result.get("target_role"),
        "job_description": result.get("job_id"),
        "scores": {"final_ats_score": final_score},
        "skill_details": {"matched_skills": matched},
        "entity_detection": {
            "experience_years": experience.get("candidate_experience_years")
        },
    }

    # Job ID overrides role experience limits while recursive merge retains
    # ATS, location, availability, and other role/default checks.
    per_candidate_rules = copy.deepcopy(recruiter_rules)
    job_id = result.get("job_id")
    job_overrides = result.get("_job_id_rules", JOB_ID_EXPERIENCE_RULES).get(job_id, {})
    per_candidate_rules = merge_rule_overrides(per_candidate_rules, job_overrides)
    per_candidate_rules["mandatory_skills"] = mandatory
    return adapted, per_candidate_rules


def evaluate_one(result: dict, all_rules: dict) -> dict:
    candidate_id = result.get("candidate_id")
    if result.get("ats_scoring_status") != "COMPLETED":
        return {
            "candidate_id": candidate_id,
            "job_id": result.get("job_id"),
            "ats_scoring_status": result.get("ats_scoring_status"),
            "eligibility_status": "BLOCKED",
            "ats_score": None,
            "reason": "No completed Day63 ATS result; eligibility was not evaluated.",
            "failed_rules": [],
        }

    from eligibility_engine.eligibility_engine import EligibilityDecisionEngine

    role_rules, rule_source = get_role_rules(all_rules, result.get("target_role"))
    result_with_rules = dict(result)
    result_with_rules["_job_id_rules"] = all_rules.get("job_id_rules", {})
    adapted, per_candidate_rules = prepare_day63_candidate(result_with_rules, role_rules)
    if result.get("job_id") in all_rules.get("job_id_rules", {}):
        rule_source += f" + job_id: {result['job_id']}"
    candidate_data = result.get("candidate_information") or {}
    decision = EligibilityDecisionEngine(per_candidate_rules).evaluate(
        day18_result=adapted,
        candidate={
            "location": candidate_data.get("location"),
            "notice_period_days": candidate_data.get("notice_period_days"),
        },
    )
    eligibility = decision.get("eligibility", {})
    return {
        "candidate_id": candidate_id,
        "job_id": result.get("job_id"),
        "target_role": result.get("target_role"),
        "ats_scoring_status": "COMPLETED",
        "eligibility_status": eligibility.get("status", "Unknown"),
        "ats_score": result["scores"]["final_ats_score"],
        "required_skills": result["skill_details"]["required_skills"],
        "matched_skills": result["skill_details"]["matched_skills"],
        "missing_skills": result["skill_details"]["missing_skills"],
        "rule_checks": decision.get("rule_checks", {}),
        "reason": eligibility.get("reason", "No reason available."),
        "failed_rules": eligibility.get("failed_rules", []),
        "rule_source": rule_source,
        "applied_rules": per_candidate_rules,
    }


def main() -> None:
    source = load_json(DAY63_RESULTS)
    rules = load_json(RULES_FILE)
    results = []
    errors = []

    for candidate in source.get("candidate_results", []):
        try:
            item = evaluate_one(candidate, rules)
            results.append(item)
            print(f"{item['candidate_id']}: {item['eligibility_status']}")
        except Exception as error:
            errors.append({
                "candidate_id": candidate.get("candidate_id"),
                "error": f"{type(error).__name__}: {error}",
            })
            results.append({
                "candidate_id": candidate.get("candidate_id"),
                "job_id": candidate.get("job_id"),
                "eligibility_status": "ERROR",
                "error": f"{type(error).__name__}: {error}",
            })

    summary = {
        "engine": "ZecPath Day 63 eligibility using the existing Day 21 decision engine",
        "source_file": str(DAY63_RESULTS),
        "generated_at": datetime.now().astimezone().isoformat(),
        "total_candidates": len(results),
        "eligible": sum(x.get("eligibility_status") == "Eligible" for x in results),
        "review": sum(x.get("eligibility_status") == "Review" for x in results),
        "rejected": sum(x.get("eligibility_status") == "Rejected" for x in results),
        "blocked": sum(x.get("eligibility_status") == "BLOCKED" for x in results),
        "errors": len(errors),
        "candidate_results": results,
        "errors_detail": errors,
        "notes": [
            "Day63 ATS scores and Day18 weights are consumed without recalculation.",
            "Each candidate's mandatory skill list comes from their Day63 JD skill_details.",
            "Missing mandatory skills retain the existing Day21 hard-rejection behavior.",
            "Blocked Day63 candidates remain blocked and receive no eligibility score.",
        ],
    }
    output_path = OUTPUT_DIR / "day63_eligibility_summary.json"
    save_json(summary, output_path)
    print(f"\nEligibility summary: {{'total': {len(results)}, 'eligible': {summary['eligible']}, 'review': {summary['review']}, 'rejected': {summary['rejected']}, 'blocked': {summary['blocked']}, 'errors': {summary['errors']}}}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
