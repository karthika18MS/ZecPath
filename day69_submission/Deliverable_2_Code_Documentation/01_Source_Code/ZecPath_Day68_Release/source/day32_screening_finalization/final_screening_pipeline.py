import json
import os
import sys
from datetime import datetime, timezone


# ============================================================
# DAY 32 — COMPLETE AI SCREENING SYSTEM
# ============================================================
#
# Final integration layer for the ZecPath AI Screening System.
#
# Existing modules:
#
# Day 25 -> Answer Understanding
# Day 26 -> Screening Scoring
# Day 27 -> Confidence / Sentiment / Behavioral Analysis
# Day 28 -> AI Screening Report
# Day 29 -> AI Conversation Flow
# Day 30 -> Optimization
# Day 31 -> Edge Case & Failure Handling
#
# Day 32 -> Complete System Integration
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DAY25_DIR = os.path.join(
    PROJECT_ROOT,
    "day25_answer_understanding"
)

DAY26_DIR = os.path.join(
    PROJECT_ROOT,
    "day26_screening_scoring"
)

DAY27_DIR = os.path.join(
    PROJECT_ROOT,
    "day27_confidence_sentiment"
)

DAY28_DIR = os.path.join(
    PROJECT_ROOT,
    "day28_ai_screening_report"
)

DAY29_DIR = os.path.join(
    PROJECT_ROOT,
    "day29_ai_conversation_flow"
)

DAY31_DIR = os.path.join(
    PROJECT_ROOT,
    "day31_edge_case_handling"
)


# ============================================================
# ADD REQUIRED DIRECTORIES TO PYTHON PATH
# ============================================================

for directory in [
    DAY25_DIR,
    DAY26_DIR,
    DAY27_DIR,
    DAY28_DIR,
    DAY29_DIR,
    DAY31_DIR
]:

    if directory not in sys.path:
        sys.path.insert(
            0,
            directory
        )


# ============================================================
# DAY 25 — ANSWER UNDERSTANDING
# ============================================================

from semantic_answer_builder import (
    SemanticAnswerBuilder
)


# ============================================================
# DAY 26 — SCREENING SCORING
# ============================================================

from screening_scoring_engine import (
    ScreeningScoringEngine
)


# ============================================================
# DAY 27 — CONFIDENCE
# ============================================================

from confidence_analyzer import (
    ConfidenceAnalyzer
)


# ============================================================
# DAY 27 — SENTIMENT
# ============================================================

from sentiment_scorer import (
    SentimentScorer
)


# ============================================================
# DAY 27 — BEHAVIORAL INDICATORS
# ============================================================

from behavioral_indicators import (
    BehavioralIndicators
)


# ============================================================
# DAY 28 — SCREENING REPORT
# ============================================================

from screening_report_builder import (
    ScreeningReportBuilder
)


# ============================================================
# DAY 29 — AI CALL FLOW
# ============================================================

from ai_call_flow import (
    AICallFlow
)


# ============================================================
# DAY 31 — ROBUST AI FLOW
# ============================================================

from robust_ai_flow import (
    RobustAIFlow
)


# ============================================================
# COMPLETE PIPELINE
# ============================================================

class FinalScreeningPipeline:

    """
    Complete ZecPath AI Screening System.

    Integrates the working modules from Day 25 to Day 31.

    The pipeline processes candidate answers and produces:

        - Edge-case result
        - Answer understanding
        - Intent
        - Semantic information
        - Screening score
        - Confidence analysis
        - Sentiment analysis
        - Behavioral indicators
        - Conversation decision
    """

    def __init__(self):

        # ----------------------------------------------------
        # Day 25
        # ----------------------------------------------------

        self.semantic_builder = (
            SemanticAnswerBuilder()
        )

        # ----------------------------------------------------
        # Day 26
        # ----------------------------------------------------

        self.scoring_engine = (
            ScreeningScoringEngine()
        )

        # ----------------------------------------------------
        # Day 27
        # ----------------------------------------------------

        self.confidence_analyzer = (
            ConfidenceAnalyzer()
        )

        self.sentiment_scorer = (
            SentimentScorer()
        )

        self.behavioral_indicators = (
            BehavioralIndicators()
        )

        # ----------------------------------------------------
        # Day 28
        # ----------------------------------------------------

        self.report_builder = (
            ScreeningReportBuilder()
        )

        # ----------------------------------------------------
        # Day 29
        # ----------------------------------------------------

        self.call_flow = (
            AICallFlow()
        )

        # ----------------------------------------------------
        # Day 31
        # ----------------------------------------------------

        self.robust_flow = (
            RobustAIFlow()
        )

    # ========================================================
    # TIMESTAMP
    # ========================================================

    @staticmethod
    def timestamp():

        return datetime.now(
            timezone.utc
        ).isoformat()

    # ========================================================
    # PROCESS ONE RESPONSE
    # ========================================================

    def process_response(
        self,
        candidate_id,
        job_id,
        question_id,
        question,
        question_category,
        raw_answer,
        duration_seconds=0,
        audio_quality=1.0,
        background_noise=0.0,
        previous_answers=None,
        retry_count=0,
        follow_up_count=0
    ):

        if previous_answers is None:
            previous_answers = []

        # ====================================================
        # STEP 1
        # DAY 31 — ROBUST AI FLOW
        # ====================================================

        robust_result = (
            self.robust_flow.process_input(

                transcript=raw_answer,

                audio_quality=audio_quality,

                background_noise=background_noise,

                retry_count=retry_count,

                follow_up_count=follow_up_count
            )
        )

        robust_action = (
            robust_result.get(
                "action",
                "continue"
            )
        )

        # ----------------------------------------------------
        # Edge case detected
        # ----------------------------------------------------

        if robust_action != "continue":

            return {

                "system":
                    "ZecPath AI Screening System",

                "pipeline_version":
                    "Day 32",

                "pipeline_status":
                    "edge_case_handled",

                "candidate": {

                    "candidate_id":
                        candidate_id,

                    "job_id":
                        job_id
                },

                "question": {

                    "question_id":
                        question_id,

                    "question":
                        question,

                    "category":
                        question_category
                },

                "input": {

                    "raw_answer":
                        raw_answer
                },

                "robust_ai_flow":
                    robust_result,

                "conversation_action":
                    robust_action,

                "created_at":
                    self.timestamp()
            }

        # ====================================================
        # STEP 2
        # DAY 25 — ANSWER UNDERSTANDING
        # ====================================================

        normalized_answer = (
            self.normalize_answer(
                raw_answer
            )
        )

        semantic_result = (
            self.semantic_builder.build(

                candidate_id=
                    candidate_id,

                job_id=
                    job_id,

                question_id=
                    question_id,

                question=
                    question,

                question_category=
                    question_category,

                raw_answer=
                    raw_answer,

                normalized_answer=
                    normalized_answer
            )
        )

        # ----------------------------------------------------
        # Extract Day 25 information
        # ----------------------------------------------------

        intent = semantic_result.get(
            "intent",
            "unknown"
        )

        answer_status = semantic_result.get(
            "answer_status",
            "valid"
        )

        off_topic = semantic_result.get(
            "off_topic",
            False
        )

        semantic_object = semantic_result.get(
            "semantic_object",
            {}
        )

        # ====================================================
        # STEP 3
        # DAY 29 — CONVERSATION FLOW
        # ====================================================

        conversation_result = (
            self.call_flow.analyze_response(

                candidate_id=
                    candidate_id,

                job_id=
                    job_id,

                question_id=
                    question_id,

                question=
                    question,

                question_category=
                    question_category,

                answer_status=
                    answer_status,

                intent=
                    intent,

                current_answer=
                    normalized_answer,

                previous_answers=
                    previous_answers
            )
        )

        conversation_action = (
            conversation_result
            .get("decision", {})
            .get("action")
        )

        # ====================================================
        # STEP 4
        # DAY 26 — SCREENING SCORING
        # ====================================================

        scoring_result = (
            self.scoring_engine.score_response(

                candidate_id=
                    candidate_id,

                job_id=
                    job_id,

                question_id=
                    question_id,

                question=
                    question,

                question_category=
                    question_category,

                normalized_answer=
                    normalized_answer,

                intent=
                    intent,

                answer_status=
                    answer_status,

                off_topic=
                    off_topic,

                semantic_object=
                    semantic_object
            )
        )

        # ====================================================
        # STEP 5
        # DAY 27 — CONFIDENCE ANALYSIS
        # ====================================================

        confidence_result = (
            self.confidence_analyzer
            .analyze_response(

                candidate_id=
                    candidate_id,

                question_id=
                    question_id,

                answer=
                    raw_answer,

                duration_seconds=
                    duration_seconds
            )
        )

        # ====================================================
        # STEP 6
        # DAY 27 — SENTIMENT ANALYSIS
        # ====================================================

        sentiment_result = (
            self.sentiment_scorer
            .analyze_response(

                candidate_id=
                    candidate_id,

                question_id=
                    question_id,

                answer=
                    raw_answer
            )
        )

        # ====================================================
        # STEP 7
        # DAY 27 — BEHAVIORAL INDICATORS
        # ====================================================

        # Day 27 behavioral module expects a contradiction
        # analysis object. Day 31/29 do not automatically
        # provide one, so this integration supplies a safe
        # baseline for the current response.

        contradiction_result = {

            "contradiction_analysis": {

                "detected":
                    False,

                "count":
                    0,

                "types":
                    [],

                "details":
                    []
            }
        }

        behavioral_result = (
            self.behavioral_indicators
            .build_indicators(

                candidate_id=
                    candidate_id,

                question_id=
                    question_id,

                confidence_analysis=
                    confidence_result,

                sentiment_analysis=
                    sentiment_result,

                contradiction_analysis=
                    contradiction_result,

                answer_status=
                    answer_status
            )
        )

        # ====================================================
        # STEP 8
        # FINAL INTEGRATED RESULT
        # ====================================================

        final_result = {

            "system":
                "ZecPath AI Screening System",

            "pipeline_version":
                "Day 32",

            "pipeline_status":
                "success",

            "candidate": {

                "candidate_id":
                    candidate_id,

                "job_id":
                    job_id
            },

            "question": {

                "question_id":
                    question_id,

                "question":
                    question,

                "category":
                    question_category
            },

            "input": {

                "raw_answer":
                    raw_answer,

                "normalized_answer":
                    normalized_answer,

                "duration_seconds":
                    duration_seconds,

                "audio_quality":
                    audio_quality,

                "background_noise":
                    background_noise
            },

            # ------------------------------------------------
            # Day 31
            # ------------------------------------------------

            "edge_case_handling": {

                "status":
                    "normal",

                "action":
                    robust_action,

                "result":
                    robust_result
            },

            # ------------------------------------------------
            # Day 25
            # ------------------------------------------------

            "answer_understanding": {

                "intent":
                    intent,

                "answer_status":
                    answer_status,

                "off_topic":
                    off_topic,

                "confidence":
                    semantic_result.get(
                        "confidence"
                    ),

                "semantic_object":
                    semantic_object
            },

            # ------------------------------------------------
            # Day 26
            # ------------------------------------------------

            "screening_scoring":
                scoring_result,

            # ------------------------------------------------
            # Day 27
            # ------------------------------------------------

            "confidence_analysis":
                confidence_result,

            "sentiment_analysis":
                sentiment_result,

            "behavioral_indicators":
                behavioral_result,

            # ------------------------------------------------
            # Day 29
            # ------------------------------------------------

            "conversation_flow": {

                "response_type":
                    conversation_result.get(
                        "response_type"
                    ),

                "action":
                    conversation_action,

                "reason":
                    conversation_result
                    .get("decision", {})
                    .get("reason"),

                "next_prompt":
                    conversation_result.get(
                        "next_prompt"
                    )
            },

            "created_at":
                self.timestamp()
        }

        return final_result

    # ========================================================
    # NORMALIZE ANSWER
    # ========================================================

    @staticmethod
    def normalize_answer(answer):

        if answer is None:
            return ""

        return " ".join(
            str(answer).strip().split()
        )

    # ========================================================
    # PROCESS COMPLETE SCREENING SESSION
    # ========================================================

    def process_screening_session(
        self,
        candidate_id,
        job_id,
        questions
    ):

        """
        Process multiple screening questions.

        `questions` must be a list of dictionaries.

        Each dictionary can contain:

            question_id
            question
            question_category
            answer
            duration_seconds
            audio_quality
            background_noise
        """

        response_results = []

        previous_answers = []

        for question_data in questions:

            answer = question_data.get(
                "answer",
                ""
            )

            result = self.process_response(

                candidate_id=
                    candidate_id,

                job_id=
                    job_id,

                question_id=
                    question_data.get(
                        "question_id"
                    ),

                question=
                    question_data.get(
                        "question"
                    ),

                question_category=
                    question_data.get(
                        "question_category"
                    ),

                raw_answer=
                    answer,

                duration_seconds=
                    question_data.get(
                        "duration_seconds",
                        0
                    ),

                audio_quality=
                    question_data.get(
                        "audio_quality",
                        1.0
                    ),

                background_noise=
                    question_data.get(
                        "background_noise",
                        0.0
                    ),

                previous_answers=
                    previous_answers
            )

            response_results.append(
                result
            )

            previous_answers.append(
                answer
            )

        # ====================================================
        # CALCULATE SESSION SUMMARY
        # ====================================================

        successful_results = [

            result

            for result in response_results

            if result.get(
                "pipeline_status"
            ) == "success"
        ]

        question_scores = []

        for result in successful_results:

            scoring = result.get(
                "screening_scoring",
                {}
            )

            score = scoring.get(
                "normalized_score"
            )

            if isinstance(
                score,
                (int, float)
            ):

                question_scores.append(
                    score
                )

        if question_scores:

            final_score = round(
                sum(question_scores)
                / len(question_scores),
                2
            )

        else:

            final_score = 0.0

        # ----------------------------------------------------
        # Average communication indicators
        # ----------------------------------------------------

        communication_scores = {

            "confidence": [],

            "clarity": [],

            "engagement": [],

            "consistency": [],

            "communication_strength": []
        }

        for result in successful_results:

            behavioral = result.get(
                "behavioral_indicators",
                {}
            )

            indicators = behavioral.get(
                "communication_indicators",
                {}
            )

            for name in communication_scores:

                value = (
                    indicators
                    .get(name, {})
                    .get("score")
                )

                if isinstance(
                    value,
                    (int, float)
                ):

                    communication_scores[
                        name
                    ].append(value)

        average_communication = {}

        for name, values in (
            communication_scores.items()
        ):

            if values:

                average_communication[name] = round(
                    sum(values) / len(values),
                    2
                )

            else:

                average_communication[name] = 0.0

        # ----------------------------------------------------
        # Session summary
        # ----------------------------------------------------

        total_questions = len(
            response_results
        )

        successful_questions = len(
            successful_results
        )

        edge_cases = (
            total_questions
            - successful_questions
        )

        session_result = {

            "system":
                "ZecPath AI Screening System",

            "pipeline_version":
                "Day 32",

            "session_status":
                "completed",

            "candidate_id":
                candidate_id,

            "job_id":
                job_id,

            "screening_summary": {

                "total_questions":
                    total_questions,

                "successfully_processed":
                    successful_questions,

                "edge_cases_handled":
                    edge_cases,

                "final_screening_score":
                    final_score,

                "score_scale":
                    "0-100",

                "average_communication":
                    average_communication
            },

            "responses":
                response_results,

            "created_at":
                self.timestamp()
        }

        return session_result

    # ========================================================
    # SAVE FINAL RESULT
    # ========================================================

    def save_result(
        self,
        result,
        filename="final_screening_pipeline_result.json"
    ):

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(
            results_dir,
            exist_ok=True
        )

        output_path = os.path.join(
            results_dir,
            filename
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        return output_path


# ============================================================
# DAY 32 DEMO
# ============================================================

if __name__ == "__main__":

    pipeline = FinalScreeningPipeline()

    # --------------------------------------------------------
    # Simulated candidate screening session
    # --------------------------------------------------------

    questions = [

        {

            "question_id":
                "BACKEND_EXP_001",

            "question":
                "How many years of backend development "
                "experience do you have?",

            "question_category":
                "experience",

            "answer":
                "I have three years of backend development "
                "experience. I have worked with Python "
                "and Django.",

            "duration_seconds":
                8,

            "audio_quality":
                1.0,

            "background_noise":
                0.0
        },

        {

            "question_id":
                "BACKEND_SKILLS_001",

            "question":
                "What technical skills do you have?",

            "question_category":
                "skills",

            "answer":
                "I have worked with Python, Django, "
                "Docker and PostgreSQL.",

            "duration_seconds":
                9,

            "audio_quality":
                1.0,

            "background_noise":
                0.0
        },

        {

            "question_id":
                "BACKEND_AVAILABILITY_001",

            "question":
                "When would you be available to join?",

            "question_category":
                "availability",

            "answer":
                "I can join immediately.",

            "duration_seconds":
                5,

            "audio_quality":
                1.0,

            "background_noise":
                0.0
        },

        {

            "question_id":
                "BACKEND_SALARY_001",

            "question":
                "What is your expected salary?",

            "question_category":
                "salary",

            "answer":
                "I expect 6 lakhs per year.",

            "duration_seconds":
                5,

            "audio_quality":
                1.0,

            "background_noise":
                0.0
        }
    ]

    # --------------------------------------------------------
    # Run complete screening
    # --------------------------------------------------------

    final_result = (
        pipeline.process_screening_session(

            candidate_id=
                "candidate_006",

            job_id=
                "JOB_BACKEND_001",

            questions=
                questions
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = pipeline.save_result(
        final_result
    )

    # --------------------------------------------------------
    # Display summary
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("DAY 32 — COMPLETE AI SCREENING SYSTEM")
    print("=" * 75)

    print(
        f"Candidate             : "
        f"{final_result['candidate_id']}"
    )

    print(
        f"Job                   : "
        f"{final_result['job_id']}"
    )

    summary = (
        final_result[
            "screening_summary"
        ]
    )

    print(
        f"Total Questions       : "
        f"{summary['total_questions']}"
    )

    print(
        f"Successfully Processed: "
        f"{summary['successfully_processed']}"
    )

    print(
        f"Edge Cases Handled    : "
        f"{summary['edge_cases_handled']}"
    )

    print(
        f"Final Screening Score : "
        f"{summary['final_screening_score']}/100"
    )

    print()
    print("Average Communication")
    print("-" * 75)

    communication = (
        summary[
            "average_communication"
        ]
    )

    print(
        f"Confidence            : "
        f"{communication['confidence']}"
    )

    print(
        f"Clarity               : "
        f"{communication['clarity']}"
    )

    print(
        f"Engagement            : "
        f"{communication['engagement']}"
    )

    print(
        f"Consistency           : "
        f"{communication['consistency']}"
    )

    print(
        f"Communication Strength: "
        f"{communication['communication_strength']}"
    )

    print()
    print("Question Results")
    print("-" * 75)

    for response in final_result[
        "responses"
    ]:

        question_id = (
            response[
                "question"
            ][
                "question_id"
            ]
        )

        status = (
            response[
                "pipeline_status"
            ]
        )

        if status == "success":

            scoring = response[
                "screening_scoring"
            ]

            score = scoring.get(
                "normalized_score",
                0
            )

            action = (
                response[
                    "conversation_flow"
                ][
                    "action"
                ]
            )

            print(
                f"{question_id}: "
                f"score={score}, "
                f"action={action}"
            )

        else:

            action = response.get(
                "conversation_action"
            )

            print(
                f"{question_id}: "
                f"edge_case_action={action}"
            )

    print()
    print("=" * 75)
    print(
        f"Final result saved to: "
        f"{output_path}"
    )
    print("=" * 75)