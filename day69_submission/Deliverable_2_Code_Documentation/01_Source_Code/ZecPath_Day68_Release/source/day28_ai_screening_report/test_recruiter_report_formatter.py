from pathlib import Path
import json

from recruiter_report_formatter import RecruiterReportFormatter


BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"


def load_test_report():
    file_path = RESULTS_DIR / "candidate_006_screening_report.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def test_header():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_header()

    assert "AI SCREENING REPORT" in output
    assert "candidate_006" in output
    assert "JOB_BACKEND_001" in output


def test_screening_score():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_screening_score()

    assert "92.5/100" in output
    assert "Clarity" in output
    assert "Relevance" in output
    assert "Completeness" in output
    assert "Consistency" in output


def test_key_answers():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_key_answers()

    assert "Experience" in output
    assert "3" in output
    assert "backend development" in output
    assert "Python and Django" in output


def test_highlights():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_highlights()

    assert "Skill Confirmations" in output
    assert "Python" in output
    assert "Django" in output
    assert "Salary Expectation" in output
    assert "Availability" in output


def test_strengths():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_strengths()

    assert "STRENGTHS" in output
    assert "confidence" in output.lower()


def test_risks():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_risks()

    assert "RISKS" in output
    assert "No major risks identified" in output


def test_missing_data():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_missing_data()

    assert "MISSING DATA" in output
    assert "No missing data identified" in output


def test_communication_summary():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_communication_summary()

    assert "COMMUNICATION SUMMARY" in output
    assert "Confidence" in output
    assert "Clarity" in output
    assert "Engagement" in output
    assert "Consistency" in output
    assert "97.5" in output


def test_behavioral_signals():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_behavioral_signals()

    assert "BEHAVIORAL / RESPONSE SIGNALS" in output
    assert "Hesitation Count" in output
    assert "Uncertainty Count" in output
    assert "Response Word Count" in output
    assert "normal" in output
    assert "positive" in output


def test_question_scores():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_question_scores()

    assert "QUESTION-WISE EVALUATION" in output
    assert "BACKEND_EXP_001" in output
    assert "95.0/100" in output
    assert "experience" in output


def test_complete_report():
    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output = formatter.format_report()

    required_sections = [
        "AI SCREENING REPORT",
        "SCREENING SCORE",
        "KEY ANSWERS",
        "RECRUITER HIGHLIGHTS",
        "STRENGTHS",
        "RISKS",
        "MISSING DATA",
        "COMMUNICATION SUMMARY",
        "BEHAVIORAL / RESPONSE SIGNALS",
        "QUESTION-WISE EVALUATION",
        "REPORT INFORMATION",
    ]

    for section in required_sections:
        assert section in output


def test_save_report():

    report = load_test_report()
    formatter = RecruiterReportFormatter(report)

    output_file = RESULTS_DIR / "test_recruiter_report.txt"

    formatter.save_report(output_file)

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as file:
        content = file.read()

    assert "AI SCREENING REPORT" in content
    assert "candidate_006" in content

    # Clean up test output
    output_file.unlink()


def test_load_from_file():

    input_file = RESULTS_DIR / "candidate_006_screening_report.json"

    formatter = RecruiterReportFormatter.load_from_file(input_file)

    assert isinstance(formatter, RecruiterReportFormatter)
    assert formatter.report["candidate_id"] == "candidate_006"


def test_format_value():

    assert RecruiterReportFormatter.format_value(None) == "Not provided"

    assert (
        RecruiterReportFormatter.format_value(["Python", "Django"])
        == "Python, Django"
    )

    assert (
        RecruiterReportFormatter.format_value({"years": 3})
        == "years: 3"
    )


if __name__ == "__main__":

    print("\nRECRUITER REPORT FORMATTER TEST")
    print("=" * 50)

    tests = [
        ("Header formatting", test_header),
        ("Screening score", test_screening_score),
        ("Key answers", test_key_answers),
        ("Recruiter highlights", test_highlights),
        ("Strengths", test_strengths),
        ("Risks", test_risks),
        ("Missing data", test_missing_data),
        ("Communication summary", test_communication_summary),
        ("Behavioral signals", test_behavioral_signals),
        ("Question scores", test_question_scores),
        ("Complete report", test_complete_report),
        ("Save report", test_save_report),
        ("Load from file", test_load_from_file),
        ("Value formatting", test_format_value),
    ]

    passed = 0
    failed = 0

    for name, test in tests:
        try:
            test()
            print(f"{name} PASS")
            passed += 1
        except Exception as error:
            print(f"{name} FAIL")
            print(f"  Error: {error}")
            failed += 1

    print("=" * 50)
    print(f"Total : {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nAll recruiter report formatter tests passed.")
    else:
        print("\nSome tests failed.")