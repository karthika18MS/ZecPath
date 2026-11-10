import re


class AnswerExtractor:
    """
    Extracts structured information from candidate answers.

    Extracts:
        - Skills
        - Experience
        - Availability
        - Salary expectation
    """

    # -------------------------------------------------
    # Known technical skills
    # -------------------------------------------------

    KNOWN_SKILLS = [
        "Python",
        "Django",
        "FastAPI",
        "Docker",
        "AWS",
        "Git",
        "MongoDB",
        "PostgreSQL",
        "SQL",
        "REST API",
        "Machine Learning",
        "Data Science",
        "Java",
        "JavaScript",
        "React",
        "Node.js",
        "Excel",
        "Power BI",
        "Tableau"
    ]

    # -------------------------------------------------
    # Experience domains
    # -------------------------------------------------

    EXPERIENCE_DOMAINS = [
        "backend development",
        "backend",
        "frontend development",
        "frontend",
        "full stack development",
        "full stack",
        "software development",
        "data science",
        "data analysis",
        "machine learning",
        "web development",
        "python development",
        "human resources",
        "recruitment",
        "marketing"
    ]

    # -------------------------------------------------
    # Number words
    # -------------------------------------------------

    NUMBER_WORDS = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    # =================================================
    # Text normalization
    # =================================================

    def normalize_text(self, text):
        """
        Normalize whitespace in the answer.
        """

        if text is None:
            return ""

        text = str(text).strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    # =================================================
    # Skill extraction
    # =================================================

    def extract_skills(self, text):
        """
        Extract known technical skills from the answer.

        Example:
            "I know Python, Django and Docker."

        Returns:
            ["Python", "Django", "Docker"]
        """

        normalized = self.normalize_text(text)

        found_skills = []

        for skill in self.KNOWN_SKILLS:

            pattern = (
                r"\b"
                + re.escape(skill)
                + r"\b"
            )

            if re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE
            ):

                found_skills.append(skill)

        return found_skills

    # =================================================
    # Number word conversion
    # =================================================

    def extract_number_word(
        self,
        text,
        unit_pattern
    ):
        """
        Extract a number written as a word.

        Example:
            "three years"
            "six months"

        Returns:
            Integer or None
        """

        pattern = (
            r"\b("
            + "|".join(
                self.NUMBER_WORDS.keys()
            )
            + r")\s*"
            + unit_pattern
            + r"\b"
        )

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            return None

        number_word = (
            match.group(1).lower()
        )

        return self.NUMBER_WORDS[
            number_word
        ]

    # =================================================
    # Experience extraction
    # =================================================

    def extract_experience(self, text):
        """
        Extract experience years, months and domain.

        Supports:

            "3 years"
            "three years"
            "6 months"
            "six months"
            "3 years of backend development"
        """

        normalized = self.normalize_text(text)

        result = {
            "years": None,
            "months": None,
            "domain": None
        }

        # ---------------------------------------------
        # Numeric years
        # ---------------------------------------------

        year_match = re.search(
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:years?|yrs?)\b",
            normalized,
            flags=re.IGNORECASE
        )

        if year_match:

            years_value = float(
                year_match.group(1)
            )

            if years_value.is_integer():

                result["years"] = int(
                    years_value
                )

            else:

                result["years"] = years_value

        # ---------------------------------------------
        # Word-based years
        # ---------------------------------------------

        else:

            word_years = self.extract_number_word(
                normalized,
                r"(?:years?|yrs?)"
            )

            if word_years is not None:

                result["years"] = word_years

        # ---------------------------------------------
        # Numeric months
        # ---------------------------------------------

        month_match = re.search(
            r"(\d+)\s*"
            r"(?:months?|mos?)\b",
            normalized,
            flags=re.IGNORECASE
        )

        if month_match:

            result["months"] = int(
                month_match.group(1)
            )

        # ---------------------------------------------
        # Word-based months
        # ---------------------------------------------

        else:

            word_months = self.extract_number_word(
                normalized,
                r"(?:months?|mos?)"
            )

            if word_months is not None:

                result["months"] = word_months

        # ---------------------------------------------
        # Experience domain
        # ---------------------------------------------

        for domain in self.EXPERIENCE_DOMAINS:

            pattern = (
                r"\b"
                + re.escape(domain)
                + r"\b"
            )

            if re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE
            ):

                result["domain"] = domain

                break

        # ---------------------------------------------
        # Nothing extracted
        # ---------------------------------------------

        if (
            result["years"] is None
            and result["months"] is None
            and result["domain"] is None
        ):

            return None

        return result

    # =================================================
    # Availability extraction
    # =================================================

    def extract_availability(self, text):
        """
        Extract candidate availability.

        Examples:

            "I can join immediately."
            "I can join in 30 days."
            "I can join after two weeks."
            "I am available."
        """

        normalized = self.normalize_text(
            text
        ).lower()

        if not normalized:
            return None

        # ---------------------------------------------
        # Immediate availability
        # ---------------------------------------------

        immediate_patterns = [
            "immediately",
            "immediate",
            "right away",
            "can join now",
            "available now"
        ]

        for pattern in immediate_patterns:

            if pattern in normalized:

                return {
                    "status": "immediate",
                    "days": 0
                }

        # ---------------------------------------------
        # Numeric days
        # ---------------------------------------------

        day_match = re.search(
            r"(\d+)\s*"
            r"(?:days?|day)\b",
            normalized
        )

        if day_match:

            days = int(
                day_match.group(1)
            )

            return {
                "status": "notice_period",
                "days": days
            }

        # ---------------------------------------------
        # Numeric weeks
        # ---------------------------------------------

        week_match = re.search(
            r"(\d+)\s*"
            r"(?:weeks?|week)\b",
            normalized
        )

        if week_match:

            weeks = int(
                week_match.group(1)
            )

            return {
                "status": "notice_period",
                "days": weeks * 7
            }

        # ---------------------------------------------
        # Word-based weeks
        # Example: "two weeks"
        # ---------------------------------------------

        word_weeks = self.extract_number_word(
            normalized,
            r"(?:weeks?|week)"
        )

        if word_weeks is not None:

            return {
                "status": "notice_period",
                "days": word_weeks * 7
            }

        # ---------------------------------------------
        # Word-based days
        # Example: "thirty days"
        #
        # Currently supports number words up to ten.
        # ---------------------------------------------

        word_days = self.extract_number_word(
            normalized,
            r"(?:days?|day)"
        )

        if word_days is not None:

            return {
                "status": "notice_period",
                "days": word_days
            }

        # ---------------------------------------------
        # Generic availability
        # ---------------------------------------------

        availability_patterns = [
            "available",
            "can join",
            "able to join"
        ]

        for pattern in availability_patterns:

            if pattern in normalized:

                return {
                    "status": "available",
                    "days": None
                }

        return None

    # =================================================
    # Salary extraction
    # =================================================

    def extract_salary(self, text):
        """
        Extract salary expectation.

        Supports:

            "6 LPA"
            "6 lakhs"
            "6 lakhs per year"
            "₹600000"
            "Rs 600000"
            "INR 600000"
            "600000 salary"
            "600000 package"
            "600000 CTC"
        """

        normalized = self.normalize_text(
            text
        ).lower()

        if not normalized:
            return None

        # ---------------------------------------------
        # LPA / Lakhs
        # ---------------------------------------------

        lpa_match = re.search(
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:lpa|lakhs?|lakh)\b",
            normalized
        )

        if lpa_match:

            value = float(
                lpa_match.group(1)
            )

            amount = int(
                value * 100000
            )

            period = self.detect_salary_period(
                normalized
            )

            return {
                "amount": amount,
                "currency": "INR",
                "unit": "annual",
                "period": period,
                "source": "lpa"
            }

        # ---------------------------------------------
        # INR / Rs / ₹
        # ---------------------------------------------

        inr_match = re.search(
            r"(?:₹|rs\.?|inr)\s*"
            r"([\d,]+)",
            normalized
        )

        if inr_match:

            amount = int(
                inr_match.group(1)
                .replace(",", "")
            )

            period = self.detect_salary_period(
                normalized
            )

            unit = (
                "annual"
                if period == "annual"
                else "monthly"
            )

            return {
                "amount": amount,
                "currency": "INR",
                "unit": unit,
                "period": period,
                "source": "inr"
            }

        # ---------------------------------------------
        # Numeric salary/package/CTC
        # ---------------------------------------------

        numeric_match = re.search(
            r"(\d[\d,]*)\s*"
            r"(?:salary|package|ctc)\b",
            normalized
        )

        if numeric_match:

            amount = int(
                numeric_match.group(1)
                .replace(",", "")
            )

            period = self.detect_salary_period(
                normalized
            )

            unit = (
                "annual"
                if period == "annual"
                else "monthly"
            )

            return {
                "amount": amount,
                "currency": "INR",
                "unit": unit,
                "period": period,
                "source": "numeric"
            }

        return None

    # =================================================
    # Salary period detection
    # =================================================

    def detect_salary_period(self, text):
        """
        Detect whether salary is annual or monthly.
        """

        normalized = self.normalize_text(
            text
        ).lower()

        annual_patterns = [
            "per year",
            "per annum",
            "annual",
            "annually",
            "yearly",
            "lpa",
            "lakhs",
            "lakh"
        ]

        for pattern in annual_patterns:

            if pattern in normalized:
                return "annual"

        monthly_patterns = [
            "per month",
            "monthly",
            "month"
        ]

        for pattern in monthly_patterns:

            if pattern in normalized:
                return "monthly"

        # Default
        return "annual"

    # =================================================
    # Extract everything
    # =================================================

    def extract_all(self, text):
        """
        Extract all supported information
        from a candidate answer.
        """

        return {
            "skills": self.extract_skills(text),

            "experience": self.extract_experience(
                text
            ),

            "availability": self.extract_availability(
                text
            ),

            "salary_expectation": self.extract_salary(
                text
            )
        }


# =====================================================
# Standalone test
# =====================================================

if __name__ == "__main__":

    extractor = AnswerExtractor()

    answer = (
        "I have three years of backend development "
        "experience with Python, Django and Docker. "
        "I can join immediately and I expect "
        "6 lakhs per year."
    )

    result = extractor.extract_all(
        answer
    )

    print("=" * 70)
    print("ZecPath - Day 25")
    print("ANSWER EXTRACTOR")
    print("=" * 70)

    print("\nInput:")
    print(answer)

    print("\nExtracted Information:")

    print(
        result
    )

    print("=" * 70)