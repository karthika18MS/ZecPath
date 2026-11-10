
import json
from pathlib import Path
import sys


# ============================================================
# IMPORT SHARED CONFIGURATION
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SIMULATION_ROOT.parents[1]

if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

from config_loader import SimulationConfig


# ============================================================
# DATASET LOADER
# ============================================================

class DatasetLoader:
    """
    Loads candidate profiles, resumes, job descriptions
    and assessment responses from a configurable dataset.
    """

    def __init__(self, dataset_root=None):

        self.config = SimulationConfig()

        self.dataset_root = (
            Path(dataset_root).resolve()
            if dataset_root
            else self.config.dataset_root
        )

        self.profile_dir = self.dataset_root / "01_candidate_profiles"
        self.resume_dir = self.dataset_root / "02_sample_resumes"
        self.jd_dir = self.dataset_root / "03_job_descriptions"

        self.response_dir = (
            self.dataset_root / "04_candidate_responses"
        )

        self.hr_dir = self.response_dir / "hr_responses"
        self.aptitude_dir = self.response_dir / "aptitude_responses"
        self.technical_dir = self.response_dir / "technical_responses"
        self.machine_test_dir = self.response_dir / "machine_test_responses"

    # --------------------------------------------------------
    # LOAD JSON
    # --------------------------------------------------------

    def load_json(self, file_path):

        if not file_path or not file_path.exists():
            return None

        try:
            with file_path.open("r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            return {
                "_load_error": str(error)
            }

    # --------------------------------------------------------
    # GENERATE CANDIDATE KEY
    # --------------------------------------------------------

    def get_candidate_key(self, candidate_id):

        candidate_id = str(candidate_id)

        if candidate_id.startswith("CAND"):
            number = candidate_id[4:]
            return f"candidate_{number}"

        return candidate_id.lower()

    # --------------------------------------------------------
    # FIND RESUME
    # --------------------------------------------------------

    def find_resume(self, candidate_key):

        if not self.resume_dir.exists():
            return None

        supported_extensions = [".pdf", ".docx"]

        for extension in supported_extensions:

            matches = list(
                self.resume_dir.rglob(
                    f"{candidate_key}_resume{extension}"
                )
            )

            if matches:
                return matches[0]

        return None

    # --------------------------------------------------------
    # FIND JOB DESCRIPTION
    # --------------------------------------------------------

    def find_job_description(self, job_id):

        if not job_id or not self.jd_dir.exists():
            return None

        matches = list(
            self.jd_dir.glob(f"{job_id}_*.txt")
        )

        return matches[0] if matches else None

    # --------------------------------------------------------
    # LOAD ASSESSMENT RESPONSE
    # --------------------------------------------------------

    def load_assessment(self, folder, candidate_key, suffix):

        file_path = folder / f"{candidate_key}_{suffix}.json"

        return self.load_json(file_path)

    # --------------------------------------------------------
    # VALIDATE MACHINE TEST
    # --------------------------------------------------------

    def validate_machine_test(self, data):
        """
        Machine-test files use a different structure from
        HR, aptitude and technical response files.

        They do not use response_status.

        A valid machine-test JSON file is classified as
        AVAILABLE_SIMULATED when its required sections exist.
        """

        if data is None:
            return "MISSING"

        if not isinstance(data, dict):
            return "INVALID_FORMAT"

        if data.get("_load_error"):
            return "INVALID_JSON"

        if data.get("assessment_type") != "MACHINE_TEST":
            return "INVALID_ASSESSMENT_TYPE"

        task = data.get("task")
        if not isinstance(task, dict):
            return "INCOMPLETE_DATA"

        test_results = task.get("test_results")
        if not isinstance(test_results, dict):
            return "INCOMPLETE_DATA"

        review_scores = task.get("review_scores")
        if not isinstance(review_scores, dict):
            return "INCOMPLETE_DATA"

        # The supplied Day 63 machine-test files explicitly
        # identify their scores and results as simulated.
        is_simulated = (
            data.get("is_simulated") is True
            or data.get("test_results_are_simulated") is True
            or data.get("review_scores_are_simulated") is True
            or test_results.get("is_simulated") is True
            or review_scores.get("is_simulated") is True
        )

        if is_simulated:
            return "AVAILABLE_SIMULATED"

        return "AVAILABLE_UNVERIFIED"

    # --------------------------------------------------------
    # VALIDATE ASSESSMENT
    # --------------------------------------------------------

    def validate_assessment(self, data, assessment_type=None):

        if assessment_type == "machine_test":
            return self.validate_machine_test(data)

        if data is None:
            return "MISSING"

        if not isinstance(data, dict):
            return "INVALID_FORMAT"

        if data.get("_load_error"):
            return "INVALID_JSON"

        response_status = data.get("response_status")

        if isinstance(response_status, str):
            response_status = response_status.strip().lower()

        if response_status == "not_provided":
            return "NOT_PROVIDED"

        if response_status == "completed":
            return "AVAILABLE"

        if response_status:
            return "UNKNOWN_STATUS"

        return "STATUS_NOT_SPECIFIED"

    # --------------------------------------------------------
    # LOAD ONE CANDIDATE
    # --------------------------------------------------------

    def load_candidate(self, profile_file):

        profile_file = Path(profile_file)
        profile = self.load_json(profile_file)

        if not isinstance(profile, dict):

            return {
                "profile_file": str(profile_file),
                "profile_source": str(profile_file),
                "load_status": "INVALID_PROFILE",
                "load_error": profile
            }

        if profile.get("_load_error"):

            return {
                "profile_file": str(profile_file),
                "profile_source": str(profile_file),
                "load_status": "INVALID_PROFILE",
                "load_error": profile["_load_error"]
            }

        candidate_id = profile.get("candidate_id")

        if not candidate_id:

            return {
                "profile_file": str(profile_file),
                "profile_source": str(profile_file),
                "load_status": "INVALID_PROFILE",
                "load_error": "Missing candidate_id"
            }

        candidate_key = self.get_candidate_key(candidate_id)
        job_id = profile.get("job_id")

        resume = self.find_resume(candidate_key)

        job_description = (
            self.find_job_description(job_id)
            if job_id else None
        )

        assessments = {

            "hr": self.load_assessment(
                self.hr_dir,
                candidate_key,
                "hr"
            ),

            "aptitude": self.load_assessment(
                self.aptitude_dir,
                candidate_key,
                "aptitude"
            ),

            "technical": self.load_assessment(
                self.technical_dir,
                candidate_key,
                "technical"
            ),

            "machine_test": self.load_assessment(
                self.machine_test_dir,
                candidate_key,
                "machine_test"
            )
        }

        return {

            "candidate_id": candidate_id,

            "job_id": job_id,

            "profile": profile,

            "profile_source": str(profile_file),

            "resume": (
                str(resume)
                if resume else None
            ),

            "job_description": (
                str(job_description)
                if job_description else None
            ),

            "assessments": assessments,

            "load_status": "LOADED"
        }

    # --------------------------------------------------------
    # VALIDATE CANDIDATE INPUTS
    # --------------------------------------------------------

    def validate_candidate(self, candidate):

        if candidate.get("load_status") != "LOADED":
            return candidate

        checks = {}

        checks["resume"] = (
            "AVAILABLE"
            if candidate.get("resume")
            else "MISSING"
        )

        checks["job_description"] = (
            "AVAILABLE"
            if candidate.get("job_description")
            else "MISSING"
        )

        for assessment, data in candidate["assessments"].items():

            checks[assessment] = self.validate_assessment(
                data,
                assessment
            )

        candidate["input_validation"] = checks

        # Missing or unprovided inputs
        candidate["missing_inputs"] = [
            name
            for name, status in checks.items()
            if status in ("MISSING", "NOT_PROVIDED")
        ]

        # Invalid input data
        candidate["invalid_inputs"] = [
            name
            for name, status in checks.items()
            if status in (
                "INVALID_JSON",
                "INVALID_FORMAT",
                "INVALID_ASSESSMENT_TYPE",
                "INCOMPLETE_DATA"
            )
        ]

        # Inputs that exist but whose status is not confirmed
        candidate["unverified_inputs"] = [
            name
            for name, status in checks.items()
            if status in (
                "STATUS_NOT_SPECIFIED",
                "UNKNOWN_STATUS",
                "AVAILABLE_UNVERIFIED"
            )
        ]

        # A simulated machine-test file is present, but it
        # must not be confused with a real executed assessment.
        machine_test_data = candidate["assessments"].get(
            "machine_test"
        )

        if isinstance(machine_test_data, dict):

            if checks.get("machine_test") == "AVAILABLE_SIMULATED":

                task = machine_test_data.get("task", {})
                test_results = task.get("test_results", {})
                review_scores = task.get("review_scores", {})

                candidate["machine_test_metadata"] = {
                    "is_simulated": True,
                    "data_type": machine_test_data.get("data_type"),
                    "score_source": machine_test_data.get("score_source"),
                    "execution_status": test_results.get(
                        "execution_status"
                    ),
                    "review_status": review_scores.get(
                        "review_status"
                    ),
                    "test_results_are_simulated": (
                        machine_test_data.get(
                            "test_results_are_simulated"
                        )
                    ),
                    "review_scores_are_simulated": (
                        machine_test_data.get(
                            "review_scores_are_simulated"
                        )
                    )
                }

        # Profile validity and input completeness are separate.
        candidate["profile_validity"] = "VALID"

        candidate["input_completeness"] = (
            "COMPLETE"
            if (
                not candidate["missing_inputs"]
                and not candidate["invalid_inputs"]
                and not candidate["unverified_inputs"]
            )
            else "INCOMPLETE"
        )

        return candidate

    # --------------------------------------------------------
    # LOAD COMPLETE DATASET
    # --------------------------------------------------------

    def load_dataset(self):

        if not self.profile_dir.exists():

            raise FileNotFoundError(
                f"Profile directory not found: {self.profile_dir}"
            )

        profile_files = sorted(
            self.profile_dir.glob("*.json")
        )

        candidates = []

        for profile_file in profile_files:

            candidate = self.load_candidate(profile_file)
            candidate = self.validate_candidate(candidate)

            candidates.append(candidate)

        valid_count = sum(
            item.get("load_status") == "LOADED"
            for item in candidates
        )

        invalid_count = len(candidates) - valid_count

        complete_count = sum(
            item.get("input_completeness") == "COMPLETE"
            for item in candidates
        )

        incomplete_count = valid_count - complete_count

        return {

            "dataset_name": self.dataset_root.name,

            "dataset_root": str(self.dataset_root),

            "dataset_type": self.config.dataset_type,

            "total_candidates": len(candidates),

            "valid_candidates": valid_count,

            "invalid_candidates": invalid_count,

            "complete_candidates": complete_count,

            "incomplete_candidates": incomplete_count,

            "candidates": candidates
        }


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    loader = DatasetLoader()
    dataset = loader.load_dataset()

    print("=" * 65)
    print("ZECPath - CONFIGURABLE DATASET LOADER")
    print("=" * 65)

    print("Dataset:", dataset["dataset_name"])
    print("Dataset Root:", dataset["dataset_root"])
    print("Dataset Type:", dataset["dataset_type"])

    print("Total Candidates:", dataset["total_candidates"])
    print("Valid Profiles:", dataset["valid_candidates"])
    print("Invalid Profiles:", dataset["invalid_candidates"])

    print("Complete Inputs:", dataset["complete_candidates"])
    print("Incomplete Inputs:", dataset["incomplete_candidates"])

    print("\nCANDIDATE INPUT VALIDATION")
    print("-" * 65)

    for candidate in dataset["candidates"]:

        if candidate.get("load_status") != "LOADED":

            print("\nInvalid Profile:")
            print(candidate.get("profile_file"))
            print("Reason:", candidate.get("load_error"))

            continue

        print("\nCandidate:", candidate["candidate_id"])
        print("Job:", candidate["job_id"])
        print("Profile Validity:", candidate["profile_validity"])
        print("Input Completeness:", candidate["input_completeness"])

        for name, status in candidate["input_validation"].items():
            print(f"{name}: {status}")

        if candidate.get("machine_test_metadata"):

            metadata = candidate["machine_test_metadata"]

            print("Machine Test Simulation:", metadata["is_simulated"])
            print("Test Execution:", metadata["execution_status"])
            print("Human Review:", metadata["review_status"])

    print("\nDataset loading completed.")
