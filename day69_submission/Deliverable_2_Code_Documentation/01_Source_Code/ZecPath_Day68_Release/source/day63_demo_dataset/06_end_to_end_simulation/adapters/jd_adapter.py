
import re
import sys
from pathlib import Path


# ============================================================
# 1. SHARED CONFIGURATION
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SIMULATION_ROOT.parents[1]

if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config_loader import SimulationConfig


# ============================================================
# 2. JOB DESCRIPTION ADAPTER
# ============================================================

class JDAdapter:
    """
    Reads job descriptions and converts them into a
    standardized structure for the ZecPath ATS pipeline.

    Dataset paths are loaded through SimulationConfig.
    """

    def __init__(self, dataset_root=None):

        self.config = SimulationConfig()

        if dataset_root:

            self.dataset_root = Path(dataset_root).resolve()

            self.jd_directory = (
                self.dataset_root / "03_job_descriptions"
            )

        else:

            self.dataset_root = self.config.dataset_root

            self.jd_directory = self.config.jd_dir

    # --------------------------------------------------------
    # EXTRACT BASIC FIELD
    # --------------------------------------------------------

    def extract_field(self, text, heading):

        pattern = (
            rf"^{re.escape(heading)}\s*:\s*(.*?)$"
        )

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.MULTILINE
        )

        if match:
            return match.group(1).strip()

        return None

    # --------------------------------------------------------
    # EXTRACT SECTION CONTENT
    # --------------------------------------------------------

    def extract_section(
        self,
        text,
        start_heading,
        end_headings
    ):

        start_pattern = (
            rf"^\s*{re.escape(start_heading)}\s*:\s*$"
        )

        start_match = re.search(
            start_pattern,
            text,
            flags=re.IGNORECASE | re.MULTILINE
        )

        if not start_match:
            return []

        section_start = start_match.end()

        remaining_text = text[section_start:]

        end_positions = []

        for heading in end_headings:

            pattern = (
                rf"^\s*{re.escape(heading)}\s*:\s*$"
            )

            match = re.search(
                pattern,
                remaining_text,
                flags=re.IGNORECASE | re.MULTILINE
            )

            if match:
                end_positions.append(match.start())

        section_end = (
            min(end_positions)
            if end_positions
            else len(remaining_text)
        )

        section_text = remaining_text[:section_end]

        items = []

        for line in section_text.splitlines():

            line = line.strip()

            # Remove bullet markers
            line = re.sub(
                r"^[-*•]\s*",
                "",
                line
            )

            # Remove numbering
            line = re.sub(
                r"^\d+[.)]\s*",
                "",
                line
            )

            if line:
                items.append(line)

        return items

    # --------------------------------------------------------
    # EXTRACT EXPERIENCE RANGE
    # --------------------------------------------------------

    def extract_experience_range(self, text):

        patterns = [

            # Example: 2-4 Years
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:-|–|—|to)\s*"
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",

            # Example: Minimum: 2 years Maximum: 4 years
            r"minimum\s*:\s*(\d+(?:\.\d+)?)\s*years?"
            r".*?"
            r"maximum\s*:\s*(\d+(?:\.\d+)?)\s*years?"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE | re.DOTALL
            )

            if match:

                minimum = float(match.group(1))

                maximum = float(match.group(2))

                return {
                    "minimum_years": minimum,
                    "maximum_years": maximum
                }

        return {
            "minimum_years": None,
            "maximum_years": None
        }

    # --------------------------------------------------------
    # PROCESS JOB DESCRIPTION
    # --------------------------------------------------------

    def process_job_description(
        self,
        job_id,
        jd_path
    ):

        jd_path = Path(jd_path)

        # Standardized result structure

        result = {

            "job_id": job_id,

            "jd_status": "NOT_PROCESSED",

            "jd_source": str(jd_path),

            "job_title": None,

            "company": None,

            "job_location": None,

            "employment_type": None,

            "experience_requirement": {

                "minimum_years": None,

                "maximum_years": None
            },

            "mandatory_skills": [],

            "preferred_skills": [],

            "education_requirement": [],

            "missing_fields": [],

            "warnings": [],

            "error": None
        }

        # ----------------------------------------------------
        # STEP 1: CHECK FILE EXISTENCE
        # ----------------------------------------------------

        if not jd_path.exists():

            result["jd_status"] = "MISSING"

            result["error"] = (
                "Job description file does not exist."
            )

            return result

        # ----------------------------------------------------
        # STEP 2: VALIDATE FILE FORMAT
        # ----------------------------------------------------

        if jd_path.suffix.lower() != ".txt":

            result["jd_status"] = "FAILED"

            result["error"] = (
                "Unsupported job description format."
            )

            return result

        try:

            # ------------------------------------------------
            # STEP 3: READ JOB DESCRIPTION
            # ------------------------------------------------

            text = jd_path.read_text(
                encoding="utf-8"
            )

            if not text.strip():

                result["jd_status"] = "FAILED"

                result["error"] = (
                    "Job description file is empty."
                )

                return result

            # ------------------------------------------------
            # STEP 4: EXTRACT BASIC INFORMATION
            # ------------------------------------------------

            result["job_title"] = self.extract_field(
                text,
                "JOB TITLE"
            )

            result["company"] = self.extract_field(
                text,
                "COMPANY"
            )

            result["job_location"] = self.extract_field(
                text,
                "JOB LOCATION"
            )

            result["employment_type"] = self.extract_field(
                text,
                "EMPLOYMENT TYPE"
            )

            # ------------------------------------------------
            # STEP 5: EXTRACT EXPERIENCE REQUIREMENT
            # ------------------------------------------------

            result["experience_requirement"] = (
                self.extract_experience_range(text)
            )

            # ------------------------------------------------
            # STEP 6: EXTRACT MANDATORY SKILLS
            # ------------------------------------------------

            result["mandatory_skills"] = (
                self.extract_section(
                    text,
                    "MANDATORY SKILLS",
                    [
                        "PREFERRED SKILLS",
                        "EDUCATIONAL QUALIFICATION",
                        "EXPERIENCE REQUIREMENT",
                        "ADDITIONAL REQUIREMENTS",
                        "JOB SUMMARY"
                    ]
                )
            )

            # ------------------------------------------------
            # STEP 7: EXTRACT PREFERRED SKILLS
            # ------------------------------------------------

            result["preferred_skills"] = (
                self.extract_section(
                    text,
                    "PREFERRED SKILLS",
                    [
                        "EDUCATIONAL QUALIFICATION",
                        "EXPERIENCE REQUIREMENT",
                        "ADDITIONAL REQUIREMENTS",
                        "JOB SUMMARY"
                    ]
                )
            )

            # ------------------------------------------------
            # STEP 8: EXTRACT EDUCATION REQUIREMENT
            # ------------------------------------------------

            result["education_requirement"] = (
                self.extract_section(
                    text,
                    "EDUCATIONAL QUALIFICATION",
                    [
                        "EXPERIENCE REQUIREMENT",
                        "ADDITIONAL REQUIREMENTS",
                        "JOB SUMMARY"
                    ]
                )
            )

            # ------------------------------------------------
            # STEP 9: VALIDATE REQUIRED FIELDS
            # ------------------------------------------------

            required_fields = [

                "job_title",

                "company",

                "mandatory_skills"
            ]

            for field in required_fields:

                if not result.get(field):

                    result["missing_fields"].append(
                        field
                    )

            # ------------------------------------------------
            # STEP 10: EXPERIENCE VALIDATION
            # ------------------------------------------------

            experience = result[
                "experience_requirement"
            ]

            if (
                experience["minimum_years"] is None
                or experience["maximum_years"] is None
            ):

                result["warnings"].append(
                    "Complete minimum and maximum "
                    "experience requirements were not detected."
                )

            # ------------------------------------------------
            # STEP 11: PREFERRED SKILLS VALIDATION
            # ------------------------------------------------

            if not result["preferred_skills"]:

                result["warnings"].append(
                    "No preferred skills were detected."
                )

            # ------------------------------------------------
            # STEP 12: FINAL STATUS
            # ------------------------------------------------

            if result["missing_fields"]:

                result["jd_status"] = "INCOMPLETE"

            else:

                result["jd_status"] = "PROCESSED"

            return result

        except Exception as error:

            result["jd_status"] = "FAILED"

            result["error"] = (
                f"{type(error).__name__}: {str(error)}"
            )

            return result


# ============================================================
# 3. BATCH JOB DESCRIPTION VALIDATION
# ============================================================

def batch_validate_job_descriptions():

    adapter = JDAdapter()

    # Get JD directory from shared configuration
    jd_directory = adapter.jd_directory

    if not jd_directory.exists():

        raise FileNotFoundError(
            f"Job description directory not found: "
            f"{jd_directory}"
        )

    # Discover all JD files dynamically
    jd_files = sorted(
        jd_directory.glob("JD*.txt")
    )

    total = len(jd_files)

    successful = 0

    failed = 0

    print(
        "\nZecPath - Configurable Batch JD Validation"
    )

    print("=" * 70)

    print("Dataset:", adapter.dataset_root)
    print("JD Directory:", jd_directory)

    if total == 0:

        print("No job description files found.")

        return

    # --------------------------------------------------------
    # PROCESS EACH JOB DESCRIPTION
    # --------------------------------------------------------

    for jd_path in jd_files:

        # Extract JD001 from JD001_mern_developer
        job_id = jd_path.stem.split("_")[0]

        output = adapter.process_job_description(
            job_id=job_id,
            jd_path=jd_path
        )

        print("\nJob ID:", output["job_id"])

        print(
            "Job Title:",
            output["job_title"]
        )

        print(
            "JD Status:",
            output["jd_status"]
        )

        print(
            "Mandatory Skills:",
            output["mandatory_skills"]
        )

        print(
            "Preferred Skills:",
            output["preferred_skills"]
        )

        print(
            "Experience:",
            output["experience_requirement"]
        )

        print(
            "Missing Fields:",
            output["missing_fields"]
        )

        print(
            "Warnings:",
            output["warnings"]
        )

        print(
            "Error:",
            output["error"]
        )

        if output["jd_status"] == "PROCESSED":

            successful += 1

        else:

            failed += 1

        print("-" * 70)

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\nFINAL SUMMARY")

    print("=" * 70)

    print("Total Job Descriptions:", total)

    print("Successful:", successful)

    print("Failed:", failed)

    if total > 0 and successful == total:

        print(
            "RESULT: ALL JOB DESCRIPTIONS "
            "PROCESSED SUCCESSFULLY"
        )

    else:

        print(
            "RESULT: SOME JOB DESCRIPTIONS "
            "NEED REVIEW"
        )


# ============================================================
# 4. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    batch_validate_job_descriptions()
