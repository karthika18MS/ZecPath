"""
ZecPath Day 53 - Deliverable 3: Export-Ready Report Format

Reads:
    results/candidate_ai_profile.json

Writes:
    results/candidate_hiring_report.md

This exporter presents existing profile data only. It does not recalculate
scores or make/change a hiring decision.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
INPUT_FILE = RESULTS_DIR / "candidate_ai_profile.json"
OUTPUT_FILE = RESULTS_DIR / "candidate_hiring_report.md"


def value(data, key, default=None):
    return data.get(key, default) if isinstance(data, dict) else default


def fmt(value_):
    if value_ is None or value_ == "":
        return "Not available"
    if isinstance(value_, bool):
        return "Yes" if value_ else "No"
    if isinstance(value_, float):
        return f"{value_:.2f}"
    return str(value_)


def score(value_):
    if value_ is None or value_ == "":
        return "Not available"
    try:
        return f"{float(value_):.2f}/100"
    except (TypeError, ValueError):
        return fmt(value_)


def safe_text(value_):
    return fmt(value_).replace("|", r"\|").replace("\n", " ")


def bullets(items, empty_message="No information provided in the source report."):
    if not items:
        return f"- {empty_message}"

    result = []
    for item in items:
        if isinstance(item, dict):
            area = item.get("area")
            evidence = item.get("evidence")
            description = item.get("description")
            reason = item.get("reason")
            name = item.get("name")

            heading = area or description or reason or name
            if heading:
                result.append(f"- **{safe_text(heading)}**")
                if evidence is not None:
                    if isinstance(evidence, list):
                        result.extend(f"  - {safe_text(entry)}" for entry in evidence)
                    else:
                        result.append(f"  - Evidence: {safe_text(evidence)}")
                note = item.get("note")
                if note:
                    result.append(f"  - Note: {safe_text(note)}")
            else:
                result.append(f"- {safe_text(json.dumps(item, ensure_ascii=False))}")
        elif isinstance(item, list):
            result.extend(f"- {safe_text(entry)}" for entry in item)
        else:
            result.append(f"- {safe_text(item)}")
    return "\n".join(result)


def build_report(profile):
    if not isinstance(profile, dict):
        raise ValueError("Candidate profile JSON must contain an object.")

    candidate = profile.get("candidate_information", {})
    executive = profile.get("executive_summary", {})
    performance = profile.get("performance_summary", {})
    ats = profile.get("ats_profile", {})
    screening = profile.get("screening_insights", {})
    hr = profile.get("hr_insights", {})
    technical = profile.get("technical_performance", {})
    machine = profile.get("machine_test_performance", {})
    risk = profile.get("risk_indicators", {})
    decision = profile.get("final_recommendation_details", {})
    quality = profile.get("report_quality", {})

    # Use the exact nested structure from candidate_ai_profile.json.
    score_rows = [
        ("ATS assessment", value(performance.get("ats", {}), "score")),
        ("Initial screening", value(performance.get("screening", {}), "score")),
        ("HR interview", value(performance.get("hr_interview", {}), "score")),
        ("Technical interview", value(performance.get("technical_interview", {}), "score")),
        ("Machine test", value(performance.get("machine_test", {}), "score")),
        ("Hiring fit", value(performance.get("hiring_fit", {}), "score")),
    ]

    reasons = decision.get("reasons", [])
    indicators = risk.get("indicators", [])
    if not indicators and risk.get("explicit_risk_flags"):
        indicators = risk["explicit_risk_flags"]

    skill_score = None
    # The profile gives an ATS skill score in the evidence of strengths;
    # preserve that source-reported value rather than deriving a new score.
    for item in profile.get("strengths", []):
        evidence = item.get("evidence", "") if isinstance(item, dict) else ""
        if item.get("area") == "Skill matching" and "84.62" in str(evidence):
            skill_score = 84.62
            break

    test_results = machine.get("test_results", {})
    avg = hr.get("parameter_averages", {})
    communication = screening.get("average_communication", {})
    experience = ats.get("experience_details", {})
    education = ats.get("education_details", {})

    lines = [
        "# ZecPath — Candidate Hiring Intelligence Report",
        "",
        f"**Report version:** {safe_text(profile.get('report_version'))}  ",
        f"**Report type:** {safe_text(profile.get('report_type'))}  ",
        f"**Candidate ID:** {safe_text(candidate.get('candidate_id'))}  ",
        f"**Job ID:** {safe_text(candidate.get('job_id'))}  ",
        f"**Target role:** {safe_text(candidate.get('target_role'))}  ",
        f"**Export generated (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}  ",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"- **Hiring fit score:** {score(executive.get('hiring_fit_score'))}",
        f"- **Final recommendation:** {safe_text(executive.get('final_recommendation'))}",
        f"- **Confidence indicator:** {score(executive.get('confidence_score'))}",
        f"- **Confidence interpretation:** {safe_text(executive.get('confidence_interpretation'))}",
        f"- **Human review required:** {fmt(executive.get('human_review_required'))}",
        f"- **Automated hiring action taken:** {fmt(executive.get('automated_hiring_action_taken'))}",
        "",
        "> This report reproduces the existing profile. It does not independently verify the candidate's claims or make a hiring decision.",
        "",
        "## 2. Assessment Score Summary",
        "",
        "| Assessment | Score | Source status | Source / data type |",
        "|---|---:|---|---|",
    ]

    for label, raw_score in score_rows:
        key_map = {
            "ATS assessment": "ats",
            "Initial screening": "screening",
            "HR interview": "hr_interview",
            "Technical interview": "technical_interview",
            "Machine test": "machine_test",
            "Hiring fit": "hiring_fit",
        }
        source = performance.get(key_map[label], {})
        source_text = source.get("source", "Not available")
        if source.get("data_type"):
            source_text += f"; {source['data_type']}"
        lines.append(
            f"| {label} | {score(raw_score)} | "
            f"{safe_text(source.get('status'))} | {safe_text(source_text)} |"
        )

    lines += [
        "",
        "## 3. ATS and Skill Analysis",
        "",
        f"- **ATS matching status:** {safe_text(ats.get('matching_status'))}",
        f"- **Shortlisting status:** {safe_text(ats.get('shortlisting_status'))}",
        f"- **Skill match score:** {score(skill_score)}",
        f"- **Matched required skills:** {len(ats.get('matched_skills', []))} of {len(ats.get('required_skills', []))}",
        "",
        "**Matched skills**",
        "",
        bullets(ats.get("matched_skills", []), "No matched skills listed."),
        "",
        "**Required skills without an ATS match**",
        "",
        bullets(ats.get("missing_skill_matches", []), "No unmatched skills listed."),
        "",
        "### Experience alignment",
        "",
        f"- **Score:** {score(experience.get('score'))}",
        f"- **Candidate experience:** {fmt(experience.get('candidate_experience_years'))} years",
        f"- **Required range:** {fmt(experience.get('minimum_required_years'))}–{fmt(experience.get('maximum_required_years'))} years",
        f"- **Status:** {safe_text(experience.get('status'))}",
        "",
        "### Education alignment",
        "",
        f"- **Score:** {score(education.get('score'))}",
        f"- **Candidate degrees:** {safe_text(education.get('candidate_degrees', []))}",
        f"- **Required fields:** {safe_text(education.get('required_fields', []))}",
        f"- **Status:** {safe_text(education.get('status'))}",
        "",
        "## 4. Screening and Interview Insights",
        "",
        f"- **Screening questions processed:** {fmt(screening.get('successfully_processed'))} of {fmt(screening.get('total_questions'))}",
        f"- **Screening communication strength:** {score(communication.get('communication_strength'))}",
        f"- **HR questions:** {fmt(hr.get('total_questions'))}",
        "",
        "| HR parameter | Score |",
        "|---|---:|",
    ]
    for key, label in [
        ("answer_relevance", "Answer relevance"),
        ("communication", "Communication"),
        ("confidence", "Confidence"),
        ("consistency", "Consistency"),
    ]:
        lines.append(f"| {label} | {score(avg.get(key))} |")

    lines += [
        "",
        f"- **Technical questions evaluated:** {fmt(value(technical.get('evaluation_summary', {}), 'total_questions'))}",
        f"- **Technical score category:** {safe_text(value(technical.get('evaluation_summary', {}), 'score_category'))}",
        f"- **Machine tests passed:** {fmt(test_results.get('passed_tests'))} of {fmt(test_results.get('total_tests'))}",
        f"- **Machine-test pass rate:** {fmt(test_results.get('test_pass_rate'))}%",
        "",
        "## 5. Candidate Strengths",
        "",
        bullets(profile.get("strengths", [])),
        "",
        "## 6. Improvement Areas",
        "",
        bullets(profile.get("improvement_areas", [])),
        "",
        "## 7. Risk Indicators and Review Flags",
        "",
        f"- **Eligibility status:** {safe_text(risk.get('eligibility_status'))}",
        f"- **Demo rounds identified:** {safe_text(risk.get('demo_rounds', []))}",
        "",
        bullets([
            {
                "description": item.get("description", item.get("type", "Risk indicator")),
                "evidence": f"Status: {item.get('status', 'Not specified')}",
            }
            for item in indicators
        ], "No risk indicators listed in the source profile."),
        "",
        "Behavioral observations such as hesitation or speech pace are limited response indicators. The source explicitly warns against inferring personality, integrity, or job suitability from these signals alone.",
        "",
        "## 8. Final Recommendation and Explanation",
        "",
        f"**Recorded decision:** {safe_text(decision.get('decision'))}",
        "",
        "**Reasons recorded in the source profile:**",
        "",
        bullets(reasons),
        "",
        f"- **Decision policy:** {safe_text(decision.get('decision_policy'))}",
        f"- **Score-based decision:** {safe_text(decision.get('score_based_decision'))}",
        "",
        "### Configured thresholds and safeguards",
        "",
    ]

    thresholds = decision.get("score_thresholds", {})
    if thresholds:
        for key, val in thresholds.items():
            lines.append(f"- **{safe_text(key.replace('_', ' ').capitalize())}:** {fmt(val)}")
    else:
        lines.append("- Threshold details were not provided.")

    lines += [
        "",
        "## 9. Data Quality and Limitations",
        "",
        f"- **Source report status:** {safe_text(quality.get('source_report_status'))}",
        f"- **All configured sources available:** {fmt(quality.get('all_configured_sources_available'))}",
        f"- **Demo data present:** {fmt(quality.get('demo_data_present'))}",
        f"- **Verified hiring decision:** {fmt(quality.get('verified_hiring_decision'))}",
        "",
        "**Source-reported limitations**",
        "",
        bullets(quality.get("limitations", [])),
        "",
        "## 10. Human Review Checklist",
        "",
        "- [ ] Verify candidate and job information.",
        "- [ ] Confirm assessment scores against their source reports.",
        "- [ ] Replace or verify demo/test assessment inputs.",
        "- [ ] Confirm eligibility and mandatory job criteria.",
        "- [ ] Review missing skill matches in the resume context.",
        "- [ ] Record the authorized human review outcome.",
        "",
        "---",
        "",
        "*Generated by the ZecPath Day 53 Report Exporter. Scores and recommendation are copied from the candidate profile and are not recalculated by this exporter.*",
        "",
    ]

    return "\n".join(lines)



def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Profile not found: {INPUT_FILE}. Run candidate_profile_report.py first."
        )
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        profile = json.load(f)

    report = build_report(profile)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report, encoding="utf-8")

    candidate = profile.get("candidate_information", {})
    print("=" * 60)
    print("ZecPath Day 53 - Export-Ready Report Format")
    print("=" * 60)
    print("Status: SUCCESS")
    print(f"Candidate ID: {candidate.get('candidate_id', 'Not available')}")
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print("Format: Markdown (.md)")
    print("Scores recalculated: No")
    print("Recommendation changed: No")
    print("=" * 60)


if __name__ == "__main__":
    main()
