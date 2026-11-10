import re


class IntentClassifier:
    """
    Classifies the intent of a candidate's screening answer.

    Supported intents:
        introduction
        education
        experience
        skills
        location
        salary
        notice_period
        availability
        off_topic
        vague
        no_response
    """

    # =================================================
    # Intent Keywords
    # =================================================

    INTENT_KEYWORDS = {

        "introduction": [
            "my name",
            "i am",
            "i'm",
            "myself",
            "introduce",
            "introduction",
            "about me"
        ],

        "education": [
            "degree",
            "education",
            "qualification",
            "mca",
            "bca",
            "btech",
            "b.tech",
            "mtech",
            "m.tech",
            "bachelor",
            "master",
            "university",
            "college",
            "graduation",
            "graduate"
        ],

        "experience": [
            "experience",
            "years of experience",
            "months of experience",
            "worked",
            "work experience",
            "backend development",
            "software development",
            "developer",
            "previous company",
            "previous role"
        ],

        "skills": [
            "skills",
            "technical skills",
            "technologies",
            "technology",
            "python",
            "django",
            "fastapi",
            "docker",
            "aws",
            "git",
            "mongodb",
            "postgresql",
            "sql",
            "react",
            "javascript",
            "machine learning",
            "data science"
        ],

        "location": [
            "location",
            "located",
            "live",
            "living",
            "reside",
            "city",
            "place",
            "kerala",
            "kochi",
            "trivandrum",
            "thiruvananthapuram",
            "bangalore",
            "bengaluru",
            "chennai",
            "mumbai",
            "delhi"
        ],

        "salary": [
            "salary",
            "expected salary",
            "salary expectation",
            "expecting",
            "package",
            "ctc",
            "lpa",
            "lakhs",
            "lakh",
            "per annum",
            "annual salary",
            "monthly salary"
        ],

        "notice_period": [
            "notice period",
            "notice",
            "serving notice",
            "days to join",
            "joining period"
        ],

        "availability": [
            "available",
            "availability",
            "join",
            "joining",
            "can join",
            "immediately",
            "immediate",
            "start",
            "starting"
        ]
    }

    # =================================================
    # Vague Answer Patterns
    # =================================================

    VAGUE_PATTERNS = [
        "i don't know",
        "i do not know",
        "not sure",
        "i'm not sure",
        "i am not sure",
        "maybe",
        "perhaps",
        "i think",
        "i guess",
        "around that",
        "something like that",
        "probably",
        "whatever",
        "anything is fine",
        "anything is okay",
        "no idea",
        "can't say",
        "cannot say",
        "not certain"
    ]

    # =================================================
    # No Response Patterns
    # =================================================

    NO_RESPONSE_PATTERNS = [
        "",
        "no response",
        "[inaudible]",
        "[unclear]",
        "[silence]",
        "silence"
    ]

    # =================================================
    # Explicit Off-topic Patterns
    # =================================================

    OFF_TOPIC_PATTERNS = [
        "watching movies",
        "watch movies",
        "watching cricket",
        "playing cricket",
        "playing football",
        "playing games",
        "cooking",
        "my favorite food",
        "my favourite food",
        "weather is",
        "i like music",
        "i love music",
        "my hobby is",
        "my hobbies are"
    ]

    # =================================================
    # Normalize Text
    # =================================================

    def normalize_text(self, text):
        """
        Converts text to lowercase and removes
        unnecessary whitespace.
        """

        if text is None:
            return ""

        text = str(text).lower().strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    # =================================================
    # No Response Detection
    # =================================================

    def is_no_response(self, answer):
        """
        Detect whether the candidate gave no response.
        """

        normalized = self.normalize_text(
            answer
        )

        return normalized in self.NO_RESPONSE_PATTERNS

    # =================================================
    # Vague Detection
    # =================================================

    def is_vague(self, answer):
        """
        Detect whether the answer is vague or uncertain.
        """

        normalized = self.normalize_text(
            answer
        )

        for pattern in self.VAGUE_PATTERNS:

            if pattern in normalized:
                return True

        return False

    # =================================================
    # Keyword Matching
    # =================================================

    def contains_keyword(
        self,
        text,
        keywords
    ):
        """
        Check whether text contains any keyword.
        """

        for keyword in keywords:

            if keyword in text:
                return True

        return False

    # =================================================
    # Question Category Classification
    # =================================================

    def classify_by_question_category(
        self,
        answer,
        question_category
    ):
        """
        Classify answer according to the expected
        question category.
        """

        normalized_answer = self.normalize_text(
            answer
        )

        if question_category in self.INTENT_KEYWORDS:

            keywords = self.INTENT_KEYWORDS[
                question_category
            ]

            if self.contains_keyword(
                normalized_answer,
                keywords
            ):

                return question_category

        return None

    # =================================================
    # Intent Classification
    # =================================================

    def classify(
        self,
        question,
        answer,
        question_category=None
    ):
        """
        Classify the intent of a candidate answer.

        Classification order:

            1. No response
            2. Vague response
            3. Explicit off-topic response
            4. Question category
            5. Question keywords
            6. Answer keywords
            7. Off-topic fallback
        """

        normalized_question = self.normalize_text(
            question
        )

        normalized_answer = self.normalize_text(
            answer
        )

        # ---------------------------------------------
        # 1. No response
        # ---------------------------------------------

        if self.is_no_response(
            normalized_answer
        ):

            return {
                "intent": "no_response",
                "confidence": 1.0,
                "reason": (
                    "No meaningful response detected."
                )
            }

        # ---------------------------------------------
        # 2. Vague response
        # ---------------------------------------------

        if self.is_vague(
            normalized_answer
        ):

            return {
                "intent": "vague",
                "confidence": 0.90,
                "reason": (
                    "Candidate response is vague "
                    "or uncertain."
                )
            }

        # ---------------------------------------------
        # 3. Explicit off-topic detection
        # ---------------------------------------------

        for pattern in self.OFF_TOPIC_PATTERNS:

            if pattern in normalized_answer:

                return {
                    "intent": "off_topic",
                    "confidence": 0.95,
                    "reason": (
                        "Candidate answer contains "
                        "content unrelated to the "
                        "screening question."
                    )
                }

        # ---------------------------------------------
        # 4. Match expected question category
        # ---------------------------------------------

        if question_category:

            category_intent = (
                self.classify_by_question_category(
                    normalized_answer,
                    question_category
                )
            )

            if category_intent:

                return {
                    "intent": category_intent,
                    "confidence": 0.95,
                    "reason": (
                        "Answer matches the expected "
                        "question category."
                    )
                }

        # ---------------------------------------------
        # 5. Check question keywords
        # ---------------------------------------------

        for intent, keywords in (
            self.INTENT_KEYWORDS.items()
        ):

            if self.contains_keyword(
                normalized_question,
                keywords
            ):

                return {
                    "intent": intent,
                    "confidence": 0.90,
                    "reason": (
                        "Question indicates this intent."
                    )
                }

        # ---------------------------------------------
        # 6. Check answer keywords
        # ---------------------------------------------

        for intent, keywords in (
            self.INTENT_KEYWORDS.items()
        ):

            if self.contains_keyword(
                normalized_answer,
                keywords
            ):

                return {
                    "intent": intent,
                    "confidence": 0.80,
                    "reason": (
                        "Answer contains keywords "
                        "associated with this intent."
                    )
                }

        # ---------------------------------------------
        # 7. Unknown / unrelated answer
        # ---------------------------------------------

        return {
            "intent": "off_topic",
            "confidence": 0.70,
            "reason": (
                "Answer does not match a known "
                "screening intent."
            )
        }

    # =================================================
    # Off-topic Detection
    # =================================================

    def detect_off_topic(
        self,
        question,
        answer,
        question_category=None
    ):
        """
        Detect whether the candidate's answer
        is unrelated to the question.
        """

        normalized_question = self.normalize_text(
            question
        )

        normalized_answer = self.normalize_text(
            answer
        )

        # ---------------------------------------------
        # No response is not off-topic
        # ---------------------------------------------

        if self.is_no_response(
            normalized_answer
        ):

            return {
                "is_off_topic": False,
                "confidence": 1.0,
                "reason": (
                    "No response is not treated "
                    "as off-topic."
                )
            }

        # ---------------------------------------------
        # Explicit off-topic patterns
        # ---------------------------------------------

        for pattern in self.OFF_TOPIC_PATTERNS:

            if pattern in normalized_answer:

                return {
                    "is_off_topic": True,
                    "confidence": 0.95,
                    "reason": (
                        "Answer contains content "
                        "unrelated to the screening "
                        "question."
                    )
                }

        # ---------------------------------------------
        # Vague is not automatically off-topic
        # ---------------------------------------------

        if self.is_vague(
            normalized_answer
        ):

            return {
                "is_off_topic": False,
                "confidence": 0.90,
                "reason": (
                    "Answer is vague but not "
                    "clearly off-topic."
                )
            }

        # ---------------------------------------------
        # Check expected category relevance
        # ---------------------------------------------

        if question_category in self.INTENT_KEYWORDS:

            category_keywords = (
                self.INTENT_KEYWORDS[
                    question_category
                ]
            )

            if self.contains_keyword(
                normalized_answer,
                category_keywords
            ):

                return {
                    "is_off_topic": False,
                    "confidence": 0.90,
                    "reason": (
                        "Answer contains information "
                        "relevant to the question."
                    )
                }

        # ---------------------------------------------
        # Check question-answer word overlap
        # ---------------------------------------------

        question_words = set(
            normalized_question.split()
        )

        answer_words = set(
            normalized_answer.split()
        )

        common_words = (
            question_words.intersection(
                answer_words
            )
        )

        # ---------------------------------------------
        # Longer answer with no relevance
        # ---------------------------------------------

        if len(normalized_answer.split()) >= 3:

            if not common_words and question_category:

                return {
                    "is_off_topic": True,
                    "confidence": 0.80,
                    "reason": (
                        "Answer does not contain "
                        "information relevant to "
                        "the question."
                    )
                }

        # ---------------------------------------------
        # Default
        # ---------------------------------------------

        return {
            "is_off_topic": False,
            "confidence": 0.70,
            "reason": (
                "Answer appears potentially relevant."
            )
        }

    # =================================================
    # Answer Status Detection
    # =================================================

    def detect_answer_status(
        self,
        answer
    ):
        """
        Detect whether the candidate answer is:

            - no_response
            - vague
            - valid
        """

        normalized_answer = self.normalize_text(
            answer
        )

        # ---------------------------------------------
        # No response
        # ---------------------------------------------

        if self.is_no_response(
            normalized_answer
        ):

            return {
                "status": "no_response",
                "confidence": 1.0,
                "reason": (
                    "No meaningful candidate response "
                    "was detected."
                )
            }

        # ---------------------------------------------
        # Vague response
        # ---------------------------------------------

        if self.is_vague(
            normalized_answer
        ):

            return {
                "status": "vague",
                "confidence": 0.90,
                "reason": (
                    "Candidate response is unclear "
                    "or uncertain."
                )
            }

        # ---------------------------------------------
        # Very short answer
        # ---------------------------------------------

        words = normalized_answer.split()

        if len(words) <= 1:

            return {
                "status": "vague",
                "confidence": 0.80,
                "reason": (
                    "Candidate response is too short "
                    "to provide sufficient information."
                )
            }

        # ---------------------------------------------
        # Valid answer
        # ---------------------------------------------

        return {
            "status": "valid",
            "confidence": 0.90,
            "reason": (
                "Candidate provided a meaningful response."
            )
        }


# =====================================================
# Standalone Test
# =====================================================

if __name__ == "__main__":

    classifier = IntentClassifier()

    result = classifier.classify(
        question=(
            "How many years of backend "
            "development experience do you have?"
        ),
        answer=(
            "I have three years of backend "
            "development experience."
        ),
        question_category="experience"
    )

    print("=" * 70)
    print("ZecPath - Intent Classifier")
    print("=" * 70)

    print(result)

    print("=" * 70)