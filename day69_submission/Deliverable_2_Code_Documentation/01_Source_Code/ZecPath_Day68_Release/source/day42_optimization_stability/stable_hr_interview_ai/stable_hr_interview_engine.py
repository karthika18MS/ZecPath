class StableHRInterviewEngine:

    def __init__(
        self,
        max_followups_per_question=2,
        max_total_questions=10,
        prevent_duplicate_questions=True
    ):
        """
        Initialize Stable HR Interview Engine.
        """

        self.max_followups_per_question = (
            max_followups_per_question
        )

        self.max_total_questions = (
            max_total_questions
        )

        self.prevent_duplicate_questions = (
            prevent_duplicate_questions
        )

    # =========================================================
    # FOLLOW-UP LIMIT
    # =========================================================

    def get_followup_limit(self):

        value = (
            self.max_followups_per_question
        )

        if isinstance(
            value,
            (int, float)
        ):

            return value

        if isinstance(
            value,
            dict
        ):

            possible_keys = [
                "max_followups_per_question",
                "max_followups",
                "followup_limit",
                "limit"
            ]

            for key in possible_keys:

                if key in value:

                    configured_value = (
                        value[key]
                    )

                    if isinstance(
                        configured_value,
                        (int, float)
                    ):

                        return configured_value

        return 2

    # =========================================================
    # VALIDATE INTERVIEW FLOW
    # =========================================================

    def validate_interview_flow(
        self,
        question_results
    ):
        """
        Validate stability of the HR interview.

        Checks:
            1. Question structure
            2. Question count
            3. Question IDs
            4. Duplicate question IDs
            5. Question text
            6. Candidate answer
            7. Response status
            8. Follow-up count
        """

        errors = []
        warnings = []

        # -----------------------------------------------------
        # Validate list
        # -----------------------------------------------------

        if not isinstance(
            question_results,
            list
        ):

            return {
                "stable": False,
                "total_questions": 0,
                "duplicate_questions": [],
                "errors": [
                    "Question results must be a list."
                ],
                "warnings": [],
                "question_validation": {
                    "question_text_available": 0,
                    "candidate_answer_available": 0,
                    "response_status_available": 0,
                    "complete_questions": 0
                }
            }

        total_questions = len(
            question_results
        )

        # -----------------------------------------------------
        # Question count
        # -----------------------------------------------------

        if total_questions == 0:

            errors.append(
                "No interview questions found."
            )

        if (
            total_questions
            > self.max_total_questions
        ):

            errors.append(
                f"Interview contains "
                f"{total_questions} questions. "
                f"Maximum allowed is "
                f"{self.max_total_questions}."
            )

        # -----------------------------------------------------
        # Tracking
        # -----------------------------------------------------

        question_ids = []

        question_text_available = 0

        candidate_answer_available = 0

        response_status_available = 0

        complete_questions = 0

        # -----------------------------------------------------
        # Validate each question
        # -----------------------------------------------------

        for index, question in enumerate(
            question_results,
            start=1
        ):

            if not isinstance(
                question,
                dict
            ):

                errors.append(
                    f"Question {index} is not "
                    f"a valid object."
                )

                continue

            # -------------------------------------------------
            # Question ID
            # -------------------------------------------------

            question_id = question.get(
                "question_id"
            )

            if not question_id:

                errors.append(
                    f"Question {index}: "
                    f"Missing question ID."
                )

            else:

                question_ids.append(
                    question_id
                )

            # -------------------------------------------------
            # Question text
            # -------------------------------------------------

            question_text = (
                question.get(
                    "question_text"
                )
                or question.get(
                    "question"
                )
            )

            if not question_text:

                errors.append(
                    f"{question_id or index}: "
                    f"Question text is missing."
                )

            else:

                question_text_available += 1

            # -------------------------------------------------
            # Candidate answer
            # -------------------------------------------------

            candidate_answer = question.get(
                "candidate_answer"
            )

            if not candidate_answer:

                errors.append(
                    f"{question_id or index}: "
                    f"Candidate answer is missing."
                )

            else:

                candidate_answer_available += 1

            # -------------------------------------------------
            # Response status
            # -------------------------------------------------

            response_status = question.get(
                "response_status"
            )

            if not response_status:

                errors.append(
                    f"{question_id or index}: "
                    f"Response status is missing."
                )

            else:

                response_status_available += 1

            # -------------------------------------------------
            # Complete question
            # -------------------------------------------------

            if (
                question_text
                and candidate_answer
                and response_status
            ):

                complete_questions += 1

        # -----------------------------------------------------
        # Duplicate question IDs
        # -----------------------------------------------------

        duplicate_questions = []

        if self.prevent_duplicate_questions:

            seen = set()

            for question_id in question_ids:

                if question_id in seen:

                    duplicate_questions.append(
                        question_id
                    )

                else:

                    seen.add(
                        question_id
                    )

            if duplicate_questions:

                errors.append(
                    "Duplicate question IDs found: "
                    + ", ".join(
                        duplicate_questions
                    )
                )

        # -----------------------------------------------------
        # Follow-up validation
        # -----------------------------------------------------

        followup_limit = (
            self.get_followup_limit()
        )

        for index, question in enumerate(
            question_results,
            start=1
        ):

            if not isinstance(
                question,
                dict
            ):

                continue

            followup_count = question.get(
                "followup_count",
                0
            )

            if followup_count is None:

                warnings.append(
                    f"Question {index}: "
                    f"Follow-up count is unavailable."
                )

                continue

            if not isinstance(
                followup_count,
                (int, float)
            ):

                warnings.append(
                    f"Question {index}: "
                    f"Invalid follow-up count."
                )

                continue

            if followup_count > followup_limit:

                errors.append(
                    f"Question {index}: "
                    f"Follow-up limit exceeded "
                    f"({followup_count} > "
                    f"{followup_limit})."
                )

        # -----------------------------------------------------
        # Final status
        # -----------------------------------------------------

        stable = (
            len(errors) == 0
        )

        return {
            "stable": stable,

            "total_questions":
                total_questions,

            "duplicate_questions":
                duplicate_questions,

            "errors":
                errors,

            "warnings":
                warnings,

            "question_validation": {
                "question_text_available":
                    question_text_available,

                "candidate_answer_available":
                    candidate_answer_available,

                "response_status_available":
                    response_status_available,

                "complete_questions":
                    complete_questions
            }
        }

    # =========================================================
    # COMPATIBILITY METHOD
    # =========================================================

    def validate_interview(
        self,
        question_results
    ):
        """
        Compatibility wrapper used by
        the Day 42 runner.
        """

        return self.validate_interview_flow(
            question_results
        )