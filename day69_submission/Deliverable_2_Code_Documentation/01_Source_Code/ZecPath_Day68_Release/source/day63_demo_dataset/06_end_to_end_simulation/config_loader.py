
import json
from pathlib import Path


# ============================================================
# ZECPath DAY 63 - SHARED CONFIGURATION LOADER
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parent

PROJECT_ROOT = SIMULATION_ROOT.parents[1]

CONFIG_FILE = (
    SIMULATION_ROOT / "config" / "pipeline_config.json"
)


class SimulationConfig:

    """
    Loads and validates the configuration used by
    the reusable ZecPath End-to-End Simulation.
    """

    def __init__(self, config_file=CONFIG_FILE):

        self.config_file = Path(config_file)

        self.config = self.load_config()

        self.validate_config()

        self.dataset_root = self.resolve_dataset_root()

        self.dataset_name = self.config["dataset"]["dataset_name"]

        self.dataset_type = self.config["dataset"]["dataset_type"]

        self.execution = self.config["execution"]

        self.reporting = self.config["reporting"]

        self.simulation_root = SIMULATION_ROOT

        self.project_root = PROJECT_ROOT

        self.output_dir = SIMULATION_ROOT / "outputs"

    # --------------------------------------------------------
    # LOAD CONFIGURATION
    # --------------------------------------------------------

    def load_config(self):

        if not self.config_file.exists():

            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}"
            )

        try:

            with self.config_file.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Invalid configuration JSON: {error}"
            )

        if not isinstance(data, dict):

            raise ValueError(
                "Configuration must contain a JSON object."
            )

        return data

    # --------------------------------------------------------
    # VALIDATE CONFIGURATION
    # --------------------------------------------------------

    def validate_config(self):

        required_sections = [
            "dataset",
            "execution",
            "reporting"
        ]

        for section in required_sections:

            if section not in self.config:

                raise ValueError(
                    f"Missing configuration section: {section}"
                )

            if not isinstance(self.config[section], dict):

                raise ValueError(
                    f"Configuration section '{section}' must be an object."
                )

        dataset = self.config["dataset"]

        required_dataset_fields = [
            "dataset_name",
            "dataset_root",
            "dataset_type"
        ]

        for field in required_dataset_fields:

            if not dataset.get(field):

                raise ValueError(
                    f"Missing dataset configuration: {field}"
                )

        execution = self.config["execution"]

        timeout = execution.get("timeout_seconds", 900)

        if not isinstance(timeout, int) or timeout <= 0:

            raise ValueError(
                "timeout_seconds must be a positive integer."
            )

        for field in (
            "continue_on_stage_failure",
            "validate_outputs"
        ):

            if field in execution and not isinstance(
                execution[field], bool
            ):

                raise ValueError(
                    f"Execution setting '{field}' must be boolean."
                )

        reporting = self.config["reporting"]

        for field in (
            "generate_candidate_reports",
            "generate_batch_report",
            "generate_performance_report"
        ):

            if field in reporting and not isinstance(
                reporting[field], bool
            ):

                raise ValueError(
                    f"Reporting setting '{field}' must be boolean."
                )

    # --------------------------------------------------------
    # RESOLVE DATASET PATH
    # --------------------------------------------------------

    def resolve_dataset_root(self):

        configured_path = Path(
            self.config["dataset"]["dataset_root"]
        )

        if not configured_path.is_absolute():

            configured_path = PROJECT_ROOT / configured_path

        configured_path = configured_path.resolve()

        if not configured_path.exists():

            raise FileNotFoundError(
                f"Dataset directory not found: {configured_path}"
            )

        if not configured_path.is_dir():

            raise NotADirectoryError(
                f"Dataset path is not a directory: {configured_path}"
            )

        return configured_path

    # --------------------------------------------------------
    # GET DATASET SUBDIRECTORIES
    # --------------------------------------------------------

    def get_dataset_path(self, folder_name):

        return self.dataset_root / folder_name

    @property
    def profile_dir(self):

        return self.get_dataset_path("01_candidate_profiles")

    @property
    def resume_dir(self):

        return self.get_dataset_path("02_sample_resumes")

    @property
    def jd_dir(self):

        return self.get_dataset_path("03_job_descriptions")

    @property
    def response_dir(self):

        return self.get_dataset_path("04_candidate_responses")

    # --------------------------------------------------------
    # GET EXECUTION SETTINGS
    # --------------------------------------------------------

    @property
    def timeout_seconds(self):

        return self.execution.get("timeout_seconds", 900)

    @property
    def continue_on_stage_failure(self):

        return self.execution.get(
            "continue_on_stage_failure", False
        )

    @property
    def validate_outputs(self):

        return self.execution.get("validate_outputs", True)

    # --------------------------------------------------------
    # DISPLAY CONFIGURATION
    # --------------------------------------------------------

    def display(self):

        print("=" * 65)

        print("ZECPath - SIMULATION CONFIGURATION")

        print("=" * 65)

        print("Configuration:", self.config_file)

        print("Project Root:", self.project_root)

        print("Simulation Root:", self.simulation_root)

        print("Dataset Name:", self.dataset_name)

        print("Dataset Type:", self.dataset_type)

        print("Dataset Root:", self.dataset_root)

        print("Candidate Profiles:", self.profile_dir)

        print("Resumes:", self.resume_dir)

        print("Job Descriptions:", self.jd_dir)

        print("Candidate Responses:", self.response_dir)

        print("Output Directory:", self.output_dir)

        print("Timeout:", self.timeout_seconds, "seconds")

        print("=" * 65)


# ============================================================
# TEST CONFIGURATION LOADER
# ============================================================

if __name__ == "__main__":

    try:

        config = SimulationConfig()

        config.display()

        print("\nCONFIGURATION STATUS: SUCCESS")

    except Exception as error:

        print("\nCONFIGURATION STATUS: FAILED")

        print("Error:", error)

        raise
