import json
import os
from typing import Dict, Any, List


# ============================================================
# ZecPath Day 47 - Technical Scoring Engine
# ============================================================
#
# Deliverable 1:
# Technical Scoring Engine
#
# Purpose:
# Evaluate the depth of technical knowledge beyond
# surface-level answers.
#
# The engine evaluates:
#   1. Accuracy of Answer
#   2. Depth of Explanation
#   3. Logical Reasoning
#   4. Real-World Applicability
#
# It also:
#   - Uses question-type-specific scoring rubrics
#   - Detects shallow vs deep answers
#   - Normalizes scores across difficulty levels
#   - Produces explainable scoring output
#   - Supports multiple technical skills/questions
#
# NOTE:
# The questions and parameter scores in this file are
# structured DEMO/TEST data, not real candidate interview data.
# ============================================================


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "technical_scores.json"
)


# ============================================================
# 1. SCORING RUBRIC PER QUESTION TYPE
# ============================================================

SCORING_WEIGHTS = {

    "conceptual": {
        "accuracy": 0.40,
        "depth": 0.30,
        "logical_reasoning": 0.15,
        "real_world_applicability": 0.15
    },

    "experience_based": {
        "accuracy": 0.30,
        "depth": 0.25,
        "logical_reasoning": 0.20,
        "real_world_applicability": 0.25
    },

    "scenario_based": {
        "accuracy": 0.25,
        "depth": 0.25,
        "logical_reasoning": 0.30,
        "real_world_applicability": 0.20
    },

    "technical_follow_up": {
        "accuracy": 0.30,
        "depth": 0.35,
        "logical_reasoning": 0.20,
        "real_world_applicability": 0.15
    }
}


# ============================================================
# 2. DIFFICULTY LEVELS
# ============================================================

DIFFICULTY_LEVELS = {
    "basic": {
        "expected_level": "Fundamental technical knowledge",
        "normalization_factor": 1.00
    },

    "intermediate": {
        "expected_level": "Practical and deeper technical knowledge",
        "normalization_factor": 1.00
    },

    "advanced": {
        "expected_level": "Advanced technical knowledge and problem solving",
        "normalization_factor": 1.00
    }
}


# ============================================================
# 3. SCORE CATEGORY
# ============================================================

def get_score_category(score: float) -> str:

    if score >= 90:
        return "excellent"

    if score >= 80:
        return "strong"

    if score >= 60:
        return "good"

    if score >= 40:
        return "basic"

    return "poor"


# ============================================================
# 4. NORMALIZE INDIVIDUAL SCORE
# ============================================================

def normalize_score(score: float) -> float:

    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    return round(
        max(0.0, min(100.0, score)),
        2
    )


# ============================================================
# 5. DETECT SHALLOW VS DEEP ANSWERS
# ============================================================

def detect_answer_depth(
    answer: str
) -> Dict[str, Any]:

    if not isinstance(answer, str):
        answer = ""

    cleaned_answer = answer.strip()

    if not cleaned_answer:

        return {
            "classification": "empty",
            "word_count": 0,
            "indicators": [],
            "explanation": (
                "No candidate answer was provided."
            )
        }

    words = cleaned_answer.split()

    word_count = len(words)

    answer_lower = cleaned_answer.lower()

    indicators = []

    # --------------------------------------------------------
    # Explanation indicators
    # --------------------------------------------------------

    explanation_keywords = [
        "because",
        "therefore",
        "how",
        "why",
        "process",
        "implementation",
        "works",
        "reason"
    ]

    # --------------------------------------------------------
    # Practical indicators
    # --------------------------------------------------------

    practical_keywords = [
        "example",
        "project",
        "production",
        "application",
        "real-world",
        "used",
        "implemented",
        "developed"
    ]

    # --------------------------------------------------------
    # Technical indicators
    # --------------------------------------------------------

    technical_keywords = [
        "api",
        "database",
        "authentication",
        "authorization",
        "performance",
        "optimization",
        "scalability",
        "architecture",
        "testing",
        "deployment",
        "security",
        "cache",
        "component",
        "state",
        "middleware",
        "query",
        "index"
    ]

    for keyword in explanation_keywords:

        if keyword in answer_lower:
            indicators.append(keyword)

    for keyword in practical_keywords:

        if keyword in answer_lower:
            indicators.append(keyword)

    for keyword in technical_keywords:

        if keyword in answer_lower:
            indicators.append(keyword)

    indicators = list(
        dict.fromkeys(indicators)
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if word_count < 15:

        classification = "shallow"

    elif word_count < 40 and len(indicators) < 2:

        classification = "basic"

    elif (
        word_count >= 80
        or len(indicators) >= 5
    ):

        classification = "deep"

    else:

        classification = "moderate"

    explanations = {

        "shallow": (
            "Answer contains limited explanation "
            "and technical depth."
        ),

        "basic": (
            "Answer demonstrates basic technical "
            "understanding with limited supporting detail."
        ),

        "moderate": (
            "Answer provides reasonable technical "
            "explanation and supporting details."
        ),

        "deep": (
            "Answer demonstrates detailed technical "
            "understanding with supporting explanation "
            "and practical context."
        )
    }

    return {

        "classification": classification,

        "word_count": word_count,

        "indicators": indicators,

        "explanation": explanations[
            classification
        ]
    }


# ============================================================
# 6. GET QUESTION-TYPE WEIGHTS
# ============================================================

def get_question_weights(
    question_type: str
) -> Dict[str, float]:

    question_type = (
        question_type
        .lower()
        .strip()
    )

    if question_type not in SCORING_WEIGHTS:

        question_type = "conceptual"

    return SCORING_WEIGHTS[
        question_type
    ]


# ============================================================
# 7. VALIDATE WEIGHTS
# ============================================================

def validate_weights(
    weights: Dict[str, float]
) -> bool:

    required_keys = {
        "accuracy",
        "depth",
        "logical_reasoning",
        "real_world_applicability"
    }

    if set(weights.keys()) != required_keys:

        return False

    total = sum(
        float(value)
        for value in weights.values()
    )

    return abs(total - 1.0) < 0.0001


# ============================================================
# 8. CALCULATE WEIGHTED SCORE
# ============================================================

def calculate_weighted_score(
    parameter_scores: Dict[str, float],
    weights: Dict[str, float]
) -> Dict[str, Any]:

    weighted_contributions = {}

    for parameter, weight in weights.items():

        score = normalize_score(
            parameter_scores.get(
                parameter,
                0
            )
        )

        contribution = (
            score * weight
        )

        weighted_contributions[
            parameter
        ] = round(
            contribution,
            2
        )

    final_score = sum(
        weighted_contributions.values()
    )

    return {

        "weighted_contributions":
            weighted_contributions,

        "technical_score":
            round(
                final_score,
                2
            )
    }


# ============================================================
# 9. NORMALIZE SCORE ACROSS DIFFICULTY
# ============================================================

def normalize_for_difficulty(
    score: float,
    difficulty: str
) -> float:

    difficulty = (
        difficulty
        .lower()
        .strip()
    )

    difficulty_data = DIFFICULTY_LEVELS.get(
        difficulty,
        DIFFICULTY_LEVELS["basic"]
    )

    factor = difficulty_data[
        "normalization_factor"
    ]

    normalized_score = (
        score * factor
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                normalized_score
            )
        ),
        2
    )


# ============================================================
# 10. GENERATE EXPLANATION
# ============================================================

def generate_explanation(
    parameter_scores: Dict[str, float],
    answer_depth: Dict[str, Any],
    final_score: float
) -> str:

    strongest_parameter = max(
        parameter_scores,
        key=parameter_scores.get
    )

    weakest_parameter = min(
        parameter_scores,
        key=parameter_scores.get
    )

    strongest_score = parameter_scores[
        strongest_parameter
    ]

    weakest_score = parameter_scores[
        weakest_parameter
    ]

    return (

        f"The candidate received a technical "
        f"score of {final_score:.2f}. "

        f"The strongest parameter was "
        f"{strongest_parameter} "
        f"({strongest_score:.2f}), "

        f"while the weakest parameter was "
        f"{weakest_parameter} "
        f"({weakest_score:.2f}). "

        f"The answer was classified as "
        f"{answer_depth['classification']}. "

        f"{answer_depth['explanation']}"
    )


# ============================================================
# 11. EVALUATE ONE TECHNICAL QUESTION
# ============================================================

def evaluate_technical_question(
    candidate_id: str,
    job_id: str,
    question: Dict[str, Any]
) -> Dict[str, Any]:

    question_type = question[
        "question_type"
    ]

    difficulty = question[
        "difficulty"
    ]

    parameter_scores = question[
        "parameter_scores"
    ]

    weights = get_question_weights(
        question_type
    )

    if not validate_weights(weights):

        raise ValueError(
            f"Invalid scoring weights for "
            f"{question_type}"
        )

    normalized_parameter_scores = {

        key: normalize_score(value)

        for key, value
        in parameter_scores.items()
    }

    answer_depth = detect_answer_depth(
        question["candidate_answer"]
    )

    weighted_result = calculate_weighted_score(
        normalized_parameter_scores,
        weights
    )

    original_score = weighted_result[
        "technical_score"
    ]

    normalized_score = normalize_for_difficulty(
        original_score,
        difficulty
    )

    explanation = generate_explanation(
        normalized_parameter_scores,
        answer_depth,
        normalized_score
    )

    return {

        "candidate_id": candidate_id,

        "job_id": job_id,

        "question": {

            "question_id": question[
                "question_id"
            ],

            "question_text": question[
                "question_text"
            ],

            "skill_domain": question[
                "skill_domain"
            ],

            "question_type": question_type,

            "difficulty": difficulty
        },

        "candidate_answer":
            question[
                "candidate_answer"
            ],

        "answer_analysis": {

            "depth_classification":
                answer_depth[
                    "classification"
                ],

            "word_count":
                answer_depth[
                    "word_count"
                ],

            "depth_indicators":
                answer_depth[
                    "indicators"
                ],

            "depth_explanation":
                answer_depth[
                    "explanation"
                ]
        },

        "parameter_scores":
            normalized_parameter_scores,

        "scoring_weights":
            weights,

        "weighted_contributions":
            weighted_result[
                "weighted_contributions"
            ],

        "score_summary": {

            "original_score":
                original_score,

            "difficulty_normalized_score":
                normalized_score,

            "score_category":
                get_score_category(
                    normalized_score
                )
        },

        "explainability": {

            "explanation":
                explanation,

            "formula": (
                "Accuracy × Weight + "
                "Depth × Weight + "
                "Logical Reasoning × Weight + "
                "Real-World Applicability × Weight"
            )
        }
    }


# ============================================================
# 12. DEMO TECHNICAL QUESTIONS
# ============================================================
#
# These are SAMPLE/DEMO inputs.
# They are not real candidate interview responses.
# ============================================================

DEMO_QUESTIONS = [

    {
        "question_id": "TECH_JS_001",

        "skill_domain": "JavaScript",

        "question_type": "conceptual",

        "difficulty": "basic",

        "question_text":
            "What is the difference between let, const and var in JavaScript?",

        "candidate_answer":
            (
                "let and const are block scoped. "
                "const cannot be reassigned after declaration, "
                "while let can be reassigned. "
                "var is function scoped and has different "
                "hoisting behavior."
            ),

        "parameter_scores": {

            "accuracy": 90,

            "depth": 82,

            "logical_reasoning": 80,

            "real_world_applicability": 78
        }
    },


    {
        "question_id": "TECH_REACT_001",

        "skill_domain": "React",

        "question_type": "experience_based",

        "difficulty": "intermediate",

        "question_text":
            "How have you used React components and state management in a project?",

        "candidate_answer":
            (
                "In a project, I used reusable React components to "
                "separate the user interface into smaller modules. "
                "I used state to manage changing data and passed "
                "data between components using props. For larger "
                "sections of the application, I organized state "
                "carefully so that components remained reusable. "
                "This helped make the application easier to maintain "
                "and test."
            ),

        "parameter_scores": {

            "accuracy": 88,

            "depth": 84,

            "logical_reasoning": 82,

            "real_world_applicability": 86
        }
    },


    {
        "question_id": "TECH_NODE_001",

        "skill_domain": "Node.js",

        "question_type": "scenario_based",

        "difficulty": "advanced",

        "question_text":
            (
                "How would you improve the performance of a "
                "Node.js API when the number of users increases?"
            ),

        "candidate_answer":
            (
                "I would first identify the performance bottleneck "
                "using monitoring and profiling tools. I would "
                "check database queries, API response time and CPU "
                "usage. Database queries can be optimized using "
                "indexes and efficient queries. I would also use "
                "caching where appropriate and consider asynchronous "
                "processing for time-consuming operations. In a "
                "production system, load balancing and horizontal "
                "scaling can be used when traffic increases. "
                "I would monitor the system after optimization "
                "to verify the improvement."
            ),

        "parameter_scores": {

            "accuracy": 90,

            "depth": 84,

            "logical_reasoning": 86,

            "real_world_applicability": 80
        }
    },


    {
        "question_id": "TECH_EXPRESS_001",

        "skill_domain": "Express.js",

        "question_type": "conceptual",

        "difficulty": "intermediate",

        "question_text":
            "What is middleware in Express.js and why is it useful?",

        "candidate_answer":
            (
                "Middleware functions execute during the request "
                "and response cycle. They can inspect requests, "
                "modify request or response objects, perform "
                "authentication, log requests, handle errors, "
                "and pass control to the next middleware or route."
            ),

        "parameter_scores": {

            "accuracy": 91,

            "depth": 85,

            "logical_reasoning": 82,

            "real_world_applicability": 84
        }
    },


    {
        "question_id": "TECH_MONGO_001",

        "skill_domain": "MongoDB",

        "question_type": "scenario_based",

        "difficulty": "intermediate",

        "question_text":
            (
                "A MongoDB query is becoming slow as the collection "
                "grows. How would you investigate and improve it?"
            ),

        "candidate_answer":
            (
                "I would inspect the query execution plan to "
                "understand how MongoDB is searching the collection. "
                "I would check whether suitable indexes exist for "
                "the fields used in filtering or sorting. I would "
                "also review the query structure and avoid retrieving "
                "unnecessary fields. After making changes, I would "
                "test the query again and compare performance."
            ),

        "parameter_scores": {

            "accuracy": 87,

            "depth": 82,

            "logical_reasoning": 88,

            "real_world_applicability": 85
        }
    }
]


# ============================================================
# 13. VALIDATE DEMO QUESTIONS
# ============================================================

def validate_questions(
    questions: List[Dict[str, Any]]
) -> None:

    required_fields = [

        "question_id",

        "skill_domain",

        "question_type",

        "difficulty",

        "question_text",

        "candidate_answer",

        "parameter_scores"
    ]

    question_ids = []

    for question in questions:

        missing = [

            field

            for field in required_fields

            if field not in question
        ]

        if missing:

            raise ValueError(
                "Missing fields in question "
                f"{question.get('question_id', 'UNKNOWN')}: "
                + ", ".join(missing)
            )

        if question[
            "question_id"
        ] in question_ids:

            raise ValueError(
                "Duplicate question ID: "
                + question[
                    "question_id"
                ]
            )

        question_ids.append(
            question[
                "question_id"
            ]
        )

        if question[
            "question_type"
        ] not in SCORING_WEIGHTS:

            raise ValueError(
                "Unsupported question type: "
                + question[
                    "question_type"
                ]
            )

        if question[
            "difficulty"
        ] not in DIFFICULTY_LEVELS:

            raise ValueError(
                "Unsupported difficulty: "
                + question[
                    "difficulty"
                ]
            )


# ============================================================
# 14. EVALUATE ALL QUESTIONS
# ============================================================

def evaluate_all_questions(
    candidate_id: str,
    job_id: str,
    questions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    validate_questions(
        questions
    )

    results = []

    for question in questions:

        result = evaluate_technical_question(
            candidate_id,
            job_id,
            question
        )

        results.append(
            result
        )

    return results


# ============================================================
# 15. BUILD FINAL OUTPUT
# ============================================================

def build_final_result(
    candidate_id: str,
    job_id: str,
    results: List[Dict[str, Any]]
) -> Dict[str, Any]:

    scores = [

        result[
            "score_summary"
        ][
            "difficulty_normalized_score"
        ]

        for result in results
    ]

    overall_score = (

        sum(scores) / len(scores)

        if scores

        else 0.0
    )

    skill_domains = list(
        dict.fromkeys(

            result[
                "question"
            ][
                "skill_domain"
            ]

            for result in results
        )
    )

    return {

        "engine": (
            "ZecPath Day 47 Technical "
            "Scoring Engine"
        ),

        "data_type": (
            "DEMO_SAMPLE_DATA"
        ),

        "candidate_id":
            candidate_id,

        "job_id":
            job_id,

        "evaluation_summary": {

            "total_questions":
                len(results),

            "total_skills":
                len(skill_domains),

            "skills_evaluated":
                skill_domains,

            "overall_technical_score":
                round(
                    overall_score,
                    2
                ),

            "overall_score_category":
                get_score_category(
                    overall_score
                )
        },

        "question_wise_scores":
            results,

        "scoring_parameters": [

            "accuracy",

            "depth",

            "logical_reasoning",

            "real_world_applicability"
        ],

        "answer_depth_levels": [

            "shallow",

            "basic",

            "moderate",

            "deep"
        ],

        "difficulty_levels": [

            "basic",

            "intermediate",

            "advanced"
        ],

        "explainability": {

            "scoring_formula": (
                "Accuracy × Weight + "
                "Depth × Weight + "
                "Logical Reasoning × Weight + "
                "Real-World Applicability × Weight"
            ),

            "description": (
                "Each technical answer is evaluated "
                "using question-type-specific weights. "
                "The resulting score is normalized to "
                "a 0-100 scale and accompanied by "
                "answer-depth and scoring explanations."
            )
        },

        "overall_status":
            "SUCCESS"
    }


# ============================================================
# 16. SAVE OUTPUT
# ============================================================

def save_result(
    result: Dict[str, Any]
) -> str:

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
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    return OUTPUT_FILE


# ============================================================
# 17. MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 65)

    print(
        "ZecPath Day 47 - Technical Scoring Engine"
    )

    print("=" * 65)

    try:

        candidate_id = "candidate_006"

        job_id = "JOB_BACKEND_001"

        print()
        print(
            "Data Type : DEMO / SAMPLE DATA"
        )

        print(
            "Candidate :",
            candidate_id
        )

        print(
            "Job       :",
            job_id
        )

        print()
        print(
            "Validating technical questions..."
        )

        validate_questions(
            DEMO_QUESTIONS
        )

        print(
            "Question Validation : PASS"
        )

        print()
        print(
            "Evaluating technical questions..."
        )

        results = evaluate_all_questions(
            candidate_id,
            job_id,
            DEMO_QUESTIONS
        )

        print()
        print(
            "Question-wise Technical Scores"
        )

        print("-" * 65)

        for result in results:

            question = result[
                "question"
            ]

            score = result[
                "score_summary"
            ][
                "difficulty_normalized_score"
            ]

            category = result[
                "score_summary"
            ][
                "score_category"
            ]

            depth = result[
                "answer_analysis"
            ][
                "depth_classification"
            ]

            print(
                f"{question['skill_domain']:<15}"
                f"Score: {score:>6.2f}   "
                f"Depth: {depth:<9}   "
                f"Category: {category}"
            )

        final_result = build_final_result(
            candidate_id,
            job_id,
            results
        )

        print()
        print(
            "Evaluation Summary"
        )

        print("-" * 65)

        print(
            "Total Questions        :",
            final_result[
                "evaluation_summary"
            ][
                "total_questions"
            ]
        )

        print(
            "Total Skills           :",
            final_result[
                "evaluation_summary"
            ][
                "total_skills"
            ]
        )

        print(
            "Skills Evaluated       :",
            ", ".join(
                final_result[
                    "evaluation_summary"
                ][
                    "skills_evaluated"
                ]
            )
        )

        print(
            "Overall Technical Score:",
            final_result[
                "evaluation_summary"
            ][
                "overall_technical_score"
            ]
        )

        print(
            "Overall Score Category :",
            final_result[
                "evaluation_summary"
            ][
                "overall_score_category"
            ]
        )

        output_path = save_result(
            final_result
        )

        print()
        print(
            "Result saved to:"
        )

        print(
            output_path
        )

        print()
        print(
            "Overall Status : SUCCESS"
        )

    except Exception as error:

        print()
        print(
            "Overall Status : FAILED"
        )

        print(
            "Error :",
            str(error)
        )