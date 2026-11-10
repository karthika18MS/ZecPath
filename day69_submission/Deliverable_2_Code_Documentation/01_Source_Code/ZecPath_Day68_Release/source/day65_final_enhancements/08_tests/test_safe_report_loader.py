
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


# --------------------------------------------------
# LOAD SAFE REPORT LOADER MODULE
# --------------------------------------------------

module_path = (
    Path(__file__).resolve().parents[1]
    / "06_error_handling"
    / "safe_report_loader.py"
)

spec = importlib.util.spec_from_file_location(
    "safe_report_loader",
    module_path
)

if spec is None or spec.loader is None:
    raise ImportError(
        f"Unable to load safe_report_loader from: {module_path}"
    )

safe_report_loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safe_report_loader)

load_reports_safely = safe_report_loader.load_reports_safely
validate_report_structure = (
    safe_report_loader.validate_report_structure
)


# --------------------------------------------------
# TEST CLASS
# --------------------------------------------------

class TestSafeReportLoader(unittest.TestCase):

    def create_valid_report(self, candidate_id="CAND001"):
        return {
            "report_type": "Recruiter-Friendly Candidate Summary",
            "candidate_information": {
                "candidate_id": candidate_id,
                "job_id": "JD001"
            },
            "assessment_summary": [
                {
                    "round": "ats",
                    "score": 85.0,
                    "assessment_status": "COMPLETED"
                }
            ],
            "overall_evaluation": {
                "unified_score": 85.0,
                "score_coverage": 100.0,
                "scoring_status": "COMPLETED"
            }
        }

    def test_valid_report_structure(self):
        report = self.create_valid_report()

        result = validate_report_structure(
            report,
            Path("CAND001_report.json")
        )

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["candidate_id"], "CAND001"
        )
        self.assertEqual(
            result["job_id"], "JD001"
        )

    def test_missing_candidate_id(self):
        report = self.create_valid_report()
        report["candidate_information"]["candidate_id"] = ""

        result = validate_report_structure(
            report,
            Path("invalid_report.json")
        )

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("Candidate ID" in error
                for error in result["errors"])
        )

    def test_missing_job_id(self):
        report = self.create_valid_report()
        report["candidate_information"]["job_id"] = ""

        result = validate_report_structure(
            report,
            Path("invalid_report.json")
        )

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("Job ID" in error
                for error in result["errors"])
        )

    def test_invalid_json_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            valid_path = directory / "CAND001_report.json"
            invalid_path = directory / "CAND002_report.json"

            valid_path.write_text(
                json.dumps(self.create_valid_report()),
                encoding="utf-8"
            )

            invalid_path.write_text(
                '{"candidate_id": ',
                encoding="utf-8"
            )

            result = load_reports_safely(directory)

            self.assertEqual(
                result["total_files_found"], 2
            )
            self.assertEqual(
                result["reports_loaded"], 1
            )
            self.assertEqual(
                result["failed_reports"], 1
            )

    def test_missing_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_directory = (
                Path(temp_dir) / "missing_reports"
            )

            result = load_reports_safely(
                missing_directory
            )

            self.assertFalse(result["success"])
            self.assertEqual(
                result["reports_loaded"], 0
            )
            self.assertEqual(
                result["failed_reports"], 1
            )

    def test_multiple_valid_reports(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            for number in range(1, 4):
                candidate_id = f"CAND00{number}"

                report_path = (
                    directory / f"{candidate_id}_report.json"
                )

                report_path.write_text(
                    json.dumps(
                        self.create_valid_report(candidate_id)
                    ),
                    encoding="utf-8"
                )

            result = load_reports_safely(directory)

            self.assertTrue(result["success"])
            self.assertEqual(
                result["total_files_found"], 3
            )
            self.assertEqual(
                result["reports_loaded"], 3
            )
            self.assertEqual(
                result["failed_reports"], 0
            )


# --------------------------------------------------
# RUN TESTS
# --------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
