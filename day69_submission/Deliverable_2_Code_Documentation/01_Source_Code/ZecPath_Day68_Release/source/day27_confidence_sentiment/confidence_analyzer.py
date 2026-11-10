import json
import os
import re
from datetime import datetime, timezone


class ConfidenceAnalyzer:
    """
    Analyzes communication signals from a candidate's response.

    This module focuses on communication behavior only.
    It does not make psychological or personality judgments.
    """

    # --------------------------------------------------
    # Hesitation patterns
    # --------------------------------------------------

    HESITATION_PATTERNS = [
        "um",
        "uh",
        "hmm",
        "er",
        "erm",
        "ah",
        "i think",
        "i guess",
        "maybe",
        "perhaps",
        "probably",
        "i'm not sure",
        "im not sure",
        "not sure",
        "i don't know",
        "i dont know",
        "around",
        "approximately",
        "i believe",
        "as far as i know"
    ]

    # --------------------------------------------------
    # Uncertainty patterns
    # --------------------------------------------------

    UNCERTAINTY_PATTERNS = [
        "i think",
        "i guess",
        "maybe",
        "perhaps",
        "probably",
        "i'm not sure",
        "im not sure",
        "not sure",
        "i don't know",
        "i dont know",
        "around",
        "approximately",
        "i believe",
        "as far as i know",
        "possibly",
        "might be",
        "could be"
    ]

    # --------------------------------------------------
    # Text normalization
    # --------------------------------------------------

    def normalize_text(self, text):
        """
        Normalize the candidate response.

        - Convert to lowercase
        - Remove unnecessary spaces
        """

        if not isinstance(text, str):
            return ""

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    # --------------------------------------------------
    # Hesitation detection
    # --------------------------------------------------

    def detect_hesitation(self, text):
        """
        Detect hesitation patterns in the response.
        """

        normalized_text = self.normalize_text(text)

        detected_patterns = []

        for pattern in self.HESITATION_PATTERNS:

            # Multi-word pattern
            if " " in pattern:

                if pattern in normalized_text:
                    detected_patterns.append(pattern)

            # Single-word pattern
            else:

                if re.search(
                    rf"\b{re.escape(pattern)}\b",
                    normalized_text
                ):
                    detected_patterns.append(pattern)

        return {
            "detected": len(detected_patterns) > 0,
            "count": len(detected_patterns),
            "patterns": detected_patterns
        }

    # --------------------------------------------------
    # Uncertainty detection
    # --------------------------------------------------

    def detect_uncertainty(self, text):
        """
        Detect uncertainty expressions in the response.
        """

        normalized_text = self.normalize_text(text)

        detected_patterns = []

        for pattern in self.UNCERTAINTY_PATTERNS:

            # Multi-word pattern
            if " " in pattern:

                if pattern in normalized_text:
                    detected_patterns.append(pattern)

            # Single-word pattern
            else:

                if re.search(
                    rf"\b{re.escape(pattern)}\b",
                    normalized_text
                ):
                    detected_patterns.append(pattern)

        return {
            "detected": len(detected_patterns) > 0,
            "count": len(detected_patterns),
            "patterns": detected_patterns
        }

    # --------------------------------------------------
    # Response length
    # --------------------------------------------------

    def measure_response_length(self, text):
        """
        Measure response length.

        Returns:
        - word count
        - character count
        """

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return {
                "word_count": 0,
                "character_count": 0
            }

        words = normalized_text.split()

        return {
            "word_count": len(words),
            "character_count": len(normalized_text)
        }

    # --------------------------------------------------
    # Words per minute
    # --------------------------------------------------

    def calculate_words_per_minute(
        self,
        word_count,
        duration_seconds
    ):
        """
        Calculate speaking pace in words per minute.

        Formula:

        WPM = word_count / duration_minutes
        """

        if duration_seconds <= 0:
            return 0.0

        duration_minutes = duration_seconds / 60

        wpm = word_count / duration_minutes

        return round(
            wpm,
            2
        )

    # --------------------------------------------------
    # Pace classification
    # --------------------------------------------------

    def classify_pace(self, words_per_minute):
        """
        Classify speaking pace.

        < 80 WPM      -> slow
        80-160 WPM    -> normal
        > 160 WPM     -> fast
        """

        if words_per_minute < 80:

            return "slow"

        elif words_per_minute <= 160:

            return "normal"

        else:

            return "fast"

    # --------------------------------------------------
    # Complete pace analysis
    # --------------------------------------------------

    def analyze_pace(
        self,
        word_count,
        duration_seconds
    ):
        """
        Analyze response speaking pace.
        """

        wpm = self.calculate_words_per_minute(
            word_count,
            duration_seconds
        )

        return {
            "duration_seconds": duration_seconds,
            "words_per_minute": wpm,
            "classification": self.classify_pace(wpm)
        }

    # --------------------------------------------------
    # Complete response analysis
    # --------------------------------------------------

    def analyze_response(
        self,
        candidate_id,
        question_id,
        answer,
        duration_seconds
    ):
        """
        Perform complete confidence analysis.
        """

        normalized_answer = self.normalize_text(
            answer
        )

        # Response length
        response_length = (
            self.measure_response_length(
                normalized_answer
            )
        )

        # Hesitation
        hesitation = (
            self.detect_hesitation(
                normalized_answer
            )
        )

        # Uncertainty
        uncertainty = (
            self.detect_uncertainty(
                normalized_answer
            )
        )

        # Pace
        pace = self.analyze_pace(
            response_length["word_count"],
            duration_seconds
        )

        result = {

            "candidate_id": candidate_id,

            "question_id": question_id,

            "raw_answer": answer,

            "normalized_answer": normalized_answer,

            "response_length": response_length,

            "pace": pace,

            "hesitation": hesitation,

            "uncertainty": uncertainty,

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return result

    # --------------------------------------------------
    # Save result
    # --------------------------------------------------

    def save_result(
        self,
        result,
        filename
    ):
        """
        Save confidence analysis result
        inside the results folder.
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
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        return file_path


# ======================================================
# Main
# ======================================================

if __name__ == "__main__":

    analyzer = ConfidenceAnalyzer()

    # Example candidate response
    candidate_answer = (
        "Um, I think I have maybe three years "
        "of backend development experience."
    )

    result = analyzer.analyze_response(

        candidate_id="candidate_006",

        question_id="BACKEND_EXP_001",

        answer=candidate_answer,

        duration_seconds=8.0
    )

    print("=" * 70)
    print("ZecPath - Day 27")
    print("CONFIDENCE ANALYSIS")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # Save JSON result
    filename = (
        "candidate_006_confidence_analysis.json"
    )

    saved_path = analyzer.save_result(
        result,
        filename
    )

    print("\nConfidence analysis saved to:")
    print(saved_path)

    print("=" * 70)