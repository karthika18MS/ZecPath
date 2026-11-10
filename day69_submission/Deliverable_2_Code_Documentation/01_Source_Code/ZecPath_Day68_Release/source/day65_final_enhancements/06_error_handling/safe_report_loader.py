
import json
import importlib.util
from pathlib import Path
from typing import Any


# --------------------------------------------------
# LOAD SUPPORT MODULES
# --------------------------------------------------

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def load_module(module_name: str, module_path: Path):
    """Dynamically load a Python module from its file path."""

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Unable to load {module_name} from: {module_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# Load safe JSON loader
safe_json_module = load_module(
    "safe_json_loader",
    CURRENT_DIRECTORY / "safe_json_loader.py"
)

load_json_safely = safe_json_module.load_json_safely


# Load centralized error logger
error_logger_module = load_module(
    "error_logger",
    CURRENT_DIRECTORY / "error_logger.py"
)

get_logger = error_logger_module.get_logger

logger = get_logger("safe_report_loader")


# --------------------------------------------------
# REPORT FIELD EXTRACTION
# --------------------------------------------------

def extract_candidate_id(report: dict[str, Any]) -> Any:

    candidate_information = report.get(
        "candidate_information", {}
    )

    if isinstance(candidate_information, dict):
        return candidate_information.get("candidate_id")

    return report.get("candidate_id")


def extract_job_id(report: dict[str, Any]) -> Any:

    candidate_information = report.get(
        "candidate_information", {}
    )

    if isinstance(candidate_information, dict):
        return candidate_information.get("job_id")

    return report.get("job_id")


# --------------------------------------------------
# REPORT STRUCTURE VALIDATION
# --------------------------------------------------

def validate_report_structure(
    report: Any,
    file_path: Path
) -> dict[str, Any]:

    errors = []

    if not isinstance(report, dict):
        return {
            "valid": False,
            "errors": [
                "Report JSON root must be an object."
            ]
        }

    candidate_id = extract_candidate_id(report)
    job_id = extract_job_id(report)

    if not isinstance(candidate_id, str) or not candidate_id.strip():
        errors.append("Candidate ID is missing or invalid.")

    if not isinstance(job_id, str) or not job_id.strip():
        errors.append("Job ID is missing or invalid.")

    if not isinstance(report.get("assessment_summary"), list):
        errors.append("Assessment summary is missing or invalid.")

    if not isinstance(report.get("overall_evaluation"), dict):
        errors.append("Overall evaluation is missing or invalid.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "candidate_id": candidate_id,
        "job_id": job_id
    }


# --------------------------------------------------
# SAFE REPORT LOADER
# --------------------------------------------------

def load_reports_safely(
    reports_directory: str | Path
) -> dict[str, Any]:

    directory = Path(reports_directory)

    result = {
        "success": False,
        "reports_directory": str(directory),
        "total_files_found": 0,
        "reports_loaded": 0,
        "failed_reports": 0,
        "reports": [],
        "errors": []
    }

    logger.info(
        f"Starting safe report loading. Directory: {directory}"
    )

    # Check directory existence
    if not directory.exists():

        error_message = "Reports directory does not exist."

        logger.error(
            f"{error_message} Path: {directory}"
        )

        result["errors"].append({
            "file": str(directory),
            "error": error_message
        })

        result["failed_reports"] = 1

        return result

    # Check directory validity
    if not directory.is_dir():

        error_message = "Supplied path is not a directory."

        logger.error(
            f"{error_message} Path: {directory}"
        )

        result["errors"].append({
            "file": str(directory),
            "error": error_message
        })

        result["failed_reports"] = 1

        return result

    try:

        report_files = sorted(
            directory.glob("CAND*_report.json")
        )

        result["total_files_found"] = len(report_files)

        logger.info(
            f"Report files discovered: {len(report_files)}"
        )

        if not report_files:
            logger.warning(
                f"No matching recruiter reports found in {directory}"
            )

        # Process each report
        for file_path in report_files:

            try:

                load_result = load_json_safely(file_path)

                if not load_result["success"]:

                    result["failed_reports"] += 1

                    error_message = load_result["error"]

                    result["errors"].append({
                        "file": str(file_path),
                        "error": error_message
                    })

                    logger.error(
                        f"JSON loading failed for {file_path}: "
                        f"{error_message}"
                    )

                    continue

                report_data = load_result["data"]

                validation = validate_report_structure(
                    report_data,
                    file_path
                )

                if not validation["valid"]:

                    result["failed_reports"] += 1

                    error_message = "; ".join(
                        validation["errors"]
                    )

                    result["errors"].append({
                        "file": str(file_path),
                        "error": error_message
                    })

                    logger.warning(
                        f"Invalid report structure: {file_path}. "
                        f"Reason: {error_message}"
                    )

                    continue

                result["reports"].append({
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "candidate_id": validation["candidate_id"],
                    "job_id": validation["job_id"],
                    "data": report_data
                })

                result["reports_loaded"] += 1

                logger.info(
                    f"Report loaded successfully: "
                    f"Candidate={validation['candidate_id']}, "
                    f"Job={validation['job_id']}"
                )

            except Exception as exc:

                result["failed_reports"] += 1

                result["errors"].append({
                    "file": str(file_path),
                    "error": str(exc)
                })

                logger.exception(
                    f"Unexpected error while processing report: "
                    f"{file_path}"
                )

        result["success"] = result["failed_reports"] == 0

        logger.info(
            "Safe report loading completed. "
            f"Found={result['total_files_found']}, "
            f"Loaded={result['reports_loaded']}, "
            f"Failed={result['failed_reports']}"
        )

    except Exception as exc:

        result["success"] = False

        result["errors"].append({
            "file": str(directory),
            "error": str(exc)
        })

        result["failed_reports"] += 1

        logger.exception(
            f"Unexpected error during batch report loading: {directory}"
        )

    return result


# --------------------------------------------------
# SAVE LOADING SUMMARY
# --------------------------------------------------

def save_loading_summary(
    result: dict[str, Any],
    output_path: str | Path
) -> None:

    output_file = Path(output_path)

    try:

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        logger.info(
            f"Report loading summary saved successfully: {output_file}"
        )

    except Exception:

        logger.exception(
            f"Failed to save report loading summary: {output_file}"
        )

        raise


# --------------------------------------------------
# DIRECT EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]

    enhancement_root = (
        project_root / "day65_final_enhancements"
    )

    reports_directory = (
        enhancement_root
        / "09_final_outputs"
        / "recruiter_reports"
    )

    output_path = (
        enhancement_root
        / "09_final_outputs"
        / "safe_report_loading_summary.json"
    )

    print("=" * 65)
    print("ZECPath DAY 65 - SAFE REPORT LOADER")
    print("=" * 65)

    print(f"Project root: {project_root}")
    print(f"Reports directory: {reports_directory}")

    loading_result = load_reports_safely(
        reports_directory
    )

    save_loading_summary(
        loading_result,
        output_path
    )

    print("\nBATCH LOADING SUMMARY")
    print("-" * 65)

    print(
        f"Reports found: "
        f"{loading_result['total_files_found']}"
    )

    print(
        f"Reports loaded: "
        f"{loading_result['reports_loaded']}"
    )

    print(
        f"Failed reports: "
        f"{loading_result['failed_reports']}"
    )

    print(
        f"Loading errors: "
        f"{len(loading_result['errors'])}"
    )

    if loading_result["errors"]:

        print("\nERROR DETAILS")

        for error in loading_result["errors"]:
            print(f"File: {error['file']}")
            print(f"Error: {error['error']}")

    print("\nOUTPUT FILE:")
    print(output_path)

    print("\nCENTRALIZED LOG FILE:")
    print(
        enhancement_root
        / "09_final_outputs"
        / "logs"
        / "zecpath_day65.log"
    )

    print("\nSAFE REPORT LOADING COMPLETED")
