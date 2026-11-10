
import json
import sys
import time
from pathlib import Path


# ---------------------------------------------------------
# PROJECT PATHS AND CONFIGURATION
# ---------------------------------------------------------

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SIMULATION_ROOT.parents[1]

# Make simulation modules importable.
sys.path.insert(0, str(SIMULATION_ROOT))

from config_loader import SimulationConfig


class HRAdapter:

    REQUIRED_SCORE_FIELDS = {
        "answer_relevance",
        "communication_score",
        "confidence_score",
        "consistency_score"
    }

    def __init__(self, dataset_root=None):

        self.config = SimulationConfig()

        # Optional dataset override; otherwise use pipeline_config.json.
        self.dataset_root = (
            Path(dataset_root).resolve()
            if dataset_root
            else self.config.dataset_root
        )

        self.hr_response_dir = (
            self.dataset_root
            / "04_candidate_responses"
            / "hr_responses"
        )

        self.output_dir = self.config.output_dir
        self.output_file = self.output_dir / "hr_results.json"

        # Existing Day 37 HR modules.
        day37_hr_dir = (
            self.config.project_root
            / "day37_hr_interview_scoring"
        )

        if not day37_hr_dir.exists():
            raise FileNotFoundError(
                f"Day 37 HR module directory not found: {day37_hr_dir}"
            )

        if str(day37_hr_dir) not in sys.path:
            sys.path.insert(0, str(day37_hr_dir))

        from hr_interview_scoring_engine import HRInterviewScoringEngine
        from candidate_hr_score_report import CandidateHRScoreReport

        self.engine = HRInterviewScoringEngine()
        self.report_generator = CandidateHRScoreReport()

        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("Initializing ZecPath HR Adapter...")
        print(f"Dataset: {self.config.dataset_name}")
        print(f"Dataset root: {self.dataset_root}")
        print(f"HR response directory: {self.hr_response_dir}")
        print("HR Adapter initialized successfully.")

    # -----------------------------------------------------
    # LOAD CANDIDATE HR RESPONSE
    # -----------------------------------------------------

    def load_candidate_response(self, file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "Candidate response must be a JSON object."
            )

        return data

    # -----------------------------------------------------
    # VALIDATE MANUAL EVALUATION SCORES
    # -----------------------------------------------------

    def validate_manual_scores(self, questions):

        missing_fields = []
        invalid_fields = []

        if not isinstance(questions, list) or not questions:
            return {
                "valid": False,
                "missing_fields": [],
                "invalid_fields": [],
                "error": "No interview questions found."
            }

        for index, question in enumerate(questions, start=1):

            if not isinstance(question, dict):
                invalid_fields.append({
                    "question_number": index,
                    "field": "question",
                    "reason": "Question must be a JSON object."
                })
                continue

            for field in self.REQUIRED_SCORE_FIELDS:

                if field not in question or question[field] is None:
                    missing_fields.append({
                        "question_number": index,
                        "field": field
                    })
                    continue

                value = question[field]

                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not 0 <= value <= 100
                ):
                    invalid_fields.append({
                        "question_number": index,
                        "field": field,
                        "value": value,
                        "reason": (
                            "Score must be a number between 0 and 100."
                        )
                    })

            for field in ("question_id", "question", "answer"):

                if not str(question.get(field, "")).strip():
                    invalid_fields.append({
                        "question_number": index,
                        "field": field,
                        "reason": "Required question information is missing."
                    })

        return {
            "valid": not missing_fields and not invalid_fields,
            "missing_fields": missing_fields,
            "invalid_fields": invalid_fields,
            "error": None
        }

    # -----------------------------------------------------
    # CONVERT DAY63 DATA TO DAY37 ENGINE FORMAT
    # -----------------------------------------------------

    def prepare_interview_questions(self, questions):

        prepared_questions = []

        for question in questions:
            prepared_questions.append({
                "question_id": question["question_id"],
                "question_text": question["question"],
                "candidate_answer": question["answer"],
                "answer_relevance": question["answer_relevance"],
                "communication_score": question["communication_score"],
                "confidence_score": question["confidence_score"],
                "consistency_score": question["consistency_score"]
            })

        return prepared_questions

    # -----------------------------------------------------
    # PROCESS ONE CANDIDATE
    # -----------------------------------------------------

    def process_candidate(self, file_path):

        candidate_id = file_path.stem
        job_id = None

        print("\n" + "=" * 55)
        print(f"Processing HR Candidate: {candidate_id}")
        print("=" * 55)

        try:
            data = self.load_candidate_response(file_path)

            candidate_id = data.get("candidate_id", candidate_id)
            job_id = data.get("job_id")

            if not isinstance(candidate_id, str) or not candidate_id.strip():
                raise ValueError("Invalid or missing candidate_id.")

            if not isinstance(job_id, str) or not job_id.strip():
                raise ValueError("Missing or invalid job_id.")

            response_status = str(
                data.get("response_status", "")
            ).strip().lower()

            if response_status != "completed":
                return {
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "status": "INCOMPLETE",
                    "hr_score": None,
                    "reason": "HR interview response is not completed."
                }

            questions = data.get("questions", [])

            validation = self.validate_manual_scores(questions)

            if validation["error"]:
                return {
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "status": "INVALID_DATA",
                    "hr_score": None,
                    "reason": validation["error"]
                }

            if validation["missing_fields"]:
                print("Manual evaluation scores are pending.")

                return {
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "status": "PENDING_MANUAL_EVALUATION",
                    "hr_score": None,
                    "total_questions": len(questions),
                    "missing_score_fields": validation["missing_fields"],
                    "invalid_score_fields": validation["invalid_fields"],
                    "reason": (
                        "Manual evaluation scores must be provided "
                        "for every interview question."
                    )
                }

            if validation["invalid_fields"]:
                return {
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "status": "INVALID_DATA",
                    "hr_score": None,
                    "invalid_fields": validation["invalid_fields"],
                    "reason": "Invalid HR response or evaluation score."
                }

            # Convert Day 63 JSON to Day 37 engine format.
            interview_questions = self.prepare_interview_questions(
                questions
            )

            # Run the existing Day 37 scoring engine.
            score_data = self.engine.score_interview(
                candidate_id=candidate_id,
                job_id=job_id,
                interview_questions=interview_questions
            )

            # Generate the existing Day 37 candidate report.
            report = self.report_generator.build_report(score_data)

            final_score = score_data["final_hr_interview_score"]

            score_category = (
                report["final_evaluation"]["score_category"]
            )

            print(f"Questions Processed: {len(questions)}")
            print(f"HR Score: {final_score}/100")
            print(f"Score Category: {score_category}")
            print("HR Processing: SUCCESS")

            return {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "status": "COMPLETED",
                "total_questions": len(questions),
                "hr_score": final_score,
                "score_category": score_category,
                "scoring_weights": score_data["scoring_weights"],
                "parameter_averages": score_data["parameter_averages"],
                "question_scores": score_data["question_scores"],
                "candidate_hr_report": report
            }

        except Exception as error:
            print(f"HR Processing Error: {error}")

            return {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "status": "ERROR",
                "hr_score": None,
                "reason": str(error)
            }

    # -----------------------------------------------------
    # RUN BATCH HR PROCESSING
    # -----------------------------------------------------

    def run(self):

        start_time = time.time()

        print("\n" + "#" * 60)
        print("ZECPath - CONFIGURABLE HR ADAPTER")
        print("#" * 60)

        if not self.hr_response_dir.exists():
            raise FileNotFoundError(
                "HR response directory not found: "
                f"{self.hr_response_dir}"
            )

        response_files = sorted(
            self.hr_response_dir.glob("*.json")
        )

        if not response_files:
            raise FileNotFoundError(
                "No candidate HR response JSON files found."
            )

        print(f"\nCandidate HR files found: {len(response_files)}")

        candidate_results = []

        for file_path in response_files:
            result = self.process_candidate(file_path)
            result["source_file"] = file_path.name
            candidate_results.append(result)

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        summary = {
            "total_candidates": len(candidate_results),

            "completed": sum(
                r["status"] == "COMPLETED"
                for r in candidate_results
            ),

            "pending_manual_evaluation": sum(
                r["status"] == "PENDING_MANUAL_EVALUATION"
                for r in candidate_results
            ),

            "incomplete": sum(
                r["status"] == "INCOMPLETE"
                for r in candidate_results
            ),

            "invalid_data": sum(
                r["status"] == "INVALID_DATA"
                for r in candidate_results
            ),

            "errors": sum(
                r["status"] == "ERROR"
                for r in candidate_results
            )
        }

        execution_time = round(time.time() - start_time, 4)

        output_data = {
            "engine": "ZecPath Configurable HR Adapter",
            "dataset": self.config.dataset_name,
            "dataset_type": self.config.dataset_type,
            "dataset_root": str(self.dataset_root),
            "pipeline_status": (
                "SUCCESS"
                if summary["errors"] == 0
                and summary["invalid_data"] == 0
                else "PARTIAL_SUCCESS"
            ),
            "execution_time_seconds": execution_time,
            "summary": summary,
            "candidate_results": candidate_results
        }

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        # -------------------------------------------------
        # FINAL SUMMARY
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("HR ADAPTER - FINAL SUMMARY")
        print("=" * 60)

        print(f"Dataset: {self.config.dataset_name}")
        print(f"Total Candidates: {summary['total_candidates']}")
        print(f"Completed: {summary['completed']}")
        print(
            "Pending Manual Evaluation: "
            f"{summary['pending_manual_evaluation']}"
        )
        print(f"Incomplete: {summary['incomplete']}")
        print(f"Invalid Data: {summary['invalid_data']}")
        print(f"Errors: {summary['errors']}")
        print(f"Execution Time: {execution_time} seconds")

        print("\nResults saved to:")
        print(self.output_file)

        print("\nHR Adapter execution completed.")

        return output_data


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    adapter = HRAdapter()
    adapter.run()
