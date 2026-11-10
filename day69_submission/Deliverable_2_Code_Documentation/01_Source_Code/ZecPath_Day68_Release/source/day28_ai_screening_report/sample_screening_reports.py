import json
from pathlib import Path

from recruiter_report_formatter import RecruiterReportFormatter


BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"


class SampleScreeningReports:

    def __init__(self):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def create_strong_candidate(self):
        """
        Sample 1:
        Strong candidate with good screening and communication scores.
        """

        return {
            "report_type": "AI Screening Report",
            "candidate_id": "sample_candidate_001",
            "job_id": "JOB_BACKEND_001",

            "question_context": {
                "question_id": "BACKEND_EXP_001",
                "question": "How many years of backend development experience do you have?",
                "question_category": "experience"
            },

            "key_answers": {
                "experience": {
                    "years": 4,
                    "months": None,
                    "domain": "backend development"
                },
                "response": (
                    "I have four years of backend development experience. "
                    "I have worked extensively with Python, Django, FastAPI, "
                    "PostgreSQL and Docker."
                )
            },

            "screening_evaluation": {
                "final_screening_score": 94.5,
                "score_scale": "0-100",

                "average_scores": {
                    "clarity": 9.5,
                    "relevance": 9.75,
                    "completeness": 9.5,
                    "consistency": 9.5
                },

                "screening_summary": {
                    "total_questions": 5,
                    "answered_questions": 5,
                    "no_response_questions": 0,
                    "off_topic_questions": 0
                }
            },

            "question_scores": [
                {
                    "question_id": "BACKEND_EXP_001",
                    "question": (
                        "How many years of backend development experience "
                        "do you have?"
                    ),
                    "question_category": "experience",
                    "normalized_score": 95.0,
                    "answer_status": "valid",
                    "intent": "experience",
                    "off_topic": False,
                    "strengths": [
                        "Clear response.",
                        "Relevant experience provided.",
                        "Specific technologies mentioned."
                    ],
                    "weaknesses": []
                }
            ],

            "strengths": [
                "Strong backend development experience.",
                "Multiple relevant technical skills confirmed.",
                "Strong confidence communication indicator.",
                "Strong clarity communication indicator.",
                "Strong consistency communication indicator."
            ],

            "risks": [],

            "missing_data": [],

            "highlights": {
                "salary_expectation": {
                    "amount": 70000,
                    "currency": "INR",
                    "period": "month"
                },
                "availability": "Available immediately",
                "skill_confirmations": [
                    "Python",
                    "Django",
                    "FastAPI",
                    "PostgreSQL",
                    "Docker"
                ]
            },

            "communication_summary": {
                "confidence": {
                    "score": 95,
                    "level": "strong"
                },
                "clarity": {
                    "score": 95,
                    "level": "strong"
                },
                "engagement": {
                    "score": 95,
                    "level": "strong"
                },
                "consistency": {
                    "score": 100,
                    "level": "strong"
                },
                "communication_strength": {
                    "score": 96.25,
                    "level": "strong"
                }
            },

            "behavioral_signals": {
                "hesitation_count": 0,
                "uncertainty_count": 0,
                "response_word_count": 25,
                "pace": "normal",
                "sentiment": "positive",
                "sentiment_score": 100.0,
                "contradiction_detected": False
            },

            "answer_status": "valid",
            "created_at": "2026-09-09T06:00:00+00:00"
        }

    def create_incomplete_candidate(self):
        """
        Sample 2:
        Candidate with incomplete screening information.
        """

        return {
            "report_type": "AI Screening Report",
            "candidate_id": "sample_candidate_002",
            "job_id": "JOB_BACKEND_001",

            "question_context": {
                "question_id": "BACKEND_EXP_002",
                "question": "Tell me about your backend development experience.",
                "question_category": "experience"
            },

            "key_answers": {
                "experience": {
                    "years": 1,
                    "months": None,
                    "domain": None
                },
                "response": "I have around one year of experience."
            },

            "screening_evaluation": {
                "final_screening_score": 61.5,
                "score_scale": "0-100",

                "average_scores": {
                    "clarity": 7.0,
                    "relevance": 7.5,
                    "completeness": 5.0,
                    "consistency": 8.0
                },

                "screening_summary": {
                    "total_questions": 5,
                    "answered_questions": 4,
                    "no_response_questions": 1,
                    "off_topic_questions": 0
                }
            },

            "question_scores": [
                {
                    "question_id": "BACKEND_EXP_002",
                    "question": "Tell me about your backend development experience.",
                    "question_category": "experience",
                    "normalized_score": 65.0,
                    "answer_status": "valid",
                    "intent": "experience",
                    "off_topic": False,
                    "strengths": [
                        "Experience duration provided."
                    ],
                    "weaknesses": [
                        "Technical domain not specified.",
                        "Limited supporting details."
                    ]
                }
            ],

            "strengths": [
                "Candidate provided a basic experience duration.",
                "Response remained relevant to the question."
            ],

            "risks": [
                "Limited experience details.",
                "Technical skills were not confirmed.",
                "One screening question received no response."
            ],

            "missing_data": [
                "Backend development domain",
                "Technical skills",
                "Availability",
                "Salary expectation"
            ],

            "highlights": {
                "salary_expectation": None,
                "availability": None,
                "skill_confirmations": []
            },

            "communication_summary": {
                "confidence": {
                    "score": 70,
                    "level": "moderate"
                },
                "clarity": {
                    "score": 70,
                    "level": "moderate"
                },
                "engagement": {
                    "score": 65,
                    "level": "moderate"
                },
                "consistency": {
                    "score": 90,
                    "level": "strong"
                },
                "communication_strength": {
                    "score": 73.75,
                    "level": "moderate"
                }
            },

            "behavioral_signals": {
                "hesitation_count": 2,
                "uncertainty_count": 1,
                "response_word_count": 7,
                "pace": "normal",
                "sentiment": "neutral",
                "sentiment_score": 50.0,
                "contradiction_detected": False
            },

            "answer_status": "valid",
            "created_at": "2026-09-09T06:05:00+00:00"
        }

    def create_off_topic_candidate(self):
        """
        Sample 3:
        Candidate gives an off-topic response.
        """

        return {
            "report_type": "AI Screening Report",
            "candidate_id": "sample_candidate_003",
            "job_id": "JOB_BACKEND_001",

            "question_context": {
                "question_id": "BACKEND_EXP_003",
                "question": "How many years of backend development experience do you have?",
                "question_category": "experience"
            },

            "key_answers": {
                "response": (
                    "I really enjoy working with technology and I am "
                    "looking for a good opportunity."
                )
            },

            "screening_evaluation": {
                "final_screening_score": 48.0,
                "score_scale": "0-100",

                "average_scores": {
                    "clarity": 7.0,
                    "relevance": 3.0,
                    "completeness": 2.5,
                    "consistency": 7.0
                },

                "screening_summary": {
                    "total_questions": 5,
                    "answered_questions": 5,
                    "no_response_questions": 0,
                    "off_topic_questions": 2
                }
            },

            "question_scores": [
                {
                    "question_id": "BACKEND_EXP_003",
                    "question": (
                        "How many years of backend development "
                        "experience do you have?"
                    ),
                    "question_category": "experience",
                    "normalized_score": 35.0,
                    "answer_status": "off_topic",
                    "intent": "off_topic",
                    "off_topic": True,
                    "strengths": [
                        "Response was understandable."
                    ],
                    "weaknesses": [
                        "Response did not answer the experience question.",
                        "Experience duration was not provided."
                    ]
                }
            ],

            "strengths": [
                "Response was understandable.",
                "Positive communication tone detected."
            ],

            "risks": [
                "Response was off-topic.",
                "Required experience information was not provided.",
                "Two off-topic responses detected during screening."
            ],

            "missing_data": [
                "Years of backend experience",
                "Backend development domain",
                "Technical skills"
            ],

            "highlights": {
                "salary_expectation": None,
                "availability": None,
                "skill_confirmations": []
            },

            "communication_summary": {
                "confidence": {
                    "score": 60,
                    "level": "moderate"
                },
                "clarity": {
                    "score": 80,
                    "level": "strong"
                },
                "engagement": {
                    "score": 50,
                    "level": "needs_improvement"
                },
                "consistency": {
                    "score": 100,
                    "level": "strong"
                },
                "communication_strength": {
                    "score": 72.5,
                    "level": "moderate"
                }
            },

            "behavioral_signals": {
                "hesitation_count": 0,
                "uncertainty_count": 0,
                "response_word_count": 15,
                "pace": "normal",
                "sentiment": "positive",
                "sentiment_score": 100.0,
                "contradiction_detected": False
            },

            "answer_status": "off_topic",
            "created_at": "2026-09-09T06:10:00+00:00"
        }

    def create_uncertain_candidate(self):
        """
        Sample 4:
        Candidate response contains hesitation and uncertainty.
        """

        return {
            "report_type": "AI Screening Report",
            "candidate_id": "sample_candidate_004",
            "job_id": "JOB_BACKEND_001",

            "question_context": {
                "question_id": "BACKEND_EXP_004",
                "question": "How many years of backend development experience do you have?",
                "question_category": "experience"
            },

            "key_answers": {
                "experience": {
                    "years": 3,
                    "months": None,
                    "domain": "backend development"
                },
                "response": (
                    "Um, I think I have maybe three years of backend "
                    "development experience. I believe I worked mostly "
                    "with Python."
                )
            },

            "screening_evaluation": {
                "final_screening_score": 70.0,
                "score_scale": "0-100",

                "average_scores": {
                    "clarity": 6.5,
                    "relevance": 9.0,
                    "completeness": 8.0,
                    "consistency": 7.0
                },

                "screening_summary": {
                    "total_questions": 5,
                    "answered_questions": 5,
                    "no_response_questions": 0,
                    "off_topic_questions": 0
                }
            },

            "question_scores": [
                {
                    "question_id": "BACKEND_EXP_004",
                    "question": (
                        "How many years of backend development "
                        "experience do you have?"
                    ),
                    "question_category": "experience",
                    "normalized_score": 75.0,
                    "answer_status": "valid",
                    "intent": "experience",
                    "off_topic": False,
                    "strengths": [
                        "Relevant experience was provided.",
                        "Backend development domain was identified."
                    ],
                    "weaknesses": [
                        "Hesitation and uncertainty detected."
                    ]
                }
            ],

            "strengths": [
                "Relevant backend experience was provided.",
                "Experience domain was identified.",
                "Response remained relevant to the question."
            ],

            "risks": [
                "Hesitation detected in response.",
                "Uncertainty signals detected.",
                "Communication confidence may require further evaluation."
            ],

            "missing_data": [],

            "highlights": {
                "salary_expectation": None,
                "availability": None,
                "skill_confirmations": [
                    "Python"
                ]
            },

            "communication_summary": {
                "confidence": {
                    "score": 60,
                    "level": "moderate"
                },
                "clarity": {
                    "score": 70,
                    "level": "moderate"
                },
                "engagement": {
                    "score": 75,
                    "level": "moderate"
                },
                "consistency": {
                    "score": 90,
                    "level": "strong"
                },
                "communication_strength": {
                    "score": 73.75,
                    "level": "moderate"
                }
            },

            "behavioral_signals": {
                "hesitation_count": 3,
                "uncertainty_count": 2,
                "response_word_count": 22,
                "pace": "normal",
                "sentiment": "neutral",
                "sentiment_score": 50.0,
                "contradiction_detected": False
            },

            "answer_status": "valid",
            "created_at": "2026-09-09T06:15:00+00:00"
        }

    def save_json_report(self, report, filename):
        """
        Save the structured sample report as JSON.
        """

        file_path = RESULTS_DIR / filename

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        return file_path

    def create_recruiter_report(self, report, filename):
        """
        Convert structured sample report into recruiter-ready TXT report.
        """

        formatter = RecruiterReportFormatter(report)

        file_path = RESULTS_DIR / filename

        formatter.save_report(file_path)

        return file_path

    def generate_all_reports(self):

        samples = [
            (
                self.create_strong_candidate(),
                "sample_strong_candidate_report"
            ),
            (
                self.create_incomplete_candidate(),
                "sample_incomplete_candidate_report"
            ),
            (
                self.create_off_topic_candidate(),
                "sample_off_topic_candidate_report"
            ),
            (
                self.create_uncertain_candidate(),
                "sample_uncertain_candidate_report"
            )
        ]

        generated_files = []

        for report, name in samples:

            json_file = self.save_json_report(
                report,
                f"{name}.json"
            )

            txt_file = self.create_recruiter_report(
                report,
                f"{name}.txt"
            )

            generated_files.append(
                {
                    "json": json_file,
                    "txt": txt_file
                }
            )

        return generated_files


if __name__ == "__main__":

    generator = SampleScreeningReports()

    files = generator.generate_all_reports()

    print("\nSAMPLE SCREENING REPORT GENERATOR")
    print("=" * 60)

    for file_set in files:
        print("\nGenerated JSON:")
        print(file_set["json"])

        print("Generated Recruiter Report:")
        print(file_set["txt"])

    print("\n" + "=" * 60)
    print("All sample screening reports generated successfully.")