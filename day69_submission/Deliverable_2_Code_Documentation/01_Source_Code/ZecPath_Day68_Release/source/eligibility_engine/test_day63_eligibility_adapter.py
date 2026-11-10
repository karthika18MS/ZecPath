
"""Tests for adapting Day63 scoring records to Day21 eligibility inputs."""

import unittest

from eligibility_engine.run_day63_eligibility import (
    evaluate_one,
    prepare_day63_candidate,
)


class Day63EligibilityAdapterTests(unittest.TestCase):

    def setUp(self):
        self.day63 = {
            "candidate_id": "CAND008",
            "job_id": "JD002",
            "target_role": "Python Developer",
            "ats_scoring_status": "COMPLETED",
            "scores": {
                "final_ats_score": 79.53
            },
            "skill_details": {
                "required_skills": ["Python", "Django", "SQL"],
                "matched_skills": ["Python", "SQL"],
                "missing_skills": ["Django"],
            },
            "experience_details": {
                "candidate_experience_years": 1
            },
        }

    def test_uses_jd_skills_and_day63_matches(self):

        adapted, rules = prepare_day63_candidate(
            self.day63,
            {
                "mandatory_skills": ["python", "git"],
                "ats": {
                    "eligible_min": 75
                },
            },
        )

        self.assertEqual(
            rules["mandatory_skills"],
            ["Python", "Django", "SQL"],
        )

        self.assertEqual(
            adapted["skill_details"]["matched_skills"],
            ["Python", "SQL"],
        )

        self.assertEqual(
            adapted["scores"]["final_ats_score"],
            79.53,
        )

        self.assertEqual(
            adapted["entity_detection"]["experience_years"],
            1,
        )

    def test_keeps_unscored_candidate_blocked(self):

        result = evaluate_one(
            {
                "candidate_id": "CAND007",
                "job_id": "JD001",
                "ats_scoring_status": "BLOCKED",
            },
            {},
        )

        self.assertEqual(
            result["eligibility_status"],
            "BLOCKED",
        )

        self.assertIsNone(
            result["ats_score"],
        )


if __name__ == "__main__":
    unittest.main()
