
import json
import re
import sys
from pathlib import Path


# ============================================================
# 1. PROJECT PATH CONFIGURATION
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]

if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))


# ============================================================
# 2. INPUT VALIDATOR
# ============================================================

class InputValidator:
    """
    Validates the ZecPath simulation dataset using dataset_schema.json.

    Validation includes:
    1. Required dataset directories
    2. Candidate profile JSON files
    3. Candidate resume files
    4. Job description files
    5. Candidate response files
    6. Machine-test nested structure
    7. Missing candidate inputs
    """

    def __init__(self, dataset_root, schema_path=None):

        self.dataset_root = Path(dataset_root).resolve()

        if schema_path is None:
            schema_path = (
                SIMULATION_ROOT
                / "config"
                / "dataset_schema.json"
            )

        self.schema_path = Path(schema_path).resolve()

        if not self.dataset_root.exists():
            raise FileNotFoundError(
                f"Dataset directory not found: {self.dataset_root}"
            )

        if not self.dataset_root.is_dir():
            raise NotADirectoryError(
                f"Dataset root is not a directory: {self.dataset_root}"
            )

        if not self.schema_path.exists():
            raise FileNotFoundError(
                f"Dataset schema not found: {self.schema_path}"
            )

        try:
            with open(
                self.schema_path,
                "r",
                encoding="utf-8"
            ) as file:
                self.schema = json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid dataset schema JSON: {error}"
            )

    # ========================================================
    # 3. COMMON HELPER METHODS
    # ========================================================

    @staticmethod
    def read_json(file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    @staticmethod
    def extract_candidate_number(value):

        """
        Extract candidate number from:
        CAND001
        candidate_001
        candidate_001_resume
        """

        match = re.search(
            r"(\d+)",
            str(value),
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

        return None

    def validate_extension(self, file_path, allowed_extensions):

        allowed = [
            extension.lower()
            for extension in allowed_extensions
        ]

        return Path(file_path).suffix.lower() in allowed

    # ========================================================
    # 4. DIRECTORY VALIDATION
    # ========================================================

    def validate_directories(self):

        missing_directories = []

        required_directories = self.schema.get(
            "required_directories",
            []
        )

        for directory in required_directories:

            directory_path = self.dataset_root / directory

            if not directory_path.is_dir():
                missing_directories.append(directory)

        response_config = self.schema.get(
            "responses",
            {}
        )

        response_root = (
            self.dataset_root
            / "04_candidate_responses"
        )

        for directory in response_config.get(
            "required_directories",
            []
        ):

            directory_path = response_root / directory

            if not directory_path.is_dir():
                missing_directories.append(
                    f"04_candidate_responses/{directory}"
                )

        return {
            "valid": len(missing_directories) == 0,
            "missing_directories": missing_directories
        }

    # ========================================================
    # 5. CANDIDATE PROFILE VALIDATION
    # ========================================================

    def validate_profile(self, profile_path):

        result = {
            "valid": True,
            "candidate_id": None,
            "errors": []
        }

        try:

            profile = self.read_json(profile_path)

            if not isinstance(profile, dict):

                return {
                    "valid": False,
                    "candidate_id": None,
                    "errors": [
                        "Candidate profile must be a JSON object"
                    ]
                }

            profile_config = self.schema.get(
                "candidate_profile",
                {}
            )

            # Check required fields.
            for field in profile_config.get(
                "required_fields",
                []
            ):

                if field not in profile:
                    result["errors"].append(
                        f"Missing required field: {field}"
                    )

            # Check field types.
            for field, expected_type in profile_config.get(
                "field_types",
                {}
            ).items():

                if field not in profile:
                    continue

                if expected_type == "string":

                    if not isinstance(profile[field], str):
                        result["errors"].append(
                            f"{field} must be a string"
                        )

                    elif not profile[field].strip():
                        result["errors"].append(
                            f"{field} cannot be empty"
                        )

            result["candidate_id"] = profile.get(
                "candidate_id"
            )

        except json.JSONDecodeError as error:

            result["errors"].append(
                f"Invalid JSON: {error}"
            )

        except OSError as error:

            result["errors"].append(str(error))

        result["valid"] = len(result["errors"]) == 0

        return result

    def validate_profiles(self):

        profile_dir = (
            self.dataset_root
            / "01_candidate_profiles"
        )

        results = []
        candidate_numbers = set()
        candidate_ids = set()

        if profile_dir.is_dir():

            for profile_path in sorted(
                profile_dir.glob("*.json")
            ):

                result = self.validate_profile(profile_path)

                candidate_id = result["candidate_id"]

                if candidate_id:

                    candidate_ids.add(str(candidate_id))

                    number = self.extract_candidate_number(
                        candidate_id
                    )

                    if number is not None:
                        candidate_numbers.add(number)

                results.append({
                    "file": profile_path.name,
                    "candidate_id": candidate_id,
                    "valid": result["valid"],
                    "errors": result["errors"]
                })

        invalid = [
            item for item in results
            if not item["valid"]
        ]

        return {
            "total_profiles_checked": len(results),
            "valid_profiles": len(results) - len(invalid),
            "invalid_profiles": len(invalid),
            "candidate_ids": sorted(candidate_ids),

            # Convert sets to lists for JSON serialization.
            "candidate_numbers": sorted(candidate_numbers),

            "results": results
        }

    # ========================================================
    # 6. RESUME VALIDATION
    # ========================================================

    def validate_resumes(self, candidate_numbers):

        resume_config = self.schema.get(
            "resume",
            {}
        )

        resume_dir = (
            self.dataset_root
            / "02_sample_resumes"
        )

        allowed_extensions = resume_config.get(
            "allowed_extensions",
            []
        )

        recursive = resume_config.get(
            "recursive_search",
            True
        )

        resume_files = []

        if resume_dir.is_dir():

            if recursive:
                files = resume_dir.rglob("*")
            else:
                files = resume_dir.iterdir()

            for file_path in sorted(files):

                if not file_path.is_file():
                    continue

                if not self.validate_extension(
                    file_path,
                    allowed_extensions
                ):
                    continue

                number = self.extract_candidate_number(
                    file_path.stem
                )

                resume_files.append({
                    "file": file_path.name,
                    "relative_path": str(
                        file_path.relative_to(resume_dir)
                    ),
                    "candidate_number": number,
                    "valid_extension": True
                })

        resume_candidate_numbers = {
            item["candidate_number"]
            for item in resume_files
            if item["candidate_number"] is not None
        }

        # Convert input to set for comparison.
        candidate_numbers = set(candidate_numbers)

        missing_resume_numbers = (
            candidate_numbers - resume_candidate_numbers
        )

        return {
            "total_resume_files": len(resume_files),
            "valid_resume_files": len(resume_files),

            "missing_resume_candidates": [
                f"CAND{number:03d}"
                for number in sorted(missing_resume_numbers)
            ],

            "complete": len(missing_resume_numbers) == 0,
            "files": resume_files
        }

    # ========================================================
    # 7. JOB DESCRIPTION VALIDATION
    # ========================================================

    def validate_job_descriptions(self):

        jd_config = self.schema.get(
            "job_description",
            {}
        )

        jd_dir = (
            self.dataset_root
            / "03_job_descriptions"
        )

        allowed_extensions = jd_config.get(
            "allowed_extensions",
            []
        )

        results = []

        if jd_dir.is_dir():

            for file_path in sorted(jd_dir.iterdir()):

                if not file_path.is_file():
                    continue

                valid = self.validate_extension(
                    file_path,
                    allowed_extensions
                )

                results.append({
                    "file": file_path.name,
                    "valid": valid,
                    "error": (
                        None if valid
                        else "Unsupported job description extension"
                    )
                })

        invalid = [
            item for item in results
            if not item["valid"]
        ]

        required = jd_config.get("required", True)

        has_required_files = (
            len(results) > 0 if required else True
        )

        return {
            "total_files": len(results),
            "valid_files": len(results) - len(invalid),
            "invalid_files": len(invalid),
            "required_files_present": has_required_files,
            "results": results
        }

    # ========================================================
    # 8. RESPONSE FILE VALIDATION
    # ========================================================

    def validate_response_files(self):

        response_config = self.schema.get(
            "responses",
            {}
        )

        response_root = (
            self.dataset_root
            / "04_candidate_responses"
        )

        allowed_extensions = response_config.get(
            "allowed_extensions",
            []
        )

        results = []

        for response_dir in response_config.get(
            "required_directories",
            []
        ):

            folder = response_root / response_dir

            if not folder.is_dir():
                continue

            # Only JSON candidate response files are processed.
            # Reference TXT files are intentionally ignored.
            for file_path in sorted(folder.glob("*.json")):

                try:

                    data = self.read_json(file_path)

                    valid_json = isinstance(data, dict)

                    error = (
                        None if valid_json
                        else "Response must contain a JSON object"
                    )

                except json.JSONDecodeError as exception:

                    valid_json = False
                    error = f"Invalid JSON: {exception}"

                except OSError as exception:

                    valid_json = False
                    error = str(exception)

                extension_valid = self.validate_extension(
                    file_path,
                    allowed_extensions
                )

                results.append({
                    "folder": response_dir,
                    "file": file_path.name,
                    "valid": valid_json and extension_valid,
                    "error": error if error else (
                        None if extension_valid
                        else "Unsupported response extension"
                    )
                })

        invalid = [
            item for item in results
            if not item["valid"]
        ]

        return {
            "total_response_files": len(results),
            "valid_response_files": len(results) - len(invalid),
            "invalid_response_files": len(invalid),
            "results": results
        }

    # ========================================================
    # 9. MACHINE TEST VALIDATION
    # ========================================================

    def validate_machine_test(self, file_path):

        result = {
            "valid": True,
            "errors": []
        }

        try:

            data = self.read_json(file_path)

            if not isinstance(data, dict):

                return {
                    "valid": False,
                    "errors": [
                        "Machine-test data must be a JSON object"
                    ]
                }

            machine_config = self.schema.get(
                "machine_test",
                {}
            )

            # Validate top-level fields.
            for field in machine_config.get(
                "required_fields",
                []
            ):

                if field not in data:
                    result["errors"].append(
                        f"Missing top-level field: {field}"
                    )

            # Validate assessment type.
            expected_type = machine_config.get(
                "expected_assessment_type"
            )

            if (
                expected_type
                and data.get("assessment_type") != expected_type
            ):

                result["errors"].append(
                    f"Expected assessment_type: {expected_type}"
                )

            # Validate nested task.
            task = data.get("task")

            if not isinstance(task, dict):

                result["errors"].append(
                    "task must be a JSON object"
                )

                task = {}

            else:

                for field in machine_config.get(
                    "task_required_fields",
                    []
                ):

                    if field not in task:
                        result["errors"].append(
                            f"Missing task field: {field}"
                        )

            # Validate test results.
            test_results = task.get("test_results")

            if not isinstance(test_results, dict):

                result["errors"].append(
                    "task.test_results must be a JSON object"
                )

                test_results = {}

            else:

                for field in machine_config.get(
                    "test_results_required_fields",
                    []
                ):

                    if field not in test_results:
                        result["errors"].append(
                            f"Missing task.test_results field: {field}"
                        )

            # Validate review scores.
            review_scores = task.get("review_scores")

            if not isinstance(review_scores, dict):

                result["errors"].append(
                    "task.review_scores must be a JSON object"
                )

                review_scores = {}

            else:

                for field in machine_config.get(
                    "review_scores_required_fields",
                    []
                ):

                    if field not in review_scores:
                        result["errors"].append(
                            f"Missing task.review_scores field: {field}"
                        )

            result["valid"] = len(result["errors"]) == 0

        except json.JSONDecodeError as error:

            result["valid"] = False
            result["errors"].append(
                f"Invalid JSON: {error}"
            )

        except OSError as error:

            result["valid"] = False
            result["errors"].append(str(error))

        return result

    def validate_machine_test_files(self):

        machine_test_dir = (
            self.dataset_root
            / "04_candidate_responses"
            / "machine_test_responses"
        )

        results = []

        if machine_test_dir.is_dir():

            for file_path in sorted(
                machine_test_dir.glob("*.json")
            ):

                result = self.validate_machine_test(
                    file_path
                )

                results.append({
                    "file": file_path.name,
                    "valid": result["valid"],
                    "errors": result["errors"]
                })

        invalid = [
            item for item in results
            if not item["valid"]
        ]

        return {
            "total_checked": len(results),
            "valid": len(results) - len(invalid),
            "invalid": len(invalid),
            "results": results
        }

    # ========================================================
    # 10. COMPLETE DATASET VALIDATION
    # ========================================================

    def validate_dataset(self):

        print("\nValidating dataset directories...")
        directory_result = self.validate_directories()

        print("Validating candidate profiles...")
        profile_result = self.validate_profiles()

        print("Validating candidate resumes...")

        # candidate_numbers is a JSON-compatible list.
        # validate_resumes converts it into a set internally.
        resume_result = self.validate_resumes(
            profile_result["candidate_numbers"]
        )

        print("Validating job descriptions...")
        jd_result = self.validate_job_descriptions()

        print("Validating candidate response files...")
        response_result = self.validate_response_files()

        print("Validating machine-test structures...")
        machine_result = self.validate_machine_test_files()

        overall_valid = (
            directory_result["valid"]
            and profile_result["invalid_profiles"] == 0
            and resume_result["complete"]
            and jd_result["invalid_files"] == 0
            and jd_result["required_files_present"]
            and response_result["invalid_response_files"] == 0
            and machine_result["invalid"] == 0
        )

        return {
            "schema_name": self.schema.get("schema_name"),
            "schema_version": self.schema.get("schema_version"),

            "dataset_root": str(self.dataset_root),

            "directory_validation": directory_result,

            "profile_validation": profile_result,

            "resume_validation": resume_result,

            "job_description_validation": jd_result,

            "response_validation": response_result,

            "machine_test_validation": machine_result,

            "overall_valid": overall_valid
        }


# ============================================================
# 11. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    from config_loader import SimulationConfig

    print("\nLoading simulation configuration...")

    config = SimulationConfig()

    print("Dataset root:", config.dataset_root)

    validator = InputValidator(
        dataset_root=config.dataset_root
    )

    print("\nStarting dataset schema validation...")

    result = validator.validate_dataset()

    print("\n========== DATASET SCHEMA VALIDATION ==========")

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    print("\n========== VALIDATION SUMMARY ==========")

    print(
        "Candidate profiles:",
        result["profile_validation"]["valid_profiles"],
        "/",
        result["profile_validation"]["total_profiles_checked"]
    )

    print(
        "Resume files:",
        result["resume_validation"]["total_resume_files"]
    )

    print(
        "Missing resumes:",
        result["resume_validation"]["missing_resume_candidates"]
    )

    print(
        "Job descriptions:",
        result["job_description_validation"]["valid_files"],
        "/",
        result["job_description_validation"]["total_files"]
    )

    print(
        "Response files:",
        result["response_validation"]["valid_response_files"],
        "/",
        result["response_validation"]["total_response_files"]
    )

    print(
        "Machine-test files:",
        result["machine_test_validation"]["valid"],
        "/",
        result["machine_test_validation"]["total_checked"]
    )

    if result["overall_valid"]:
        print("\nRESULT: DATASET VALIDATION SUCCESS")
    else:
        print("\nRESULT: DATASET VALIDATION FAILED")
