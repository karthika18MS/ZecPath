
"""
ZecPath Day 65 - Production Score Validator

Validates assessment scores, scoring weights,
score coverage, and candidate/job records.

This module validates data only.
It does not calculate or modify scores.
"""

import math
from collections import Counter


class ScoreValidator:
    """Production-oriented validation for ZecPath assessment scores."""

    MIN_SCORE = 0.0
    MAX_SCORE = 100.0

    REQUIRED_ROUNDS = {
        "ats",
        "hr",
        "aptitude",
        "technical",
        "machine_test",
    }

    @staticmethod
    def validate_score(score, field_name="score"):
        """Validate one numeric score."""

        if score is None:
            return {
                "valid": True,
                "status": "MISSING",
                "errors": [],
            }

        if isinstance(score, bool):
            return {
                "valid": False,
                "status": "INVALID",
                "errors": [
                    f"{field_name} must not be a boolean."
                ],
            }

        if not isinstance(score, (int, float)):
            return {
                "valid": False,
                "status": "INVALID",
                "errors": [
                    f"{field_name} must be numeric."
                ],
            }

        if not math.isfinite(score):
            return {
                "valid": False,
                "status": "INVALID",
                "errors": [
                    f"{field_name} must be a finite number."
                ],
            }

        if not ScoreValidator.MIN_SCORE <= score <= ScoreValidator.MAX_SCORE:
            return {
                "valid": False,
                "status": "INVALID",
                "errors": [
                    f"{field_name} must be between 0 and 100."
                ],
            }

        return {
            "valid": True,
            "status": "VALID",
            "errors": [],
        }

    @staticmethod
    def validate_weights(weights):
        """Validate the five cross-round scoring weights."""

        errors = []

        if not isinstance(weights, dict):
            return {
                "valid": False,
                "total_weight": None,
                "errors": ["Weights must be a JSON object."],
            }

        if set(weights.keys()) != ScoreValidator.REQUIRED_ROUNDS:
            errors.append(
                "Weights must contain exactly: "
                + ", ".join(sorted(ScoreValidator.REQUIRED_ROUNDS))
            )

        for round_name, weight in weights.items():

            if isinstance(weight, bool) or not isinstance(
                weight, (int, float)
            ):
                errors.append(
                    f"Weight for {round_name} must be numeric."
                )
                continue

            if not math.isfinite(weight) or not 0 <= weight <= 1:
                errors.append(
                    f"Weight for {round_name} must be between 0 and 1."
                )

        if not errors:
            total = sum(weights.values())

            if not math.isclose(total, 1.0, abs_tol=0.000001):
                errors.append(
                    f"Weights must total 1.0. Current total: {total}"
                )
        else:
            total = None

        return {
            "valid": len(errors) == 0,
            "total_weight": total,
            "errors": errors,
        }

    @staticmethod
    def validate_score_coverage(coverage):
        """Validate score coverage percentage."""

        return ScoreValidator.validate_score(
            coverage,
            field_name="score_coverage",
        )

    @staticmethod
    def validate_candidate(candidate, weights):
        """Validate one candidate/job cross-round record."""

        errors = []

        if not isinstance(candidate, dict):
            return {
                "valid": False,
                "errors": ["Candidate result must be an object."],
            }

        candidate_id = candidate.get("candidate_id")
        job_id = candidate.get("job_id")

        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append("Missing or invalid candidate_id.")

        if not isinstance(job_id, str) or not job_id.strip():
            errors.append("Missing or invalid job_id.")

        round_details = candidate.get("round_details")

        if not isinstance(round_details, dict):
            errors.append("round_details must be an object.")
            round_details = {}

        available_weight = 0.0
        missing_rounds = []

        for round_name, expected_weight in weights.items():

            round_data = round_details.get(round_name)

            if not isinstance(round_data, dict):
                errors.append(
                    f"Missing or invalid round details: {round_name}"
                )
                missing_rounds.append(round_name)
                continue

            score = round_data.get("score")

            result = ScoreValidator.validate_score(
                score,
                field_name=f"{round_name}.score",
            )

            errors.extend(result["errors"])

            if score is None:
                missing_rounds.append(round_name)
            elif result["valid"]:
                available_weight += expected_weight

            actual_weight = round_data.get("weight")

            if actual_weight is not None:
                if (
                    isinstance(actual_weight, bool)
                    or not isinstance(actual_weight, (int, float))
                    or not math.isfinite(actual_weight)
                    or not math.isclose(
                        actual_weight,
                        expected_weight,
                        abs_tol=0.000001,
                    )
                ):
                    errors.append(
                        f"Weight mismatch for {round_name}."
                    )

        coverage = candidate.get("score_coverage")

        coverage_result = ScoreValidator.validate_score_coverage(
            coverage
        )

        errors.extend(coverage_result["errors"])

        expected_coverage = round(available_weight * 100, 2)

        if coverage is not None and coverage_result["valid"]:
            if not math.isclose(
                coverage,
                expected_coverage,
                abs_tol=0.02,
            ):
                errors.append(
                    "Score coverage does not match available round weights."
                )

        unified_score = candidate.get("unified_score")

        unified_result = ScoreValidator.validate_score(
            unified_score,
            field_name="unified_score",
        )

        errors.extend(unified_result["errors"])

        if unified_score is None and available_weight > 0:
            errors.append(
                "Unified score is missing despite available assessment scores."
            )

        if unified_score is not None and available_weight == 0:
            errors.append(
                "Unified score exists but no valid round scores are available."
            )

        return {
            "valid": len(errors) == 0,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "missing_rounds": missing_rounds,
            "expected_score_coverage": expected_coverage,
            "errors": errors,
        }

    @staticmethod
    def validate_candidate_records(candidates, weights):
        """Validate candidate records and detect duplicate combinations."""

        errors = []
        results = []

        if not isinstance(candidates, list):
            return {
                "valid": False,
                "total_candidates": 0,
                "valid_candidates": 0,
                "invalid_candidates": 0,
                "errors": ["candidate_results must be a list."],
                "results": [],
            }

        seen = set()

        for index, candidate in enumerate(candidates, start=1):

            result = ScoreValidator.validate_candidate(
                candidate,
                weights,
            )

            results.append(result)

            if not result["valid"]:
                errors.append({
                    "record": index,
                    "candidate_id": result.get("candidate_id"),
                    "errors": result["errors"],
                })

            candidate_id = result.get("candidate_id")
            job_id = result.get("job_id")

            if (
                isinstance(candidate_id, str)
                and candidate_id.strip()
                and isinstance(job_id, str)
                and job_id.strip()
            ):
                key = (candidate_id.strip(), job_id.strip())

                if key in seen:
                    errors.append({
                        "record": index,
                        "candidate_id": candidate_id,
                        "errors": [
                            "Duplicate candidate/job combination."
                        ],
                    })

                seen.add(key)

        invalid_count = len([
            result for result in results if not result["valid"]
        ])

        return {
            "valid": len(errors) == 0,
            "total_candidates": len(candidates),
            "valid_candidates": len(candidates) - invalid_count,
            "invalid_candidates": invalid_count,
            "errors": errors,
            "results": results,
        }
