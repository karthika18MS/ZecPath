class UnifiedCandidateScore:

    """
    Day 41 - Deliverable 3

    Creates a single unified score object for a candidate.

    The object combines:
        - ATS score
        - Screening score
        - HR interview score
        - Hiring Fit percentage
        - Role
        - Job ID
        - Weight information
        - Weighted contributions
    """

    def __init__(self):
        pass

    def validate_required_data(
        self,
        candidate_id,
        job_id,
        target_role,
        ats_score,
        screening_score,
        hr_score,
        hiring_fit_percentage
    ):

        required_values = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "target_role": target_role,
            "ats_score": ats_score,
            "screening_score": screening_score,
            "hr_score": hr_score,
            "hiring_fit_percentage": hiring_fit_percentage
        }

        for field, value in required_values.items():

            if value is None:
                raise ValueError(
                    f"Required field missing: {field}"
                )

        scores = {
            "ats_score": ats_score,
            "screening_score": screening_score,
            "hr_score": hr_score,
            "hiring_fit_percentage": hiring_fit_percentage
        }

        for field, value in scores.items():

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"{field} must be numeric."
                )

            if value < 0 or value > 100:
                raise ValueError(
                    f"{field} must be between 0 and 100."
                )

    def create_unified_object(
        self,
        candidate_id,
        job_id,
        target_role,
        ats_score,
        screening_score,
        hr_score,
        hiring_fit_percentage,
        weights,
        weighted_contributions
    ):

        self.validate_required_data(
            candidate_id,
            job_id,
            target_role,
            ats_score,
            screening_score,
            hr_score,
            hiring_fit_percentage
        )

        return {

            "candidate_id": candidate_id,

            "job_id": job_id,

            "target_role": target_role,

            "round_scores": {

                "ats": round(ats_score, 2),

                "screening": round(
                    screening_score, 2
                ),

                "hr": round(hr_score, 2)
            },

            "weights": {

                "ats": weights["ats"],

                "screening": weights["screening"],

                "hr": weights["hr"]
            },

            "weighted_contributions": {

                "ats": round(
                    weighted_contributions["ats"],
                    2
                ),

                "screening": round(
                    weighted_contributions["screening"],
                    2
                ),

                "hr": round(
                    weighted_contributions["hr"],
                    2
                )
            },

            "hiring_fit_percentage": round(
                hiring_fit_percentage,
                2
            ),

            "score_status": "Complete"
        }