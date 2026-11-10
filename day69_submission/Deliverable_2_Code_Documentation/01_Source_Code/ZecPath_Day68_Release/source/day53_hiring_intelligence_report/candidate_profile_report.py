
"""
ZecPath Day 53 - Full Candidate AI Profile Report

Reads the Day 53 Hiring Intelligence Report and generates
a recruiter-friendly candidate profile.

Features:
- Candidate and job information
- ATS, screening, HR, technical, and machine-test summaries
- Evidence-based strengths and improvement areas
- Behavioral observations
- Risk indicators and data-quality warnings
- Final recommendation and explainability
- Demo-data transparency

Scores are copied from existing reports, not recalculated.
Missing values are reported as unavailable.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_FILE = RESULTS_DIR / "hiring_intelligence_report.json"
OUTPUT_FILE = RESULTS_DIR / "candidate_ai_profile.json"


def load_json(path):
    """Load and validate a JSON object."""
    if not path.exists():
        raise FileNotFoundError(
            f"Required report not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object in {path.name}."
        )

    return data


def get_section(report, name):
    """Return a section's source data when available."""
    sections = report.get("evaluation_sections", {})
    if not isinstance(sections, dict):
        return None

    section = sections.get(name, {})
    if not isinstance(section, dict):
        return None

    if section.get("status") != "AVAILABLE":
        return None

    data = section.get("data")
    return data if isinstance(data, dict) else None


def get_number(data, *keys):
    """Return the first available numeric value for the given keys."""
    if not isinstance(data, dict):
        return None

    for key in keys:
        value = data.get(key)

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)

    return None


def get_nested(data, *keys):
    """Safely read a nested dictionary path."""
    current = data

    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)

    return current


def first_available(*values):
    """Return the first value that is not None."""
    for value in values:
        if value is not None:
            return value
    return None


def add_score(scores, name, value, source, data_type=None):
    """Add an existing score without recalculating it."""
    if value is None:
        scores[name] = {
            "score": None,
            "status": "UNAVAILABLE",
            "source": source,
        }
        return

    scores[name] = {
        "score": round(value, 2),
        "status": "AVAILABLE",
        "source": source,
    }

    if data_type:
        scores[name]["data_type"] = data_type


def safe_list(value):
    """Return a list, or an empty list for invalid/missing data."""
    return value if isinstance(value, list) else []


def build_profile(report):
    """Build the full candidate profile from the combined report."""

    candidate_info = report.get("candidate_information", {})
    if not isinstance(candidate_info, dict):
        candidate_info = {}

    # Load source reports.
    ats = get_section(report, "ats")
    screening = get_section(report, "screening")
    hr = get_section(report, "hr_interview")
    technical = get_section(report, "technical_performance")
    machine = get_section(report, "machine_test")
    unified = get_section(report, "unified_candidate_score")
    recommendation = get_section(report, "final_recommendation")

    # Candidate details.
    candidate_id = candidate_info.get("candidate_id")
    job_id = candidate_info.get("job_id")

    role = (
        first_available(
            get_nested(ats, "target_role"),
            get_nested(ats, "job_role"),
            get_nested(ats, "job_title"),
        )
        or "Backend Developer"
    )

    # ATS information.
    ats_scores = get_nested(ats, "scores") or {}
    skill_details = get_nested(ats, "skill_details") or {}
    experience_details = get_nested(ats, "experience_details") or {}
    education_details = get_nested(ats, "education_details") or {}

    required_skills = safe_list(
        skill_details.get("required_skills")
    )
    matched_skills = safe_list(
        skill_details.get("matched_skills")
    )
    missing_skills = safe_list(
        skill_details.get("missing_skills")
    )

    # Screening information.
    screening_summary = (
        get_nested(screening, "screening_summary") or {}
    )

    # HR interview information.
    hr_score = get_number(
        hr,
        "final_hr_interview_score",
        "hr_interview_score",
        "final_score",
    )

    if hr_score is None:
        hr_score = get_number(
            get_nested(hr, "interview_summary"),
            "final_score",
            "final_hr_interview_score",
        )

    hr_parameters = (
        get_nested(hr, "parameter_averages")
        or get_nested(hr, "parameter_scores")
        or {}
    )

    # Technical assessment.
    technical_summary = (
        get_nested(technical, "evaluation_summary") or {}
    )

    technical_score = get_number(
        technical_summary,
        "overall_technical_score",
        "technical_score",
        "final_score",
    )

    technical_type = (
        technical.get("data_type", "NOT_PROVIDED")
        if technical else None
    )

    # Machine-test assessment.
    machine_score = get_number(
        machine,
        "machine_test_score",
        "overall_score",
        "final_score",
    )

    machine_type = (
        machine.get("data_type", "NOT_PROVIDED")
        if machine else None
    )

    # Unified candidate score.
    overall_evaluation = (
        get_nested(unified, "overall_evaluation") or {}
    )

    unified_demo_rounds = safe_list(
        overall_evaluation.get("demo_rounds")
    )

    # Correctly read the Day 52 recommendation source.
    # The source report stores decision fields at the top level.
    decision_data = recommendation if recommendation else {}

    if not decision_data:
        # Fallback to the top-level summary in the combined report.
        combined_recommendation = report.get(
            "final_recommendation", {}
        )
        if isinstance(combined_recommendation, dict):
            decision_data = combined_recommendation

    # Read Day 52 nested objects.
    confidence_data = decision_data.get("confidence", {})
    if not isinstance(confidence_data, dict):
        confidence_data = {}

    risk_assessment = decision_data.get("risk_assessment", {})
    if not isinstance(risk_assessment, dict):
        risk_assessment = {}

    explanation = decision_data.get("explanation", {})
    if not isinstance(explanation, dict):
        explanation = {}

    explainability = decision_data.get("explainability", {})
    if not isinstance(explainability, dict):
        explainability = {}

    # Decision and reasons can be stored in either explanation object.
    final_decision = first_available(
        decision_data.get("decision"),
        decision_data.get("final_decision"),
        explainability.get("final_decision"),
    )

    reasons = first_available(
        explanation.get("reasons"),
        explanation.get("decision_reasons"),
        explainability.get("decision_reasons"),
        explainability.get("reasons"),
        decision_data.get("decision_reasons"),
        decision_data.get("reasons"),
    )
    reasons = safe_list(reasons)

    # Confidence can be a nested object or a direct value.
    confidence_score = first_available(
        confidence_data.get("confidence_score"),
        decision_data.get("confidence_score"),
    )

    confidence_interpretation = first_available(
        confidence_data.get("interpretation"),
        confidence_data.get("confidence_interpretation"),
        decision_data.get("confidence_interpretation"),
        "Evaluation-data completeness indicator, not a probability "
        "of hiring success.",
    )

    # Read eligibility from the actual source fields.
    eligibility_status = first_available(
        explanation.get("eligibility_status"),
        decision_data.get("eligibility_status"),
        risk_assessment.get("eligibility_status"),
        "NOT_PROVIDED",
    )

    # Demo rounds can be recorded in the decision source or unified report.
    demo_rounds = first_available(
        risk_assessment.get("demo_data_rounds"),
        decision_data.get("demo_data_rounds"),
    )
    demo_rounds = safe_list(demo_rounds)

    if not demo_rounds:
        demo_rounds = unified_demo_rounds

    # Explicit risk flags.
    risk_flags = first_available(
        risk_assessment.get("risk_flags"),
        decision_data.get("risk_flags"),
        [],
    )
    risk_flags = safe_list(risk_flags)

    human_review_required = first_available(
        decision_data.get("human_review_required"),
        risk_assessment.get("human_review_required"),
        risk_assessment.get("requires_human_review"),
    )

    automated_action = first_available(
        decision_data.get("automated_hiring_action_taken"),
        False,
    )

    decision_policy = first_available(
        explanation.get("decision_policy"),
        explainability.get("decision_policy"),
        decision_data.get("decision_policy"),
    )

    # Scores: preserve values from their existing source files.
    scores = {}

    add_score(
        scores,
        "ats",
        get_number(ats_scores, "final_ats_score", "ats_score"),
        "Day 18 ATS report",
    )

    add_score(
        scores,
        "screening",
        get_number(
            screening_summary,
            "final_screening_score",
            "screening_score",
        ),
        "Day 32 screening report",
    )

    add_score(
        scores,
        "hr_interview",
        hr_score,
        "Day 37 HR interview report",
    )

    add_score(
        scores,
        "technical_interview",
        technical_score,
        "Day 47 technical evaluation",
        technical_type,
    )

    add_score(
        scores,
        "machine_test",
        machine_score,
        "Day 50 machine-test report",
        machine_type,
    )

    add_score(
        scores,
        "hiring_fit",
        get_number(
            overall_evaluation,
            "hiring_fit_score",
            "overall_score",
        ),
        "Day 51 unified candidate score",
        unified.get("report_type") if unified else None,
    )

    # Evidence-supported strengths.
    strengths = []
    improvement_areas = []

    skill_score = get_number(
        ats_scores, "skill_matching", "skill_match_score"
    )

    if skill_score is not None and skill_score >= 80:
        strengths.append({
            "area": "Skill matching",
            "evidence": (
                f"ATS skill-matching score: {skill_score:.2f}/100."
            ),
        })

    if required_skills and matched_skills:
        strengths.append({
            "area": "Matched technical skills",
            "evidence": (
                f"{len(matched_skills)} of {len(required_skills)} "
                "listed required skills were matched by the ATS source."
            ),
        })

    if missing_skills:
        improvement_areas.append({
            "area": "Skills not matched by ATS",
            "evidence": missing_skills,
            "note": (
                "Confirm relevance to the job and verify the resume "
                "before interpreting a missing match as a missing skill."
            ),
        })

    experience_score = get_number(experience_details, "score")

    if experience_score is not None and experience_score >= 80:
        strengths.append({
            "area": "Experience alignment",
            "evidence": (
                f"Source-reported experience alignment: "
                f"{experience_score:.2f}/100."
            ),
        })

    education_score = get_number(education_details, "score")

    if education_score is not None and education_score >= 80:
        strengths.append({
            "area": "Education alignment",
            "evidence": (
                f"Source-reported education alignment: "
                f"{education_score:.2f}/100."
            ),
        })

    communication_score = get_number(
        screening_summary,
        "communication_strength",
        "communication_score",
    )

    if communication_score is not None and communication_score >= 80:
        strengths.append({
            "area": "Screening communication indicators",
            "evidence": (
                f"Source-reported communication indicator: "
                f"{communication_score:.2f}/100."
            ),
        })

    if technical_score is not None:
        if technical_score >= 80:
            strengths.append({
                "area": "Technical assessment",
                "evidence": (
                    f"Source-reported technical score: "
                    f"{technical_score:.2f}/100."
                ),
                "data_type": technical_type,
            })
        else:
            improvement_areas.append({
                "area": "Technical assessment",
                "evidence": (
                    f"Source-reported technical score: "
                    f"{technical_score:.2f}/100."
                ),
                "note": (
                    "Review the scored answers and assessment rubric "
                    "to identify specific development needs."
                ),
                "data_type": technical_type,
            })

    # Behavioral observations: preserve source signals without
    # inferring character, integrity, or job suitability.
    behavioral_observations = []

    responses = safe_list(
        screening.get("responses") if screening else []
    )

    for response in responses:
        if not isinstance(response, dict):
            continue

        indicators = response.get("behavioral_indicators", {})
        if not isinstance(indicators, dict):
            continue

        signals = indicators.get("behavioral_signals", {})
        if not isinstance(signals, dict):
            continue

        question = response.get("question", {})
        if not isinstance(question, dict):
            question = {}

        behavioral_observations.append({
            "question_id": question.get("question_id"),
            "question_category": question.get("category"),
            "hesitation_count": signals.get("hesitation_count"),
            "uncertainty_count": signals.get("uncertainty_count"),
            "contradiction_detected": signals.get(
                "contradiction_detected"
            ),
            "pace": signals.get("pace"),
            "interpretation_limit": (
                "These are recorded response indicators, not proof "
                "of character, honesty, or job performance."
            ),
        })

    # Risk indicators distinguish demo data and missing information
    # from explicit risk flags.
    risk_indicators = []

    for flag in risk_flags:
        risk_indicators.append({
            "type": "SOURCE_REPORTED_RISK",
            "description": str(flag),
            "status": "REQUIRES_REVIEW",
        })

    for round_name in demo_rounds:
        risk_indicators.append({
            "type": "DEMO_DATA",
            "description": (
                f"{round_name} is marked as demo data in the "
                "evaluation source."
            ),
            "status": "NOT_VERIFIED",
        })

    if str(eligibility_status).upper() in {
        "NOT_PROVIDED",
        "NOT_PROVIDED".upper(),
        "NOT ASSESSED",
    }:
        risk_indicators.append({
            "type": "MISSING_INFORMATION",
            "description": "Eligibility status was not provided.",
            "status": "REQUIRES_REVIEW",
        })

    # Structured explainability.
    rules_applied = first_available(
        explainability.get("rules_applied"),
        explanation.get("rules_applied"),
        [],
    )

    score_thresholds = first_available(
        explainability.get("score_thresholds"),
        explanation.get("score_thresholds"),
        {},
    )

    # Assemble the final profile.
    profile = {
        "report_title": "ZecPath Full Candidate AI Profile",
        "report_version": "1.1",
        "report_type": report.get("report_type", "DEMO_ONLY"),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "candidate_information": {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "target_role": role,
        },

        "executive_summary": {
            "hiring_fit_score": first_available(
                get_number(overall_evaluation, "hiring_fit_score"),
                get_number(decision_data, "hiring_fit_score"),
            ),
            "final_recommendation": final_decision,
            "confidence_score": confidence_score,
            "confidence_interpretation": confidence_interpretation,
            "human_review_required": human_review_required,
            "automated_hiring_action_taken": automated_action,
        },

        "performance_summary": scores,

        "ats_profile": {
            "matching_status": (
                ats.get("matching_status") if ats else None
            ),
            "shortlisting_status": (
                ats.get("shortlisting_status") if ats else None
            ),
            "required_skills": required_skills,
            "matched_skills": matched_skills,
            "missing_skill_matches": missing_skills,
            "experience_details": experience_details,
            "education_details": education_details,
        },

        "screening_insights": screening_summary,

        "hr_insights": {
            "parameter_averages": hr_parameters,
            "total_questions": (
                hr.get("total_questions") if hr else None
            ),
        },

        "technical_performance": {
            "evaluation_summary": technical_summary,
            "data_type": technical_type,
        },

        "machine_test_performance": {
            "machine_test_score": machine_score,
            "test_results": (
                machine.get("test_results") if machine else None
            ),
            "data_type": machine_type,
        },

        "strengths": strengths,
        "improvement_areas": improvement_areas,

        "behavioral_observations": {
            "source": "Day 32 screening behavioral indicators",
            "observations": behavioral_observations,
            "interpretation_note": (
                "Do not infer personality, integrity, or suitability "
                "from hesitation, speech pace, sentiment, or confidence "
                "signals alone."
            ),
        },

        "risk_indicators": {
            "explicit_risk_flags": risk_flags,
            "indicators": risk_indicators,
            "eligibility_status": eligibility_status,
            "demo_rounds": demo_rounds,
            "behavior": risk_assessment.get("behavior", {}),
            "integrity": risk_assessment.get("integrity", {}),
        },

        "final_recommendation_details": {
            "decision": final_decision,
            "reasons": reasons,
            "decision_policy": decision_policy,
            "score_based_decision": first_available(
                explainability.get("score_based_decision"),
                explanation.get("score_based_decision"),
            ),
            "rules_applied": rules_applied,
            "score_thresholds": score_thresholds,
            "explainability": explainability,
        },

        "report_quality": {
            "source_report_status": report.get("report_status"),
            "all_configured_sources_available": (
                report.get("source_summary", {}).get(
                    "available_sources"
                )
                == report.get("source_summary", {}).get(
                    "total_sources"
                )
            ),
            "demo_data_present": bool(demo_rounds),
            "verified_hiring_decision": False,
            "limitations": [
                "Scores are copied from their source reports.",
                "Demo data is not verified assessment evidence.",
                "Source availability does not prove independent verification.",
                "Behavioral observations are not proof of character or integrity.",
                "Missing information is not treated as evidence of poor performance.",
                "The profile supports human review and does not itself make "
                "an automated hiring decision.",
            ],
        },
    }

    return profile


def main():
    try:
        source_report = load_json(INPUT_FILE)
        profile = build_profile(source_report)

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                profile,
                file,
                indent=4,
                ensure_ascii=False,
            )

        summary = profile["executive_summary"]

        print("=" * 60)
        print("ZecPath Day 53 - Full Candidate AI Profile Report")
        print("=" * 60)
        print(
            "Candidate ID:",
            profile["candidate_information"]["candidate_id"],
        )
        print(
            "Target role:",
            profile["candidate_information"]["target_role"],
        )
        print(
            "Hiring fit score:",
            summary["hiring_fit_score"],
        )
        print(
            "Final recommendation:",
            summary["final_recommendation"] or "NOT PROVIDED",
        )
        print(
            "Confidence score:",
            summary["confidence_score"]
            if summary["confidence_score"] is not None
            else "NOT PROVIDED",
        )
        print(
            "Human review required:",
            summary["human_review_required"]
            if summary["human_review_required"] is not None
            else "NOT PROVIDED",
        )
        print(
            "Strengths identified:",
            len(profile["strengths"]),
        )
        print(
            "Improvement areas identified:",
            len(profile["improvement_areas"]),
        )
        print(
            "Risk indicators:",
            len(profile["risk_indicators"]["indicators"]),
        )
        print("Output saved to:", OUTPUT_FILE)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
        OSError,
    ) as error:
        print("ERROR:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
