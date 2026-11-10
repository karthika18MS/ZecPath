
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime


# ============================================================
# ZECPath - DAY 63
# CONFIGURABLE ATS INPUT PREPARATION PIPELINE
# ============================================================
#
# PURPOSE:
# 1. Dynamically load candidate profiles.
# 2. Load dataset using shared configuration.
# 3. Process candidate resumes.
# 4. Process related job descriptions.
# 5. Prepare structured ATS input.
# 6. Identify missing or invalid input.
# 7. Preserve source and data provenance.
# 8. Save results as JSON.
#
# IMPORTANT:
# READY_FOR_ATS means input preparation is complete.
# It does NOT mean the candidate passed ATS scoring.
#
# RUN:
# python day63_demo_dataset\06_end_to_end_simulation\pipeline\ats_input_pipeline.py
# ============================================================


# ============================================================
# 1. PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SIMULATION_ROOT = Path(__file__).resolve().parents[1]

# Add project root to Python path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Add simulation root to Python path
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))


# ============================================================
# 2. IMPORT REQUIRED MODULES
# ============================================================

try:

    from config_loader import SimulationConfig

    from loaders.dataset_loader import DatasetLoader

    from adapters.resume_adapter import ResumeAdapter

    from adapters.jd_adapter import JDAdapter

except ImportError as import_error:

    print("\nIMPORT ERROR")
    print("--------------------------------------------")
    print(import_error)

    print("\nCheck that these files exist:")
    print("06_end_to_end_simulation/config_loader.py")
    print("06_end_to_end_simulation/loaders/dataset_loader.py")
    print("06_end_to_end_simulation/adapters/resume_adapter.py")
    print("06_end_to_end_simulation/adapters/jd_adapter.py")

    raise


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def path_to_string(value):
    """Convert Path objects to JSON-compatible strings."""

    if value is None:
        return None

    return str(value)


def safe_dict(value):
    """Return a dictionary or an empty dictionary."""

    if isinstance(value, dict):
        return value

    return {}


def get_profile_value(profile, *keys, default=None):
    """Read a profile value using possible field names."""

    profile = safe_dict(profile)

    for key in keys:

        value = profile.get(key)

        if value is not None:
            return value

    return default


def save_json(data, file_path):
    """Save results as formatted JSON."""

    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with file_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )


def get_resume_status(resume_result):
    """Extract resume processing status."""

    return resume_result.get(
        "resume_status",
        "UNKNOWN"
    )


def get_jd_status(jd_result):
    """Extract job description processing status."""

    return jd_result.get(
        "jd_status",
        "UNKNOWN"
    )


# ============================================================
# 4. ATS INPUT PIPELINE
# ============================================================

class ATSInputPipeline:

    def __init__(self):

        print("\nInitializing ZecPath ATS Input Pipeline...")

        # ----------------------------------------------------
        # Load shared configuration
        # ----------------------------------------------------

        self.config = SimulationConfig()

        # ----------------------------------------------------
        # Resolve dataset configuration
        # ----------------------------------------------------

        self.dataset_root = self.config.dataset_root

        self.dataset_name = self.dataset_root.name

        self.dataset_type = self.config.dataset_type

        # ----------------------------------------------------
        # Resolve output directory
        # ----------------------------------------------------

        # Outputs remain inside the current simulation
        # environment, even when the dataset is changed.

        self.output_dir = SIMULATION_ROOT / "outputs"

        self.output_file = (
            self.output_dir / "ats_input_results.json"
        )

        # ----------------------------------------------------
        # Initialize dataset loader
        # ----------------------------------------------------

        self.loader = DatasetLoader(
            self.dataset_root
        )

        # ----------------------------------------------------
        # Initialize processing adapters
        # ----------------------------------------------------

        self.resume_adapter = ResumeAdapter()

        self.jd_adapter = JDAdapter()

        # ----------------------------------------------------
        # Initialize processing state
        # ----------------------------------------------------

        self.jd_cache = {}

        self.results = []

        self.summary = {
            "total_candidates": 0,
            "ready_for_ats": 0,
            "blocked_resume": 0,
            "blocked_jd": 0,
            "blocked_resume_and_jd": 0,
            "processing_errors": 0
        }

        print("Pipeline initialized successfully.")

        print("Dataset Name:", self.dataset_name)
        print("Dataset Type:", self.dataset_type)
        print("Dataset Root:", self.dataset_root)
        print("Output Directory:", self.output_dir)

    # ========================================================
    # 5. PROCESS JOB DESCRIPTION
    # ========================================================

    def process_jd(self, job_id, jd_path):

        if not job_id:

            return {
                "job_id": None,
                "jd_status": "MISSING",
                "error": "Job ID not available."
            }

        if not jd_path:

            return {
                "job_id": job_id,
                "jd_status": "MISSING",
                "error": "Job description file not found."
            }

        jd_path = Path(jd_path)

        if not jd_path.exists():

            return {
                "job_id": job_id,
                "jd_status": "MISSING",
                "error": "Job description file does not exist."
            }

        # Reuse previously processed JD.
        if job_id in self.jd_cache:

            return self.jd_cache[job_id]

        try:

            jd_result = self.jd_adapter.process_job_description(
                job_id,
                jd_path
            )

            self.jd_cache[job_id] = jd_result

            return jd_result

        except Exception as error:

            return {
                "job_id": job_id,
                "jd_status": "FAILED",
                "error": str(error)
            }

    # ========================================================
    # 6. PROCESS RESUME
    # ========================================================

    def process_resume(self, candidate_id, resume_path):

        if not resume_path:

            return {
                "candidate_id": candidate_id,
                "resume_status": "MISSING",
                "resume_source": None,
                "entities": {},
                "missing_fields": [],
                "warnings": [],
                "error": "Resume file not provided."
            }

        resume_path = Path(resume_path)

        if not resume_path.exists():

            return {
                "candidate_id": candidate_id,
                "resume_status": "MISSING",
                "resume_source": str(resume_path),
                "entities": {},
                "missing_fields": [],
                "warnings": [],
                "error": "Resume file does not exist."
            }

        try:

            return self.resume_adapter.process_resume(
                candidate_id,
                resume_path
            )

        except Exception as error:

            return {
                "candidate_id": candidate_id,
                "resume_status": "FAILED",
                "resume_source": str(resume_path),
                "entities": {},
                "missing_fields": [],
                "warnings": [],
                "error": str(error)
            }

    # ========================================================
    # 7. PREPARE STRUCTURED ATS INPUT
    # ========================================================

    def prepare_ats_input(
        self,
        candidate,
        resume_result,
        jd_result
    ):

        candidate_id = candidate.get(
            "candidate_id"
        )

        job_id = candidate.get(
            "job_id"
        )

        profile = safe_dict(
            candidate.get("profile")
        )

        resume_entities = safe_dict(
            resume_result.get("entities")
        )

        resume_status = get_resume_status(
            resume_result
        )

        jd_status = get_jd_status(
            jd_result
        )

        # ----------------------------------------------------
        # Determine input readiness
        # ----------------------------------------------------

        resume_ready = (
            resume_status == "PROCESSED"
        )

        jd_ready = (
            jd_status == "PROCESSED"
        )

        if resume_ready and jd_ready:

            input_status = "READY_FOR_ATS"

        elif not resume_ready and not jd_ready:

            input_status = "BLOCKED_RESUME_AND_JD"

        elif not resume_ready:

            input_status = "BLOCKED_RESUME"

        else:

            input_status = "BLOCKED_JD"

        # ----------------------------------------------------
        # Candidate information
        # ----------------------------------------------------

        candidate_information = {

            "candidate_id": candidate_id,

            "name": get_profile_value(
                profile,
                "name",
                "candidate_name",
                default=resume_entities.get("name")
            ),

            "email": get_profile_value(
                profile,
                "email",
                "email_address"
            ),

            "phone": get_profile_value(
                profile,
                "phone",
                "phone_number"
            ),

            "job_id": job_id,

            "target_role": get_profile_value(
                profile,
                "target_role",
                "job_title",
                "applied_role"
            ),

            "experience_years": get_profile_value(
                profile,
                "experience_years",
                "experience"
            ),

            "education": get_profile_value(
                profile,
                "education",
                "qualification",
                "degree"
            )
        }

        # ----------------------------------------------------
        # Resume information
        # ----------------------------------------------------

        resume_information = {

            "resume_status": resume_status,

            "resume_source": path_to_string(
                resume_result.get("resume_source")
            ),

            "raw_text_characters": resume_result.get(
                "raw_text_characters"
            ),

            "cleaned_text_characters": resume_result.get(
                "cleaned_text_characters"
            ),

            "cleaned_text": resume_result.get(
                "cleaned_text"
            ),

            "extracted_entities": resume_entities,

            "missing_fields": resume_result.get(
                "missing_fields",
                []
            ),

            "warnings": resume_result.get(
                "warnings",
                []
            ),

            "error": resume_result.get("error")
        }

        # ----------------------------------------------------
        # Job description information
        # ----------------------------------------------------

        job_information = {

            "job_id": job_id,

            "jd_status": jd_status,

            "jd_source": path_to_string(
                jd_result.get("jd_source")
            ),

            "job_title": jd_result.get(
                "job_title"
            ),

            "company": jd_result.get(
                "company"
            ),

            "job_location": jd_result.get(
                "job_location"
            ),

            "employment_type": jd_result.get(
                "employment_type"
            ),

            "experience_requirement": jd_result.get(
                "experience_requirement",
                {}
            ),

            "mandatory_skills": jd_result.get(
                "mandatory_skills",
                []
            ),

            "preferred_skills": jd_result.get(
                "preferred_skills",
                []
            ),

            "education_requirement": jd_result.get(
                "education_requirement"
            ),

            "missing_fields": jd_result.get(
                "missing_fields",
                []
            ),

            "warnings": jd_result.get(
                "warnings",
                []
            ),

            "error": jd_result.get("error")
        }

        # ----------------------------------------------------
        # Final structured ATS input
        # ----------------------------------------------------

        ats_input = {

            "candidate_id": candidate_id,

            "job_id": job_id,

            "candidate_information": candidate_information,

            "resume_information": resume_information,

            "job_information": job_information,

            "input_status": input_status,

            "ats_scoring_status": "NOT_STARTED",

            "data_provenance": {

                "dataset": self.dataset_name,

                "dataset_root": str(self.dataset_root),

                "dataset_type": self.dataset_type,

                "profile_source": path_to_string(
                    candidate.get("profile_source")
                ),

                "resume_source": path_to_string(
                    resume_result.get("resume_source")
                ),

                "job_description_source": path_to_string(
                    jd_result.get("jd_source")
                ),

                "generated_at": datetime.now().isoformat(),

                "processing_stage": "ATS_INPUT_PREPARATION",

                "data_type": self.dataset_type
            }
        }

        return ats_input

    # ========================================================
    # 8. PROCESS ONE CANDIDATE
    # ========================================================

    def process_candidate(self, candidate):

        candidate_id = candidate.get(
            "candidate_id",
            "UNKNOWN"
        )

        job_id = candidate.get(
            "job_id"
        )

        print("\n" + "=" * 60)

        print(
            f"Processing Candidate: {candidate_id}"
        )

        print("=" * 60)

        # ----------------------------------------------------
        # Resume processing
        # ----------------------------------------------------

        resume_path = candidate.get(
            "resume"
        )

        resume_result = self.process_resume(
            candidate_id,
            resume_path
        )

        print(
            "Resume Status:",
            get_resume_status(resume_result)
        )

        # ----------------------------------------------------
        # JD processing
        # ----------------------------------------------------

        jd_path = candidate.get(
            "job_description"
        )

        jd_result = self.process_jd(
            job_id,
            jd_path
        )

        print(
            "JD Status:",
            get_jd_status(jd_result)
        )

        # ----------------------------------------------------
        # Prepare ATS input
        # ----------------------------------------------------

        ats_input = self.prepare_ats_input(
            candidate,
            resume_result,
            jd_result
        )

        print(
            "Input Status:",
            ats_input["input_status"]
        )

        return ats_input

    # ========================================================
    # 9. UPDATE SUMMARY
    # ========================================================

    def update_summary(self, result):

        self.summary["total_candidates"] += 1

        status = result.get(
            "input_status"
        )

        if status == "READY_FOR_ATS":

            self.summary["ready_for_ats"] += 1

        elif status == "BLOCKED_RESUME":

            self.summary["blocked_resume"] += 1

        elif status == "BLOCKED_JD":

            self.summary["blocked_jd"] += 1

        elif status == "BLOCKED_RESUME_AND_JD":

            self.summary[
                "blocked_resume_and_jd"
            ] += 1

    # ========================================================
    # 10. RUN COMPLETE DATASET
    # ========================================================

    def run(self):

        print("\n")
        print("#" * 60)
        print("ZECPath - CONFIGURABLE ATS INPUT PIPELINE")
        print("#" * 60)

        print("\nLoading candidate dataset...")

        dataset = self.loader.load_dataset()

        if not isinstance(dataset, dict):

            raise ValueError(
                "Dataset loader returned an invalid result."
            )

        candidates = dataset.get(
            "candidates",
            []
        )

        if not candidates:

            print("\nNo candidates found in the dataset.")

            return None

        print(
            f"\nCandidates discovered: {len(candidates)}"
        )

        print(
            "Dataset:",
            dataset.get("dataset_name")
        )

        # ----------------------------------------------------
        # Process each discovered candidate
        # ----------------------------------------------------

        for candidate in candidates:

            try:

                result = self.process_candidate(
                    candidate
                )

                self.results.append(result)

                self.update_summary(result)

            except Exception as error:

                candidate_id = candidate.get(
                    "candidate_id",
                    "UNKNOWN"
                )

                print(
                    f"\nERROR processing {candidate_id}: {error}"
                )

                traceback.print_exc()

                self.summary[
                    "processing_errors"
                ] += 1

                self.results.append({

                    "candidate_id": candidate_id,

                    "job_id": candidate.get("job_id"),

                    "input_status": "PROCESSING_ERROR",

                    "ats_scoring_status": "NOT_STARTED",

                    "error": str(error)
                })

        # ----------------------------------------------------
        # Determine pipeline status
        # ----------------------------------------------------

        if self.summary["processing_errors"] == 0:

            pipeline_status = "COMPLETED"

        else:

            pipeline_status = "COMPLETED_WITH_ERRORS"

        # ----------------------------------------------------
        # Build final output
        # ----------------------------------------------------

        final_output = {

            "engine": "ZecPath Day 63 ATS Input Preparation Pipeline",

            "pipeline_status": pipeline_status,

            "dataset_name": dataset.get(
                "dataset_name",
                self.dataset_name
            ),

            "dataset_root": str(self.dataset_root),

            "dataset_type": self.dataset_type,

            "generated_at": datetime.now().isoformat(),

            "summary": self.summary,

            "candidate_results": self.results
        }

        # ----------------------------------------------------
        # Save JSON output
        # ----------------------------------------------------

        save_json(
            final_output,
            self.output_file
        )

        # ----------------------------------------------------
        # Display final summary
        # ----------------------------------------------------

        self.display_summary()

        print("\nOutput saved successfully:")

        print(self.output_file)

        return final_output

    # ========================================================
    # 11. DISPLAY SUMMARY
    # ========================================================

    def display_summary(self):

        print("\n")
        print("=" * 60)
        print("ATS INPUT PIPELINE - FINAL SUMMARY")
        print("=" * 60)

        print(
            f"Total Candidates       : "
            f"{self.summary['total_candidates']}"
        )

        print(
            f"Ready for ATS          : "
            f"{self.summary['ready_for_ats']}"
        )

        print(
            f"Blocked - Resume       : "
            f"{self.summary['blocked_resume']}"
        )

        print(
            f"Blocked - JD           : "
            f"{self.summary['blocked_jd']}"
        )

        print(
            f"Blocked - Both         : "
            f"{self.summary['blocked_resume_and_jd']}"
        )

        print(
            f"Processing Errors      : "
            f"{self.summary['processing_errors']}"
        )

        print("-" * 60)

        expected_total = (
            self.summary["ready_for_ats"]
            + self.summary["blocked_resume"]
            + self.summary["blocked_jd"]
            + self.summary["blocked_resume_and_jd"]
            + self.summary["processing_errors"]
        )

        if (
            expected_total == self.summary["total_candidates"]
            and self.summary["processing_errors"] == 0
        ):

            print("PIPELINE RESULT: SUCCESS")

        else:

            print("PIPELINE RESULT: COMPLETED WITH ISSUES")

        print("=" * 60)


# ============================================================
# 12. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    try:

        pipeline = ATSInputPipeline()

        pipeline.run()

    except Exception as error:

        print("\nFATAL PIPELINE ERROR")
        print("--------------------------------------------")
        print(error)

        traceback.print_exc()
