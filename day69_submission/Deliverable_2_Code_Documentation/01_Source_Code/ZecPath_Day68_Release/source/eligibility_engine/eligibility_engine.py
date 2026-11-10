
import copy


class EligibilityDecisionEngine:
    """
    ZecPath Day 21 / Day 63 Eligibility Decision Engine.

    Supports two interfaces:

    Day 21:
        engine.evaluate(candidate=candidate, ats_result=ats_result)

    Day 63:
        engine.evaluate(day18_result=day18_result, candidate=candidate)

    Decisions:
        Eligible
        Review
        Rejected

    Missing required information:
        NOT_EVALUATED -> Review

    Hard rule failures:
        Rejected
    """

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self, recruiter_rules):

        if not isinstance(recruiter_rules, dict):
            raise TypeError("recruiter_rules must be a dictionary.")

        self.rules = copy.deepcopy(recruiter_rules)
        self._validate_rules()

    # =========================================================
    # RULE VALIDATION
    # =========================================================

    def _validate_rules(self):

        self.rules.setdefault("ats", {})
        ats_rules = self.rules["ats"]

        eligible_min = ats_rules.get("eligible_min", 75)
        review_min = ats_rules.get("review_min", 60)

        try:
            eligible_min = float(eligible_min)
            review_min = float(review_min)
        except (TypeError, ValueError):
            raise ValueError("ATS cutoffs must be numeric.")

        if review_min > eligible_min:
            raise ValueError(
                "review_min cannot be greater than eligible_min."
            )

        if review_min < 0 or eligible_min > 100:
            raise ValueError("ATS cutoffs must be between 0 and 100.")

        if eligible_min < 0:
            raise ValueError("eligible_min cannot be negative.")

        ats_rules["eligible_min"] = eligible_min
        ats_rules["review_min"] = review_min

        # Mandatory skills
        mandatory = self.rules.get("mandatory_skills", [])

        if mandatory is None:
            mandatory = []

        if not isinstance(mandatory, list):
            raise ValueError("mandatory_skills must be a list.")

        self.rules["mandatory_skills"] = [
            str(skill).strip().lower()
            for skill in mandatory
            if str(skill).strip()
        ]

        # Experience
        self.rules.setdefault("experience", {})
        experience = self.rules["experience"]

        for key in ("min_years", "max_years"):
            value = experience.get(key)

            if value is not None:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"experience.{key} must be numeric or null."
                    )

                if value < 0:
                    raise ValueError(
                        f"experience.{key} cannot be negative."
                    )

                experience[key] = value

        minimum = experience.get("min_years")
        maximum = experience.get("max_years")

        if minimum is not None and maximum is not None:
            if minimum > maximum:
                raise ValueError(
                    "experience.min_years cannot exceed max_years."
                )

        # Location
        self.rules.setdefault("location", {})

        allowed = self.rules["location"].get("allowed", [])

        if allowed is None:
            allowed = []

        if not isinstance(allowed, list):
            raise ValueError("location.allowed must be a list.")

        self.rules["location"]["allowed"] = [
            str(location).strip().lower()
            for location in allowed
            if str(location).strip()
        ]

        # Availability
        self.rules.setdefault("availability", {})

        maximum_days = self.rules["availability"].get("max_days")

        if maximum_days is not None:
            try:
                maximum_days = int(maximum_days)
            except (TypeError, ValueError):
                raise ValueError(
                    "availability.max_days must be an integer or null."
                )

            if maximum_days < 0:
                raise ValueError(
                    "availability.max_days cannot be negative."
                )

            self.rules["availability"]["max_days"] = maximum_days

    # =========================================================
    # SAFE CONVERSION
    # =========================================================

    @staticmethod
    def _safe_float(value):

        if value is None or isinstance(value, bool):
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(value):

        if value is None or isinstance(value, bool):
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # =========================================================
    # ATS SCORE CHECK
    # =========================================================

    def check_ats_score(self, ats_score):

        score = self._safe_float(ats_score)

        eligible_cutoff = self.rules["ats"]["eligible_min"]
        review_cutoff = self.rules["ats"]["review_min"]

        if score is None or not 0 <= score <= 100:
            return {
                "passed": False,
                "status": "Rejected",
                "score": None,
                "eligible_cutoff": eligible_cutoff,
                "review_cutoff": review_cutoff,
                "reason": "ATS score is missing or invalid."
            }

        if score >= eligible_cutoff:
            return {
                "passed": True,
                "status": "Eligible",
                "score": score,
                "eligible_cutoff": eligible_cutoff,
                "review_cutoff": review_cutoff,
                "reason": "ATS score meets the eligibility cutoff."
            }

        if score >= review_cutoff:
            return {
                "passed": True,
                "status": "Review",
                "score": score,
                "eligible_cutoff": eligible_cutoff,
                "review_cutoff": review_cutoff,
                "reason": "ATS score is within the recruiter review range."
            }

        return {
            "passed": False,
            "status": "Rejected",
            "score": score,
            "eligible_cutoff": eligible_cutoff,
            "review_cutoff": review_cutoff,
            "reason": "ATS score is below the review cutoff."
        }

    # =========================================================
    # MANDATORY SKILLS CHECK
    # =========================================================

    def check_mandatory_skills(self, day18_result):

        required_skills = self.rules.get("mandatory_skills", [])

        skill_details = day18_result.get("skill_details") or {}
        matched_skills = skill_details.get("matched_skills") or []

        if not isinstance(matched_skills, (list, tuple, set)):
            matched_skills = []

        matched_set = {
            str(skill).strip().lower()
            for skill in matched_skills
            if str(skill).strip()
        }

        missing_skills = [
            skill
            for skill in required_skills
            if skill not in matched_set
        ]

        if not required_skills:
            return {
                "passed": True,
                "required": [],
                "matched": sorted(matched_set),
                "missing": [],
                "status": "No mandatory skills configured."
            }

        if missing_skills:
            return {
                "passed": False,
                "required": required_skills,
                "matched": sorted(matched_set),
                "missing": missing_skills,
                "status": "Mandatory skill requirement not met."
            }

        return {
            "passed": True,
            "required": required_skills,
            "matched": sorted(matched_set),
            "missing": [],
            "status": "All mandatory skills are satisfied."
        }

    # =========================================================
    # EXPERIENCE CHECK
    # =========================================================

    def check_experience(self, day18_result):

        experience_rules = self.rules.get("experience", {})

        minimum_years = self._safe_float(
            experience_rules.get("min_years")
        )

        maximum_years = self._safe_float(
            experience_rules.get("max_years")
        )

        entity_detection = day18_result.get("entity_detection") or {}

        candidate_years = self._safe_float(
            entity_detection.get("experience_years")
        )

        # No experience restriction
        if minimum_years is None and maximum_years is None:
            return {
                "passed": True,
                "evaluation_status": "EVALUATED",
                "candidate_years": candidate_years,
                "minimum_years": None,
                "maximum_years": None,
                "status": "No experience restriction configured."
            }

        # Experience information missing
        if candidate_years is None:
            return {
                "passed": None,
                "evaluation_status": "NOT_EVALUATED",
                "candidate_years": None,
                "minimum_years": minimum_years,
                "maximum_years": maximum_years,
                "status": (
                    "Experience information unavailable; "
                    "manual review required."
                )
            }

        if minimum_years is not None and candidate_years < minimum_years:
            return {
                "passed": False,
                "evaluation_status": "EVALUATED",
                "candidate_years": candidate_years,
                "minimum_years": minimum_years,
                "maximum_years": maximum_years,
                "status": "Candidate has less experience than required."
            }

        if maximum_years is not None and candidate_years > maximum_years:
            return {
                "passed": False,
                "evaluation_status": "EVALUATED",
                "candidate_years": candidate_years,
                "minimum_years": minimum_years,
                "maximum_years": maximum_years,
                "status": "Candidate has more experience than allowed."
            }

        return {
            "passed": True,
            "evaluation_status": "EVALUATED",
            "candidate_years": candidate_years,
            "minimum_years": minimum_years,
            "maximum_years": maximum_years,
            "status": "Experience requirement satisfied."
        }

    # =========================================================
    # LOCATION CHECK
    # =========================================================

    def check_location(self, candidate):

        location_rules = self.rules.get("location", {})
        allowed_locations = location_rules.get("allowed", [])

        candidate_location = None

        if isinstance(candidate, dict):
            candidate_location = candidate.get("location")

        if candidate_location is not None:
            candidate_location = str(
                candidate_location
            ).strip().lower()

        # No location restriction
        if not allowed_locations:
            return {
                "passed": True,
                "evaluation_status": "EVALUATED",
                "candidate_location": candidate_location,
                "allowed_locations": [],
                "status": "No location restriction configured."
            }

        # Location information missing
        if not candidate_location:
            return {
                "passed": None,
                "evaluation_status": "NOT_EVALUATED",
                "candidate_location": None,
                "allowed_locations": allowed_locations,
                "status": (
                    "Candidate location unavailable; "
                    "manual review required."
                )
            }

        if candidate_location not in allowed_locations:
            return {
                "passed": False,
                "evaluation_status": "EVALUATED",
                "candidate_location": candidate_location,
                "allowed_locations": allowed_locations,
                "status": "Candidate location is not allowed."
            }

        return {
            "passed": True,
            "evaluation_status": "EVALUATED",
            "candidate_location": candidate_location,
            "allowed_locations": allowed_locations,
            "status": "Candidate location satisfies the requirement."
        }

    # =========================================================
    # AVAILABILITY CHECK
    # =========================================================

    def check_availability(self, candidate):

        availability_rules = self.rules.get("availability", {})

        maximum_days = self._safe_int(
            availability_rules.get("max_days")
        )

        candidate_notice_days = None

        if isinstance(candidate, dict):
            candidate_notice_days = candidate.get(
                "notice_period_days"
            )

        candidate_notice_days = self._safe_int(
            candidate_notice_days
        )

        # No availability restriction
        if maximum_days is None:
            return {
                "passed": True,
                "evaluation_status": "EVALUATED",
                "candidate_notice_period_days": candidate_notice_days,
                "maximum_allowed_days": None,
                "status": "No availability restriction configured."
            }

        # Notice period missing
        if candidate_notice_days is None:
            return {
                "passed": None,
                "evaluation_status": "NOT_EVALUATED",
                "candidate_notice_period_days": None,
                "maximum_allowed_days": maximum_days,
                "status": (
                    "Candidate availability information unavailable; "
                    "manual review required."
                )
            }

        if candidate_notice_days < 0:
            return {
                "passed": False,
                "evaluation_status": "EVALUATED",
                "candidate_notice_period_days": candidate_notice_days,
                "maximum_allowed_days": maximum_days,
                "status": "Candidate notice period cannot be negative."
            }

        if candidate_notice_days > maximum_days:
            return {
                "passed": False,
                "evaluation_status": "EVALUATED",
                "candidate_notice_period_days": candidate_notice_days,
                "maximum_allowed_days": maximum_days,
                "status": (
                    "Candidate notice period exceeds "
                    "the allowed maximum."
                )
            }

        return {
            "passed": True,
            "evaluation_status": "EVALUATED",
            "candidate_notice_period_days": candidate_notice_days,
            "maximum_allowed_days": maximum_days,
            "status": "Candidate availability satisfies the requirement."
        }

    # =========================================================
    # INPUT ADAPTER: DAY 21
    # =========================================================

    def _adapt_day21_input(self, candidate, ats_result):

        if not isinstance(candidate, dict):
            raise TypeError("candidate must be a dictionary.")

        if not isinstance(ats_result, dict):
            raise TypeError("ats_result must be a dictionary.")

        return {
            "candidate_id": (
                candidate.get("candidate_id")
                or ats_result.get("candidate_id")
            ),

            "target_role": (
                candidate.get("job_role")
                or candidate.get("target_role")
                or self.rules.get("job_role")
            ),

            "job_description": ats_result.get("job_id"),

            "scores": {
                "final_ats_score": ats_result.get("ats_score")
            },

            "skill_details": {
                "matched_skills": candidate.get("skills", [])
            },

            "entity_detection": {
                "experience_years": candidate.get("experience")
            }
        }

    # =========================================================
    # FINAL EVALUATION
    # =========================================================

    def evaluate(
        self,
        day18_result=None,
        candidate=None,
        ats_result=None
    ):
        """
        Evaluate a candidate.

        Day21 usage:
            evaluate(candidate=candidate, ats_result=ats_result)

        Day63 usage:
            evaluate(day18_result=day18_result, candidate=candidate)
        """

        legacy_mode = ats_result is not None

        # -----------------------------------------------------
        # Adapt Day21 input
        # -----------------------------------------------------

        if legacy_mode:
            day18_result = self._adapt_day21_input(
                candidate,
                ats_result
            )

        if not isinstance(day18_result, dict):
            raise TypeError("day18_result must be a dictionary.")

        if candidate is None:
            candidate = {}

        if not isinstance(candidate, dict):
            raise TypeError("candidate must be a dictionary.")

        # -----------------------------------------------------
        # Run all checks
        # -----------------------------------------------------

        scores = day18_result.get("scores") or {}
        ats_score = scores.get("final_ats_score")

        ats_check = self.check_ats_score(ats_score)

        skill_check = self.check_mandatory_skills(day18_result)

        experience_check = self.check_experience(day18_result)

        location_check = self.check_location(candidate)

        availability_check = self.check_availability(candidate)

        # -----------------------------------------------------
        # Collect failed rules
        # -----------------------------------------------------

        failed_rules = []

        if ats_check["passed"] is False:
            failed_rules.append("ats_score")

        if skill_check["passed"] is False:
            failed_rules.append("mandatory_skills")

        if experience_check["passed"] is False:
            failed_rules.append("experience")

        if location_check["passed"] is False:
            failed_rules.append("location")

        if availability_check["passed"] is False:
            failed_rules.append("availability")

        # -----------------------------------------------------
        # Collect not-evaluated rules
        # -----------------------------------------------------

        not_evaluated_rules = []

        if experience_check["passed"] is None:
            not_evaluated_rules.append("experience")

        if location_check["passed"] is None:
            not_evaluated_rules.append("location")

        if availability_check["passed"] is None:
            not_evaluated_rules.append("availability")

        # -----------------------------------------------------
        # Final decision priority
        # -----------------------------------------------------

        # Hard rejection has highest priority
        if failed_rules:
            final_status = "Rejected"

        # Missing required information
        elif not_evaluated_rules:
            final_status = "Review"

        # ATS review range
        elif ats_check["status"] == "Review":
            final_status = "Review"

        # All applicable rules passed
        else:
            final_status = "Eligible"

        # -----------------------------------------------------
        # Reason
        # -----------------------------------------------------

        if final_status == "Eligible":

            reason = (
                "Candidate satisfies all applicable "
                "recruiter-defined eligibility rules "
                "and meets the ATS eligibility cutoff."
            )

        elif final_status == "Review":

            review_reasons = []

            if ats_check["status"] == "Review":
                review_reasons.append(
                    "ATS score is within the recruiter review range."
                )

            if not_evaluated_rules:
                review_reasons.append(
                    "Required information is unavailable for: "
                    + ", ".join(not_evaluated_rules)
                    + "."
                )

            reason = " ".join(review_reasons)

        else:

            reason_parts = []

            if ats_check["status"] == "Rejected":
                reason_parts.append(
                    "ATS score is below the review cutoff."
                )

            if skill_check["passed"] is False:
                reason_parts.append(
                    "Mandatory skill requirements are not met."
                )

            if experience_check["passed"] is False:
                reason_parts.append(
                    "Experience requirement is not met."
                )

            if location_check["passed"] is False:
                reason_parts.append(
                    "Location requirement is not met."
                )

            if availability_check["passed"] is False:
                reason_parts.append(
                    "Availability requirement is not met."
                )

            reason = " ".join(reason_parts)

        # -----------------------------------------------------
        # Detailed checks
        # -----------------------------------------------------

        details = {
            "ats_score": ats_check,
            "mandatory_skills": skill_check,
            "experience": experience_check,
            "location": location_check,
            "availability": availability_check
        }

        # -----------------------------------------------------
        # Day21-compatible output
        # -----------------------------------------------------

        if legacy_mode:

            return {
                "candidate_id": day18_result.get("candidate_id"),
                "job_id": day18_result.get("job_description"),
                "job_role": day18_result.get("target_role"),
                "ats_score": ats_check["score"],
                "eligibility": final_status,
                "reason": reason,
                "failed_rules": failed_rules,
                "not_evaluated_rules": not_evaluated_rules,
                "details": details
            }

        # -----------------------------------------------------
        # Day63 output
        # -----------------------------------------------------

        return {
            "candidate_id": day18_result.get("candidate_id"),

            "target_role": day18_result.get("target_role"),

            "job_description": day18_result.get("job_description"),

            "eligibility": {
                "status": final_status,
                "reason": reason,
                "failed_rules": failed_rules,
                "not_evaluated_rules": not_evaluated_rules
            },

            "ats": {
                "score": ats_check["score"],
                "status": ats_check["status"],
                "eligible_cutoff": ats_check["eligible_cutoff"],
                "review_cutoff": ats_check["review_cutoff"]
            },

            "rule_checks": {
                "mandatory_skills": skill_check,
                "experience": experience_check,
                "location": location_check,
                "availability": availability_check
            }
        }
