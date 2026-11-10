import json
import os
from datetime import datetime


# ============================================================
# ZecPath Day 47
# Technical Evaluation Report
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

TECHNICAL_SCORES_FILE = os.path.join(
    RESULTS_DIR,
    "technical_scores.json"
)

SKILL_WISE_SCORES_FILE = os.path.join(
    RESULTS_DIR,
    "skill_wise_scores.json"
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "technical_evaluation_report.json"
)


# ============================================================
# Utility Functions
# ============================================================

def load_json(file_path):
    """Load JSON data from a file."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def round_score(value):
    """Round numeric scores to two decimal places."""

    if value is None:
        return None

    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def get_score_category(score):
    """Convert score into evaluation category."""

    if score is None:
        return "needs_improvement"

    if score >= 80:
        return "strong"

    if score >= 60:
        return "moderate"

    return "needs_improvement"


def get_parameter_value(parameter_scores, parameter):
    """Safely retrieve a parameter score."""

    if not isinstance(parameter_scores, dict):
        return 0.0

    value = parameter_scores.get(parameter, 0.0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# ============================================================
# IMPORTANT:
# Extract data from the ACTUAL Day 47 technical_scores.json
# ============================================================

def extract_question_information(question_record):
    """
    Extract question information from the actual structure:

    question_wise_scores
        ├── question
        │   ├── question_id
        │   ├── question_text
        │   ├── skill_domain
        │   ├── question_type
        │   └── difficulty
        │
        ├── answer_analysis
        │   └── depth_classification
        │
        ├── parameter_scores
        │
        └── score_summary
            ├── original_score
            ├── difficulty_normalized_score
            └── score_category
    """

    question_data = question_record.get(
        "question",
        {}
    )

    answer_analysis = question_record.get(
        "answer_analysis",
        {}
    )

    parameter_scores = question_record.get(
        "parameter_scores",
        {}
    )

    score_summary = question_record.get(
        "score_summary",
        {}
    )

    # --------------------------------------------------------
    # Question metadata
    # --------------------------------------------------------

    question_id = question_data.get(
        "question_id"
    )

    question_text = question_data.get(
        "question_text"
    )

    skill = question_data.get(
        "skill_domain"
    )

    question_type = question_data.get(
        "question_type"
    )

    difficulty = question_data.get(
        "difficulty"
    )

    # --------------------------------------------------------
    # Answer depth
    # --------------------------------------------------------

    answer_depth = answer_analysis.get(
        "depth_classification"
    )

    # --------------------------------------------------------
    # Technical score
    # --------------------------------------------------------

    technical_score = score_summary.get(
        "difficulty_normalized_score"
    )

    if technical_score is None:
        technical_score = score_summary.get(
            "original_score"
        )

    # --------------------------------------------------------
    # Score category
    # --------------------------------------------------------

    score_category = score_summary.get(
        "score_category"
    )

    if not score_category:
        score_category = get_score_category(
            technical_score
        )

    return {
        "question_id": question_id,
        "question_text": question_text,
        "skill": skill,
        "question_type": question_type,
        "difficulty": difficulty,
        "answer_depth": answer_depth,
        "technical_score": round_score(
            technical_score
        ),
        "score_category": score_category,
        "parameter_scores": parameter_scores
    }


# ============================================================
# Parameter Analysis
# ============================================================

def find_strongest_parameter(parameter_scores):
    """Find strongest scoring parameter."""

    if not parameter_scores:
        return {
            "parameter": None,
            "score": 0.0
        }

    strongest = max(
        parameter_scores,
        key=parameter_scores.get
    )

    return {
        "parameter": strongest,
        "score": round_score(
            parameter_scores[strongest]
        )
    }


def find_weakest_parameter(parameter_scores):
    """Find weakest scoring parameter."""

    if not parameter_scores:
        return {
            "parameter": None,
            "score": 0.0
        }

    weakest = min(
        parameter_scores,
        key=parameter_scores.get
    )

    return {
        "parameter": weakest,
        "score": round_score(
            parameter_scores[weakest]
        )
    }


# ============================================================
# Explainability
# ============================================================

def build_explanation(
    technical_score,
    strongest_parameter,
    weakest_parameter,
    answer_depth
):
    """Generate explainable scoring information."""

    if technical_score is None:
        technical_score = 0.0

    strongest_name = (
        strongest_parameter["parameter"]
    )

    strongest_score = (
        strongest_parameter["score"]
    )

    weakest_name = (
        weakest_parameter["parameter"]
    )

    weakest_score = (
        weakest_parameter["score"]
    )

    if answer_depth == "deep":

        depth_description = (
            "Answer demonstrates detailed technical "
            "understanding with supporting explanation "
            "and practical context."
        )

    elif answer_depth == "moderate":

        depth_description = (
            "Answer provides reasonable technical "
            "explanation and supporting details."
        )

    elif answer_depth == "basic":

        depth_description = (
            "Answer demonstrates basic technical "
            "understanding with limited supporting detail."
        )

    elif answer_depth == "shallow":

        depth_description = (
            "Answer provides limited technical "
            "explanation and supporting detail."
        )

    else:

        depth_description = (
            "Answer depth could not be determined."
        )

    explanation = (
        f"The candidate received a technical score of "
        f"{technical_score:.2f}. "
        f"The strongest parameter was "
        f"{strongest_name} ({strongest_score:.2f}), "
        f"while the weakest parameter was "
        f"{weakest_name} ({weakest_score:.2f}). "
        f"The answer was classified as "
        f"{answer_depth}. "
        f"{depth_description}"
    )

    return {
        "explanation": explanation,
        "formula": (
            "Accuracy × Weight + Depth × Weight + "
            "Logical Reasoning × Weight + "
            "Real-World Applicability × Weight"
        )
    }


# ============================================================
# Build Question Evaluation
# ============================================================

def build_question_evaluation(
    question_record,
    question_number
):
    """Build a clean question-wise evaluation."""

    information = extract_question_information(
        question_record
    )

    parameter_scores = information[
        "parameter_scores"
    ]

    strongest_parameter = (
        find_strongest_parameter(
            parameter_scores
        )
    )

    weakest_parameter = (
        find_weakest_parameter(
            parameter_scores
        )
    )

    explanation = build_explanation(
        information["technical_score"],
        strongest_parameter,
        weakest_parameter,
        information["answer_depth"]
    )

    return {

        "question_number":
            question_number,

        "question_id":
            information["question_id"],

        "question_text":
            information["question_text"],

        "skill":
            information["skill"],

        "question_type":
            information["question_type"],

        "difficulty":
            information["difficulty"],

        "technical_score":
            information["technical_score"],

        "answer_depth":
            information["answer_depth"],

        "score_category":
            information["score_category"],

        "parameter_scores": {

            "accuracy":
                round_score(
                    get_parameter_value(
                        parameter_scores,
                        "accuracy"
                    )
                ),

            "depth":
                round_score(
                    get_parameter_value(
                        parameter_scores,
                        "depth"
                    )
                ),

            "logical_reasoning":
                round_score(
                    get_parameter_value(
                        parameter_scores,
                        "logical_reasoning"
                    )
                ),

            "real_world_applicability":
                round_score(
                    get_parameter_value(
                        parameter_scores,
                        "real_world_applicability"
                    )
                )
        },

        "strongest_parameter":
            strongest_parameter,

        "weakest_parameter":
            weakest_parameter,

        "explainability":
            explanation
    }


# ============================================================
# Build Skill-wise Evaluation
# ============================================================

def build_skill_wise_evaluation(
    question_evaluations
):
    """Group evaluated questions by technical skill."""

    skill_groups = {}

    for question in question_evaluations:

        skill = question.get(
            "skill"
        )

        if not skill:
            continue

        if skill not in skill_groups:
            skill_groups[skill] = []

        skill_groups[skill].append(
            question
        )

    skill_wise_evaluation = {}

    for skill, questions in skill_groups.items():

        parameter_values = {
            "accuracy": [],
            "depth": [],
            "logical_reasoning": [],
            "real_world_applicability": []
        }

        technical_scores = []

        for question in questions:

            score = question.get(
                "technical_score"
            )

            if score is not None:
                technical_scores.append(
                    score
                )

            for parameter in parameter_values:

                value = question[
                    "parameter_scores"
                ].get(parameter)

                if value is not None:
                    parameter_values[
                        parameter
                    ].append(value)

        # ----------------------------------------------------
        # Parameter averages
        # ----------------------------------------------------

        parameter_averages = {}

        for parameter, values in (
            parameter_values.items()
        ):

            if values:

                parameter_averages[
                    parameter
                ] = round_score(
                    sum(values) / len(values)
                )

            else:

                parameter_averages[
                    parameter
                ] = 0.0

        # ----------------------------------------------------
        # Skill score
        # ----------------------------------------------------

        if technical_scores:

            skill_score = round_score(
                sum(technical_scores)
                / len(technical_scores)
            )

        else:

            skill_score = 0.0

        skill_wise_evaluation[skill] = {

            "skill_score":
                skill_score,

            "category":
                get_score_category(
                    skill_score
                ),

            "question_count":
                len(questions),

            "parameter_averages":
                parameter_averages,

            "strongest_parameter":
                find_strongest_parameter(
                    parameter_averages
                ),

            "weakest_parameter":
                find_weakest_parameter(
                    parameter_averages
                ),

            "question_details":
                questions
        }

    return skill_wise_evaluation


# ============================================================
# Parameter Summary
# ============================================================

def build_parameter_summary(
    question_evaluations
):
    """Calculate overall parameter averages."""

    parameter_values = {
        "accuracy": [],
        "depth": [],
        "logical_reasoning": [],
        "real_world_applicability": []
    }

    for question in question_evaluations:

        scores = question.get(
            "parameter_scores",
            {}
        )

        for parameter in parameter_values:

            value = scores.get(
                parameter
            )

            if value is not None:

                parameter_values[
                    parameter
                ].append(value)

    summary = {}

    for parameter, values in (
        parameter_values.items()
    ):

        if values:

            summary[parameter] = round_score(
                sum(values) / len(values)
            )

        else:

            summary[parameter] = 0.0

    return summary


# ============================================================
# Strengths
# ============================================================

def build_strengths(
    skill_wise_evaluation,
    parameter_summary
):
    """Build strengths list."""

    strengths = []

    for skill, skill_data in (
        skill_wise_evaluation.items()
    ):

        score = skill_data[
            "skill_score"
        ]

        if score >= 80:

            strengths.append(
                f"{skill} demonstrates strong "
                f"technical performance "
                f"({score}/100)."
            )

    if parameter_summary:

        strongest_parameter = max(
            parameter_summary,
            key=parameter_summary.get
        )

        strengths.append(
            f"{strongest_parameter.replace('_', ' ').title()} "
            f"is the strongest overall parameter with "
            f"an average score of "
            f"{parameter_summary[strongest_parameter]}/100."
        )

    return strengths


# ============================================================
# Areas for Improvement
# ============================================================

def build_improvement_areas(
    skill_wise_evaluation,
    parameter_summary
):
    """Build improvement areas."""

    improvements = []

    for skill, skill_data in (
        skill_wise_evaluation.items()
    ):

        score = skill_data[
            "skill_score"
        ]

        if score < 60:

            improvements.append(
                f"{skill} requires improvement "
                f"({score}/100)."
            )

    if parameter_summary:

        weakest_parameter = min(
            parameter_summary,
            key=parameter_summary.get
        )

        improvements.append(
            f"{weakest_parameter.replace('_', ' ').title()} "
            f"is the lowest overall parameter with "
            f"an average score of "
            f"{parameter_summary[weakest_parameter]}/100."
        )

    return improvements


# ============================================================
# MAIN
# ============================================================

def generate_report():

    print("=" * 65)
    print(
        "ZecPath Day 47 - Technical Evaluation Report"
    )
    print("=" * 65)

    # --------------------------------------------------------
    # Load Deliverable 1
    # --------------------------------------------------------

    print(
        "\nLoading Deliverable 1 technical scores..."
    )

    technical_data = load_json(
        TECHNICAL_SCORES_FILE
    )

    print(
        "Technical scores : PASS"
    )

    # --------------------------------------------------------
    # Load Deliverable 2
    # --------------------------------------------------------

    print(
        "\nLoading Deliverable 2 skill-wise scores..."
    )

    skill_wise_data = load_json(
        SKILL_WISE_SCORES_FILE
    )

    print(
        "Skill-wise scores : PASS"
    )

    # --------------------------------------------------------
    # Candidate information
    # --------------------------------------------------------

    candidate_id = technical_data.get(
        "candidate_id"
    )

    job_id = technical_data.get(
        "job_id"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Actual key is question_wise_scores
    # --------------------------------------------------------

    question_records = technical_data.get(
        "question_wise_scores",
        []
    )

    # --------------------------------------------------------
    # Build question evaluations FIRST
    # --------------------------------------------------------

    question_wise_evaluation = []

    for index, question_record in enumerate(
        question_records,
        start=1
    ):

        evaluated_question = (
            build_question_evaluation(
                question_record,
                index
            )
        )

        question_wise_evaluation.append(
            evaluated_question
        )

    # --------------------------------------------------------
    # Build skill-wise evaluation
    # --------------------------------------------------------

    skill_wise_evaluation = (
        build_skill_wise_evaluation(
            question_wise_evaluation
        )
    )

    # --------------------------------------------------------
    # Build parameter summary
    # --------------------------------------------------------

    parameter_summary = (
        build_parameter_summary(
            question_wise_evaluation
        )
    )

    # --------------------------------------------------------
    # Overall score
    # --------------------------------------------------------

    summary = skill_wise_data.get(
        "summary",
        {}
    )

    overall_score = summary.get(
        "overall_technical_skill_score"
    )

    if overall_score is None:

        overall_score = (
            technical_data
            .get("evaluation_summary", {})
            .get("overall_technical_score")
        )

    overall_score = round_score(
        overall_score
    )

    # --------------------------------------------------------
    # Overall category
    # --------------------------------------------------------

    overall_category = summary.get(
        "overall_score_category"
    )

    if not overall_category:

        overall_category = (
            technical_data
            .get("evaluation_summary", {})
            .get("overall_score_category")
        )

    if not overall_category:

        overall_category = get_score_category(
            overall_score
        )

    # --------------------------------------------------------
    # Strong and weak skills
    # --------------------------------------------------------

    strong_skills = []

    skills_needing_improvement = []

    for skill, skill_data in (
        skill_wise_evaluation.items()
    ):

        score = skill_data[
            "skill_score"
        ]

        if score >= 80:

            strong_skills.append(
                skill
            )

        elif score < 60:

            skills_needing_improvement.append(
                skill
            )

    # --------------------------------------------------------
    # Strengths
    # --------------------------------------------------------

    strengths = build_strengths(
        skill_wise_evaluation,
        parameter_summary
    )

    # --------------------------------------------------------
    # Improvements
    # --------------------------------------------------------

    improvements = (
        build_improvement_areas(
            skill_wise_evaluation,
            parameter_summary
        )
    )

    # --------------------------------------------------------
    # Final Report
    # --------------------------------------------------------

    report = {

        "report_metadata": {

            "report_name":
                "ZecPath Day 47 Technical Evaluation Report",

            "generated_at":
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),

            "data_type":
                "DEMO / SAMPLE DATA",

            "report_status":
                "SUCCESS"
        },

        "candidate_information": {

            "candidate_id":
                candidate_id,

            "job_id":
                job_id
        },

        "evaluation_summary": {

            "total_questions":
                len(question_wise_evaluation),

            "total_skills":
                len(skill_wise_evaluation),

            "overall_technical_score":
                overall_score,

            "overall_score_category":
                overall_category
        },

        "skill_wise_evaluation":
            skill_wise_evaluation,

        "parameter_wise_summary":
            parameter_summary,

        "question_wise_evaluation":
            question_wise_evaluation,

        "final_evaluation": {

            "overall_technical_score":
                overall_score,

            "overall_score_category":
                overall_category,

            "strong_skills":
                strong_skills,

            "skills_needing_improvement":
                skills_needing_improvement,

            "evaluation_basis": [
                "Accuracy of answer",
                "Depth of explanation",
                "Logical reasoning",
                "Real-world applicability"
            ],

            "strengths":
                strengths,

            "areas_for_improvement":
                improvements
        },

        "explainability": {

            "scoring_method":
                "Each skill score is the average of the "
                "normalized technical scores of questions "
                "belonging to that skill. The overall "
                "technical skill score is the average "
                "of the skill scores.",

            "parameter_summary":
                parameter_summary,

            "interpretation":
                f"The candidate achieved an overall "
                f"technical score of "
                f"{overall_score}/100. "
                f"The evaluation category is "
                f"'{overall_category}'.",

            "data_note":
                "This evaluation is generated from "
                "DEMO / SAMPLE technical interview data "
                "for system demonstration and validation. "
                "It is not a real candidate interview."
        }
    }

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation_passed = True

    for question in question_wise_evaluation:

        required_fields = [
            question.get("question_id"),
            question.get("question_text"),
            question.get("skill"),
            question.get("question_type"),
            question.get("difficulty"),
            question.get("technical_score"),
            question.get("answer_depth")
        ]

        if any(
            value is None
            for value in required_fields
        ):
            validation_passed = False
            break

    # --------------------------------------------------------
    # Terminal Output
    # --------------------------------------------------------

    print(
        "\nTechnical Evaluation Report"
    )

    print("-" * 65)

    print(
        f"Candidate ID              : "
        f"{candidate_id}"
    )

    print(
        f"Job ID                    : "
        f"{job_id}"
    )

    print(
        f"Total Questions           : "
        f"{len(question_wise_evaluation)}"
    )

    print(
        f"Total Skills              : "
        f"{len(skill_wise_evaluation)}"
    )

    print(
        f"Overall Technical Score   : "
        f"{overall_score}"
    )

    print(
        f"Overall Score Category    : "
        f"{overall_category}"
    )

    print(
        "\nSkill-wise Evaluation"
    )

    for skill, skill_data in (
        skill_wise_evaluation.items()
    ):

        print(
            f"{skill:<15} "
            f"Score: "
            f"{skill_data['skill_score']:<6} "
            f"Category: "
            f"{skill_data['category']}"
        )

    print(
        "\nParameter-wise Summary"
    )

    for parameter, score in (
        parameter_summary.items()
    ):

        print(
            f"{parameter:<30}: {score}"
        )

    print(
        "\nQuestion-wise Validation"
    )

    for question in question_wise_evaluation:

        print(
            f"Q{question['question_number']} "
            f"{question['question_id']} | "
            f"{question['question_type']} | "
            f"{question['difficulty']} | "
            f"Score: "
            f"{question['technical_score']}"
        )

    print(
        "\nQuestion Metadata Validation : "
        f"{'PASS' if validation_passed else 'FAIL'}"
    )

    print(
        "\nReport saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nOverall Status : "
        f"{'SUCCESS' if validation_passed else 'WARNING'}"
    )

    print("=" * 65)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    generate_report()