import json
import os
import re


class ConfidenceAnalyzer:

    # Words and phrases that may indicate hesitation
    HESITATION_PATTERNS = {
        "um",
        "uh",
        "hmm",
        "erm",
        "er",
        "ah",
        "i think",
        "i guess",
        "maybe",
        "perhaps",
        "probably"
    }

    # Phrases that may indicate uncertainty
    UNCERTAINTY_PATTERNS = {
        "i'm not sure",
        "im not sure",
        "not sure",
        "i don't know",
        "i dont know",
        "possibly",
        "might be",
        "could be",
        "i believe",
        "as far as i know",
        "approximately",
        "around"
    }

    # Threshold for considering a pause long
    LONG_PAUSE_THRESHOLD = 2.0

    # Maximum number of follow-up indicators used in this module
    MAX_INDICATOR_PENALTY = 100

    def normalize_text(self, text):
        """
        Normalize response text.
        """
        if not text:
            return ""

        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)

        return text

    def get_words(self, text):
        """
        Extract words from response text.
        """
        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return []

        return re.findall(r"\b[\w']+\b", normalized_text)

    def detect_hesitation(self, text):
        """
        Detect hesitation words and phrases.
        """

        normalized_text = self.normalize_text(text)

        detected = []

        for pattern in self.HESITATION_PATTERNS:

            if re.search(
                r"\b" + re.escape(pattern) + r"\b",
                normalized_text
            ):
                detected.append(pattern)

        return {
            "hesitation_detected": len(detected) > 0,
            "hesitation_count": len(detected),
            "hesitation_patterns": detected
        }

    def detect_uncertainty(self, text):
        """
        Detect uncertainty phrases.
        """

        normalized_text = self.normalize_text(text)

        detected = []

        for pattern in self.UNCERTAINTY_PATTERNS:

            if re.search(
                r"\b" + re.escape(pattern) + r"\b",
                normalized_text
            ):
                detected.append(pattern)

        return {
            "uncertainty_detected": len(detected) > 0,
            "uncertainty_count": len(detected),
            "uncertainty_patterns": detected
        }

    def detect_repeated_words(self, text):
        """
        Detect immediate repeated words.

        Example:
        'I I worked on a project'
        """

        words = self.get_words(text)

        repeated_words = []

        for i in range(1, len(words)):

            if words[i] == words[i - 1]:

                if words[i] not in repeated_words:
                    repeated_words.append(words[i])

        return {
            "repetition_detected": len(repeated_words) > 0,
            "repetition_count": len(repeated_words),
            "repeated_words": repeated_words
        }

    def detect_long_pauses(self, pause_durations):
        """
        Detect long pauses.

        pause_durations should contain pause duration
        values in seconds.

        Example:
        [0.5, 1.2, 3.5, 0.8]
        """

        if not pause_durations:
            return {
                "long_pause_detected": False,
                "long_pause_count": 0,
                "long_pause_durations": []
            }

        long_pauses = [
            pause for pause in pause_durations
            if pause >= self.LONG_PAUSE_THRESHOLD
        ]

        return {
            "long_pause_detected": len(long_pauses) > 0,
            "long_pause_count": len(long_pauses),
            "long_pause_durations": long_pauses
        }

    def calculate_words_per_minute(
        self,
        word_count,
        duration_seconds
    ):
        """
        Calculate response speaking pace.
        """

        if duration_seconds <= 0:
            return 0

        minutes = duration_seconds / 60

        return round(word_count / minutes, 2)

    def classify_pace(self, words_per_minute):
        """
        Classify speaking pace.
        """

        if words_per_minute == 0:
            return "unknown"

        if words_per_minute < 80:
            return "slow"

        if words_per_minute <= 160:
            return "normal"

        return "fast"

    def calculate_confidence_score(
        self,
        hesitation_count,
        uncertainty_count,
        repetition_count,
        long_pause_count,
        pace
    ):
        """
        Calculate behavioral confidence indicator.

        Starting score = 100.

        Penalties:
        Hesitation       = -5 each
        Uncertainty      = -5 each
        Repetition       = -5 each
        Long pause       = -5 each
        Slow/fast pace   = -5
        """

        score = 100

        score -= hesitation_count * 5
        score -= uncertainty_count * 5
        score -= repetition_count * 5
        score -= long_pause_count * 5

        if pace in ["slow", "fast"]:
            score -= 5

        score = max(0, min(100, score))

        return round(score, 2)

    def classify_confidence(self, score):
        """
        Classify the confidence indicator.
        """

        if score >= 80:
            return "high"

        if score >= 60:
            return "moderate"

        return "low"

    def analyze_response(
        self,
        candidate_id,
        question_id,
        response,
        duration_seconds=0,
        pause_durations=None
    ):
        """
        Perform complete confidence analysis.
        """

        if pause_durations is None:
            pause_durations = []

        words = self.get_words(response)

        word_count = len(words)

        hesitation = self.detect_hesitation(response)

        uncertainty = self.detect_uncertainty(response)

        repetition = self.detect_repeated_words(response)

        long_pauses = self.detect_long_pauses(
            pause_durations
        )

        words_per_minute = self.calculate_words_per_minute(
            word_count,
            duration_seconds
        )

        pace = self.classify_pace(
            words_per_minute
        )

        confidence_score = self.calculate_confidence_score(
            hesitation_count=hesitation["hesitation_count"],
            uncertainty_count=uncertainty["uncertainty_count"],
            repetition_count=repetition["repetition_count"],
            long_pause_count=long_pauses["long_pause_count"],
            pace=pace
        )

        confidence_level = self.classify_confidence(
            confidence_score
        )

        return {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "response": response,
            "word_count": word_count,
            "duration_seconds": duration_seconds,
            "words_per_minute": words_per_minute,
            "pace": pace,
            "hesitation": hesitation,
            "uncertainty": uncertainty,
            "repetition": repetition,
            "long_pauses": long_pauses,
            "confidence_score": confidence_score,
            "confidence_level": confidence_level
        }

    def save_result(self, result):
        """
        Save confidence analysis result.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(
            results_dir,
            exist_ok=True
        )

        output_file = os.path.join(
            results_dir,
            "confidence_analysis_results.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        return output_file


def main():

    analyzer = ConfidenceAnalyzer()

    sample_response = (
        "I think I worked on a backend project. "
        "I, I developed the APIs using Python and Django. "
        "Maybe I can explain more about the project."
    )

    # Example pause durations in seconds
    pause_durations = [
        0.5,
        1.0,
        2.8,
        0.7,
        3.2
    ]

    result = analyzer.analyze_response(
        candidate_id="candidate_006",
        question_id="HR_TEAM_001",
        response=sample_response,
        duration_seconds=45,
        pause_durations=pause_durations
    )

    output_file = analyzer.save_result(result)

    print("DAY 36 — CONFIDENCE ANALYZER")
    print("=" * 50)

    print(
        f"Candidate: "
        f"{result['candidate_id']}"
    )

    print(
        f"Question ID: "
        f"{result['question_id']}"
    )

    print(
        f"Word Count: "
        f"{result['word_count']}"
    )

    print(
        f"Words Per Minute: "
        f"{result['words_per_minute']}"
    )

    print(
        f"Pace: "
        f"{result['pace']}"
    )

    print(
        f"Hesitation Count: "
        f"{result['hesitation']['hesitation_count']}"
    )

    print(
        f"Uncertainty Count: "
        f"{result['uncertainty']['uncertainty_count']}"
    )

    print(
        f"Repeated Words: "
        f"{result['repetition']['repeated_words']}"
    )

    print(
        f"Long Pause Count: "
        f"{result['long_pauses']['long_pause_count']}"
    )

    print(
        f"Confidence Score: "
        f"{result['confidence_score']}/100"
    )

    print(
        f"Confidence Level: "
        f"{result['confidence_level']}"
    )

    print(
        f"Saved Result: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()