from pathlib import Path
import json

from sample_screening_reports import SampleScreeningReports


BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"


def test_strong_candidate():

    generator = SampleScreeningReports()
    report = generator.create_strong_candidate()

    assert report["candidate_id"] == "sample_candidate_001"
    assert report["screening_evaluation"]["final_screening_score"] == 94.5
    assert report["answer_status"] == "valid"

    print("1. Strong candidate sample PASS")


def test_incomplete_candidate():

    generator = SampleScreeningReports()
    report = generator.create_incomplete_candidate()

    assert report["candidate_id"] == "sample_candidate_002"
    assert report["screening_evaluation"]["final_screening_score"] == 61.5
    assert len(report["missing_data"]) > 0
    assert len(report["risks"]) > 0

    print("2. Incomplete candidate sample PASS")


def test_off_topic_candidate():

    generator = SampleScreeningReports()
    report = generator.create_off_topic_candidate()

    assert report["candidate_id"] == "sample_candidate_003"
    assert report["answer_status"] == "off_topic"

    question = report["question_scores"][0]

    assert question["off_topic"] is True
    assert question["intent"] == "off_topic"

    print("3. Off-topic candidate sample PASS")


def test_uncertain_candidate():

    generator = SampleScreeningReports()
    report = generator.create_uncertain_candidate()

    assert report["candidate_id"] == "sample_candidate_004"
    assert report["answer_status"] == "valid"

    signals = report["behavioral_signals"]

    assert signals["hesitation_count"] > 0
    assert signals["uncertainty_count"] > 0

    print("4. Uncertain candidate sample PASS")


def test_strong_candidate_skills():

    generator = SampleScreeningReports()
    report = generator.create_strong_candidate()

    skills = report["highlights"]["skill_confirmations"]

    assert "Python" in skills
    assert "Django" in skills
    assert "FastAPI" in skills

    print("5. Strong candidate skill confirmation PASS")


def test_salary_and_availability():

    generator = SampleScreeningReports()
    report = generator.create_strong_candidate()

    highlights = report["highlights"]

    assert highlights["salary_expectation"]["amount"] == 70000
    assert highlights["salary_expectation"]["currency"] == "INR"
    assert highlights["availability"] == "Available immediately"

    print("6. Salary and availability PASS")


def test_json_generation():

    generator = SampleScreeningReports()

    report = generator.create_strong_candidate()

    file_path = generator.save_json_report(
        report,
        "test_sample_screening_report.json"
    )

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        saved_report = json.load(file)

    assert saved_report["candidate_id"] == "sample_candidate_001"

    file_path.unlink()

    print("7. JSON report generation PASS")


def test_txt_generation():

    generator = SampleScreeningReports()

    report = generator.create_strong_candidate()

    file_path = generator.create_recruiter_report(
        report,
        "test_sample_recruiter_report.txt"
    )

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert "AI SCREENING REPORT" in content
    assert "sample_candidate_001" in content
    assert "94.5/100" in content
    assert "Python" in content

    file_path.unlink()

    print("8. Recruiter report generation PASS")


def test_all_reports_generation():

    generator = SampleScreeningReports()

    files = generator.generate_all_reports()

    assert len(files) == 4

    for file_set in files:

        assert file_set["json"].exists()
        assert file_set["txt"].exists()

    print("9. All four sample reports generation PASS")


def test_sample_report_structure():

    generator = SampleScreeningReports()

    reports = [
        generator.create_strong_candidate(),
        generator.create_incomplete_candidate(),
        generator.create_off_topic_candidate(),
        generator.create_uncertain_candidate()
    ]

    required_fields = [
        "report_type",
        "candidate_id",
        "job_id",
        "screening_evaluation",
        "strengths",
        "risks",
        "missing_data",
        "highlights",
        "communication_summary",
        "behavioral_signals",
        "answer_status"
    ]

    for report in reports:

        for field in required_fields:
            assert field in report

    print("10. Sample report structure PASS")


if __name__ == "__main__":

    print("\nSAMPLE SCREENING REPORT TEST")
    print("=" * 60)

    tests = [
        test_strong_candidate,
        test_incomplete_candidate,
        test_off_topic_candidate,
        test_uncertain_candidate,
        test_strong_candidate_skills,
        test_salary_and_availability,
        test_json_generation,
        test_txt_generation,
        test_all_reports_generation,
        test_sample_report_structure
    ]

    passed = 0
    failed = 0

    for test in tests:

        try:
            test()
            passed += 1

        except Exception as error:

            print(f"{test.__name__} FAIL")
            print(f"Error: {error}")
            failed += 1

    print("=" * 60)
    print(f"Total : {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nAll sample screening report tests passed.")
    else:
        print("\nSome tests failed.")