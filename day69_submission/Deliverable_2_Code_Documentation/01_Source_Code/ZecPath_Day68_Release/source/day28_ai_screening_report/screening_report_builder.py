import json
import os
from datetime import datetime, timezone


class ScreeningReportBuilder:
    """
    Builds a structured AI screening report by combining
    candidate answer information, screening scores, and
    communication indicators.

    Data sources:
        Day 25 -> Answer Understanding
        Day 26 -> Screening Scoring
        Day 27 -> Behavioral Indicators
    """

    # --------------------------------------------------
    # Extract key answers
    # --------------------------------------------------

    def extract_key_answers(self, answer_data):
        """
        Extract important candidate answers from
        Day 25 answer-understanding data.
        """

        key_answers = {}

        question_category = answer_data.get(
            "question_category",
            ""
        )

        semantic_object = answer_data.get(
            "semantic_object",
            {}
        )

        normalized_answer = answer_data.get(
            "normalized_answer",
            ""
        )

        if question_category == "experience":

            experience = semantic_object.get(
                "experience",
                {}
            )

            key_answers["experience"] = {
                "years": experience.get(
                    "years"
                ),
                "months": experience.get(
                    "months"
                ),
                "domain": experience.get(
                    "domain"
                )
            }

        elif question_category == "skills":

            key_answers["skills"] = (
                semantic_object.get(
                    "skills",
                    []
                )
            )

        elif question_category == "salary":

            key_answers["salary_expectation"] = (
                semantic_object.get(
                    "salary",
                    {}
                )
            )

        elif question_category in [
            "availability",
            "notice_period"
        ]:

            key_answers["availability"] = (
                semantic_object.get(
                    "availability",
                    semantic_object.get(
                        "notice_period",
                        None
                    )
                )
            )

        elif question_category == "location":

            key_answers["location"] = (
                semantic_object.get(
                    "location"
                )
            )

        elif question_category == "education":

            key_answers["education"] = (
                semantic_object.get(
                    "education"
                )
            )

        # Always preserve the candidate's actual answer
        key_answers["response"] = normalized_answer

        return key_answers

    # --------------------------------------------------
    # Extract screening score
    # --------------------------------------------------

    def extract_screening_score(
        self,
        scoring_data
    ):
        """
        Extract Day 26 screening score information.
        """

        return {
            "final_screening_score": scoring_data.get(
                "final_screening_score",
                0
            ),

            "score_scale": scoring_data.get(
                "score_scale",
                "0-100"
            ),

            "average_scores": scoring_data.get(
                "average_scores",
                {}
            ),

            "screening_summary": scoring_data.get(
                "screening_summary",
                {}
            )
        }

    # --------------------------------------------------
    # Extract question scores
    # --------------------------------------------------

    def extract_question_scores(
        self,
        scoring_data
    ):
        """
        Extract per-question screening scores.
        """

        question_scores = scoring_data.get(
            "question_scores",
            []
        )

        result = []

        for question in question_scores:

            result.append({

                "question_id": question.get(
                    "question_id"
                ),

                "question": question.get(
                    "question"
                ),

                "question_category": question.get(
                    "question_category"
                ),

                "normalized_score": question.get(
                    "normalized_score",
                    question.get(
                        "score",
                        0
                    )
                ),

                "answer_status": question.get(
                    "answer_status"
                ),

                "intent": question.get(
                    "intent"
                ),

                "off_topic": question.get(
                    "off_topic",
                    False
                ),

                "strengths": question.get(
                    "explanation",
                    {}
                ).get(
                    "strengths",
                    []
                ),

                "weaknesses": question.get(
                    "explanation",
                    {}
                ).get(
                    "weaknesses",
                    []
                )
            })

        return result

    # --------------------------------------------------
    # Extract strengths
    # --------------------------------------------------

    def extract_strengths(
        self,
        scoring_data,
        behavioral_data
    ):
        """
        Collect strengths from screening scores
        and communication indicators.
        """

        strengths = []

        # Screening strengths
        explanation = scoring_data.get(
            "explanation",
            {}
        )

        for item in explanation.get(
            "strengths",
            []
        ):

            if isinstance(item, dict):

                reason = item.get(
                    "reason"
                )

                if reason:
                    strengths.append(reason)

            elif isinstance(item, str):

                strengths.append(item)

        # Communication strengths
        communication = behavioral_data.get(
            "communication_indicators",
            {}
        )

        for indicator_name in [
            "confidence",
            "clarity",
            "engagement",
            "consistency"
        ]:

            indicator = communication.get(
                indicator_name,
                {}
            )

            level = indicator.get(
                "level"
            )

            if level == "strong":

                strengths.append(
                    f"Strong {indicator_name} "
                    "communication indicator."
                )

        return self.remove_duplicates(
            strengths
        )

    # --------------------------------------------------
    # Extract risks
    # --------------------------------------------------

    def extract_risks(
        self,
        scoring_data,
        behavioral_data
    ):
        """
        Identify screening and communication risk signals.
        """

        risks = []

        # Screening weaknesses
        explanation = scoring_data.get(
            "explanation",
            {}
        )

        for item in explanation.get(
            "weaknesses",
            []
        ):

            if isinstance(item, dict):

                reason = item.get(
                    "reason"
                )

                if reason:
                    risks.append(reason)

            elif isinstance(item, str):

                risks.append(item)

        # Communication indicators
        communication = behavioral_data.get(
            "communication_indicators",
            {}
        )

        for indicator_name in [
            "confidence",
            "clarity",
            "engagement",
            "consistency"
        ]:

            indicator = communication.get(
                indicator_name,
                {}
            )

            level = indicator.get(
                "level"
            )

            if level == "needs_improvement":

                risks.append(
                    f"{indicator_name.title()} "
                    "communication indicator needs "
                    "improvement."
                )

        # Behavioral signals
        signals = behavioral_data.get(
            "behavioral_signals",
            {}
        )

        if signals.get(
            "contradiction_detected",
            False
        ):

            risks.append(
                "A contradiction was detected "
                "in the available responses."
            )

        if signals.get(
            "hesitation_count",
            0
        ) > 0:

            risks.append(
                "Hesitation signals were detected "
                "in the response."
            )

        if signals.get(
            "uncertainty_count",
            0
        ) > 0:

            risks.append(
                "Uncertainty signals were detected "
                "in the response."
            )

        return self.remove_duplicates(
            risks
        )

    # --------------------------------------------------
    # Identify missing data
    # --------------------------------------------------

    def identify_missing_data(
        self,
        answer_data
    ):
        """
        Identify important information that is
        unavailable in the current answer.
        """

        missing_data = []

        question_category = answer_data.get(
            "question_category",
            ""
        )

        semantic_object = answer_data.get(
            "semantic_object",
            {}
        )

        answer_status = answer_data.get(
            "answer_status",
            ""
        )

        if answer_status == "no_response":

            missing_data.append(
                f"No response provided for "
                f"{question_category} question."
            )

            return missing_data

        if answer_status == "vague":

            missing_data.append(
                f"Response to {question_category} "
                "question is vague."
            )

        if question_category == "experience":

            experience = semantic_object.get(
                "experience",
                {}
            )

            if not experience.get("years"):

                missing_data.append(
                    "Experience duration is not "
                    "explicitly provided."
                )

            if not experience.get("domain"):

                missing_data.append(
                    "Experience domain is not "
                    "explicitly provided."
                )

        elif question_category == "skills":

            skills = semantic_object.get(
                "skills",
                []
            )

            if not skills:

                missing_data.append(
                    "No skills were confirmed "
                    "in the response."
                )

        elif question_category == "salary":

            salary = semantic_object.get(
                "salary",
                {}
            )

            if not salary:

                missing_data.append(
                    "Salary expectation is not "
                    "available in the response."
                )

        elif question_category in [
            "availability",
            "notice_period"
        ]:

            availability = semantic_object.get(
                "availability"
            )

            notice_period = semantic_object.get(
                "notice_period"
            )

            if not availability and not notice_period:

                missing_data.append(
                    "Availability or notice period "
                    "is not available."
                )

        return missing_data

    # --------------------------------------------------
    # Highlight salary
    # --------------------------------------------------

    def extract_salary_expectation(
        self,
        answer_data
    ):
        """
        Extract salary expectation if available.
        """

        semantic_object = answer_data.get(
            "semantic_object",
            {}
        )

        salary = semantic_object.get(
            "salary"
        )

        if salary:
            return salary

        return None

    # --------------------------------------------------
    # Highlight availability
    # --------------------------------------------------

    def extract_availability(
        self,
        answer_data
    ):
        """
        Extract availability information if available.
        """

        semantic_object = answer_data.get(
            "semantic_object",
            {}
        )

        availability = semantic_object.get(
            "availability"
        )

        if availability:
            return availability

        notice_period = semantic_object.get(
            "notice_period"
        )

        if notice_period:
            return notice_period

        return None

    # --------------------------------------------------
    # Highlight skills
    # --------------------------------------------------

    def extract_skill_confirmations(
        self,
        answer_data
    ):
        """
        Extract skills confirmed by the candidate.
        """

        semantic_object = answer_data.get(
            "semantic_object",
            {}
        )

        skills = semantic_object.get(
            "skills",
            []
        )

        if not isinstance(skills, list):
            return []

        return skills

    # --------------------------------------------------
    # Duplicate removal
    # --------------------------------------------------

    def remove_duplicates(
        self,
        items
    ):
        """
        Remove duplicate strings while preserving order.
        """

        result = []

        for item in items:

            if item not in result:
                result.append(item)

        return result

    # --------------------------------------------------
    # Build complete screening report
    # --------------------------------------------------

    def build_report(
        self,
        candidate_id,
        job_id,
        answer_data,
        scoring_data,
        behavioral_data
    ):
        """
        Build the complete AI screening report.
        """

        question_id = answer_data.get(
            "question_id"
        )

        question = answer_data.get(
            "question"
        )

        question_category = answer_data.get(
            "question_category"
        )

        key_answers = self.extract_key_answers(
            answer_data
        )

        screening_score = (
            self.extract_screening_score(
                scoring_data
            )
        )

        question_scores = (
            self.extract_question_scores(
                scoring_data
            )
        )

        strengths = self.extract_strengths(
            scoring_data,
            behavioral_data
        )

        risks = self.extract_risks(
            scoring_data,
            behavioral_data
        )

        missing_data = self.identify_missing_data(
            answer_data
        )

        salary_expectation = (
            self.extract_salary_expectation(
                answer_data
            )
        )

        availability = (
            self.extract_availability(
                answer_data
            )
        )

        skill_confirmations = (
            self.extract_skill_confirmations(
                answer_data
            )
        )

        communication = behavioral_data.get(
            "communication_indicators",
            {}
        )

        behavioral_signals = behavioral_data.get(
            "behavioral_signals",
            {}
        )

        report = {

            "report_type": (
                "AI Screening Report"
            ),

            "candidate_id": candidate_id,

            "job_id": job_id,

            "question_context": {

                "question_id": question_id,

                "question": question,

                "question_category":
                    question_category
            },

            "key_answers": key_answers,

            "screening_evaluation": {

                "final_screening_score":
                    screening_score[
                        "final_screening_score"
                    ],

                "score_scale":
                    screening_score[
                        "score_scale"
                    ],

                "average_scores":
                    screening_score[
                        "average_scores"
                    ],

                "screening_summary":
                    screening_score[
                        "screening_summary"
                    ]
            },

            "question_scores": question_scores,

            "strengths": strengths,

            "risks": risks,

            "missing_data": missing_data,

            "highlights": {

                "salary_expectation":
                    salary_expectation,

                "availability":
                    availability,

                "skill_confirmations":
                    skill_confirmations
            },

            "communication_summary": {

                "confidence":
                    communication.get(
                        "confidence",
                        {}
                    ),

                "clarity":
                    communication.get(
                        "clarity",
                        {}
                    ),

                "engagement":
                    communication.get(
                        "engagement",
                        {}
                    ),

                "consistency":
                    communication.get(
                        "consistency",
                        {}
                    ),

                "communication_strength":
                    communication.get(
                        "communication_strength",
                        {}
                    )
            },

            "behavioral_signals":
                behavioral_signals,

            "answer_status":
                answer_data.get(
                    "answer_status"
                ),

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return report

    # --------------------------------------------------
    # Save report
    # --------------------------------------------------

    def save_report(
        self,
        report,
        filename
    ):
        """
        Save the screening report as JSON.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(
            results_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            results_dir,
            filename
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        return file_path


# ======================================================
# Main
# ======================================================

if __name__ == "__main__":

    builder = ScreeningReportBuilder()

    # --------------------------------------------------
    # Example Day 25 data
    # --------------------------------------------------

    answer_data = {

        "candidate_id": "candidate_006",

        "job_id": "JOB_BACKEND_001",

        "question_id": "BACKEND_EXP_001",

        "question": (
            "How many years of backend development "
            "experience do you have?"
        ),

        "question_category": "experience",

        "raw_answer": (
            "Um, I have like three years of backend "
            "development experience. I have worked "
            "with Python and Django."
        ),

        "normalized_answer": (
            "I have three years of backend development "
            "experience. I have worked with Python "
            "and Django."
        ),

        "intent": "experience",

        "answer_status": "valid",

        "off_topic": False,

        "semantic_object": {

            "skills": [
                "Python",
                "Django"
            ],

            "experience": {

                "years": 3,

                "months": None,

                "domain": "backend development"
            }
        }
    }

    # --------------------------------------------------
    # Example Day 26 data
    # --------------------------------------------------

    scoring_data = {

        "candidate_id": "candidate_006",

        "job_id": "JOB_BACKEND_001",

        "screening_summary": {

            "total_questions": 4,

            "answered_questions": 4,

            "no_response_questions": 0,

            "off_topic_questions": 0
        },

        "average_scores": {

            "clarity": 8.75,

            "relevance": 9.75,

            "completeness": 9.5,

            "consistency": 9.0
        },

        "final_screening_score": 92.5,

        "score_scale": "0-100",

        "explanation": {

            "strengths": [],

            "weaknesses": []
        },

        "question_scores": [

            {

                "question_id":
                    "BACKEND_EXP_001",

                "question":
                    "How many years of backend "
                    "development experience do "
                    "you have?",

                "question_category":
                    "experience",

                "normalized_score": 95.0,

                "answer_status": "valid",

                "intent": "experience",

                "off_topic": False,

                "explanation": {

                    "strengths": [
                        "Clear response.",
                        "Relevant experience provided."
                    ],

                    "weaknesses": []
                }
            }
        ]
    }

    # --------------------------------------------------
    # Example Day 27 data
    # --------------------------------------------------

    behavioral_data = {

        "candidate_id":
            "candidate_006",

        "question_id":
            "BACKEND_SKILLS_001",

        "communication_indicators": {

            "confidence": {

                "score": 100,

                "level": "strong"
            },

            "clarity": {

                "score": 100,

                "level": "strong"
            },

            "engagement": {

                "score": 90,

                "level": "strong"
            },

            "consistency": {

                "score": 100,

                "level": "strong"
            },

            "communication_strength": {

                "score": 97.5,

                "level": "strong"
            }
        },

        "behavioral_signals": {

            "hesitation_count": 0,

            "uncertainty_count": 0,

            "response_word_count": 14,

            "pace": "normal",

            "sentiment": "positive",

            "sentiment_score": 100.0,

            "contradiction_detected": False
        }
    }

    # --------------------------------------------------
    # Build report
    # --------------------------------------------------

    report = builder.build_report(

        candidate_id="candidate_006",

        job_id="JOB_BACKEND_001",

        answer_data=answer_data,

        scoring_data=scoring_data,

        behavioral_data=behavioral_data
    )

    print("=" * 70)
    print("ZecPath - Day 28")
    print("AI SCREENING REPORT BUILDER")
    print("=" * 70)

    print(
        json.dumps(
            report,
            indent=4
        )
    )

    # --------------------------------------------------
    # Save report
    # --------------------------------------------------

    filename = (
        "candidate_006_screening_report.json"
    )

    saved_path = builder.save_report(
        report,
        filename
    )

    print("\nScreening report saved to:")
    print(saved_path)

    print("=" * 70)