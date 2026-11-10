import re


class TranscriptCleaner:
    """
    Cleans and normalizes raw speech-to-text transcripts
    while preserving the candidate's original meaning.
    """

    # -------------------------------------------------
    # Filler Words
    # -------------------------------------------------

    FILLER_WORDS = [
        "um",
        "uh",
        "er",
        "ah",
        "hmm",
        "you know",
        "like"
    ]

    # -------------------------------------------------
    # Technical Terms
    # -------------------------------------------------

    TECHNICAL_TERMS = {
        "python": "Python",
        "django": "Django",
        "fastapi": "FastAPI",
        "fast api": "FastAPI",
        "docker": "Docker",
        "aws": "AWS",
        "git": "Git",
        "mongodb": "MongoDB",
        "postgresql": "PostgreSQL",
        "post crest ql": "PostgreSQL",
        "sql": "SQL",
        "rest api": "REST API",
        "machine learning": "Machine Learning",
        "data science": "Data Science"
    }

    # -------------------------------------------------
    # 1. Silence Detection
    # -------------------------------------------------

    def detect_silence(self, text):
        """
        Detect whether the transcript contains
        a meaningful response.

        Returns:
            True  -> no response
            False -> response detected
        """

        if not text or not text.strip():
            return True

        return False

    # -------------------------------------------------
    # 2. Remove Filler Words
    # -------------------------------------------------

    def remove_filler_words(self, text):
        """
        Remove unnecessary speech filler words such as:
        um, uh, er, ah, hmm, you know and like.
        """

        for filler in self.FILLER_WORDS:

            pattern = r"\b" + re.escape(filler) + r"\b"

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            )

        # Remove repeated commas created after
        # removing filler words.
        text = re.sub(
            r",\s*,+",
            ",",
            text
        )

        # Remove commas before common connecting words.
        text = re.sub(
            r",\s+(of|and|or|but|to|for|with|in)\b",
            r" \1",
            text,
            flags=re.IGNORECASE
        )

        # Remove a comma left at the beginning
        # after removing a filler word.
        text = re.sub(
            r"^\s*,\s*",
            "",
            text
        )

        return text

    # -------------------------------------------------
    # 3. Normalize Whitespace
    # -------------------------------------------------

    def normalize_whitespace(self, text):
        """
        Replace multiple spaces with a single space.
        """

        return re.sub(
            r"\s+",
            " ",
            text
        ).strip()

    # -------------------------------------------------
    # 4. Normalize Case and Technical Terms
    # -------------------------------------------------

    def normalize_case(self, text):
        """
        Normalize known technical terms and
        first-person pronoun capitalization.
        """

        # Process longer terms first.
        terms = sorted(
            self.TECHNICAL_TERMS.items(),
            key=lambda item: len(item[0]),
            reverse=True
        )

        for term, normalized_term in terms:

            text = re.sub(
                r"\b" + re.escape(term) + r"\b",
                normalized_term,
                text,
                flags=re.IGNORECASE
            )

        # Normalize first-person pronoun.
        text = re.sub(
            r"\bi\b",
            "I",
            text
        )

        return text

    # -------------------------------------------------
    # 5. Handle Interrupted Speech
    # -------------------------------------------------

    def handle_interruption(self, text):
        """
        Detect whether the speaker was interrupted.

        An interruption is detected only when the
        transcript ends with:
            -
            —
            ...

        A normal sentence ending with '.' is NOT
        considered an interruption.
        """

        cleaned_text = text.rstrip()

        interrupted = (
            cleaned_text.endswith("-")
            or cleaned_text.endswith("—")
            or cleaned_text.endswith("...")
        )

        return interrupted

    # -------------------------------------------------
    # 6. Correct Punctuation
    # -------------------------------------------------

    def correct_punctuation(self, text):
        """
        Normalize basic punctuation while preserving
        interruption markers.
        """

        text = text.strip()

        if not text:
            return text

        # Check interruption before changing punctuation.
        is_interrupted = self.handle_interruption(
            text
        )

        # Remove spaces before punctuation.
        text = re.sub(
            r"\s+([,.!?])",
            r"\1",
            text
        )

        # Add missing spaces after punctuation.
        text = re.sub(
            r"([,.!?])([A-Za-z])",
            r"\1 \2",
            text
        )

        # Add full stop only when the transcript
        # is not interrupted.
        if not is_interrupted:

            if text[-1] not in ".!?":

                text += "."

        return text

    # -------------------------------------------------
    # 7. Detect Partial Answer
    # -------------------------------------------------

    def detect_partial_answer(self, text):
        """
        Detect potentially incomplete short answers.

        Answers containing three words or fewer
        are flagged as potentially partial.
        """

        words = text.split()

        return len(words) <= 3

    # -------------------------------------------------
    # 8. Complete Cleaning Pipeline
    # -------------------------------------------------

    def clean(self, text):
        """
        Apply the complete transcript normalization
        pipeline.

        Returns:
            Dictionary containing:
            - raw_text
            - normalized_text
            - status
            - is_interrupted
            - is_partial
        """

        # Preserve the original STT transcript.
        raw_text = text

        # -------------------------------------------------
        # Silence Check
        # -------------------------------------------------

        if self.detect_silence(text):

            return {
                "raw_text": raw_text,
                "normalized_text": "",
                "status": "no_response",
                "is_interrupted": False,
                "is_partial": False
            }

        # -------------------------------------------------
        # Normalization Pipeline
        # -------------------------------------------------

        normalized_text = self.remove_filler_words(
            text
        )

        normalized_text = self.normalize_whitespace(
            normalized_text
        )

        normalized_text = self.normalize_case(
            normalized_text
        )

        # Detect interruption before punctuation
        # correction.
        is_interrupted = self.handle_interruption(
            normalized_text
        )

        normalized_text = self.correct_punctuation(
            normalized_text
        )

        is_partial = self.detect_partial_answer(
            normalized_text
        )

        # -------------------------------------------------
        # Final Result
        # -------------------------------------------------

        return {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "status": "response_detected",
            "is_interrupted": is_interrupted,
            "is_partial": is_partial
        }


# -----------------------------------------------------
# Optional Direct Test
# -----------------------------------------------------

if __name__ == "__main__":

    cleaner = TranscriptCleaner()

    sample_text = (
        "Um, I have like three years of experience "
        "in backend development. I have worked with "
        "python, django, fast api, docker and postgresql."
    )

    result = cleaner.clean(sample_text)

    print("=" * 70)
    print("ZecPath - Transcript Cleaner")
    print("=" * 70)

    print("\nRaw transcript:")
    print(result["raw_text"])

    print("\nNormalized transcript:")
    print(result["normalized_text"])

    print("\nStatus:")
    print(result["status"])

    print("\nInterrupted:")
    print(result["is_interrupted"])

    print("\nPartial answer:")
    print(result["is_partial"])

    print("=" * 70)