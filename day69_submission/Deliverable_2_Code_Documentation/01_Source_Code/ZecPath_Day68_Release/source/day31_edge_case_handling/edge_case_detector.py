import json
import re
from datetime import datetime
from pathlib import Path


class EdgeCaseDetector:
    """
    Day 31 - Edge Case & Failure Handling

    Detects common problems that can occur during
    AI-based candidate screening:

    1. Missing answers
    2. Poor audio quality
    3. Background noise
    4. Language mixing
    """

    # ---------------------------------------------------------
    # THRESHOLDS
    # ---------------------------------------------------------

    MIN_AUDIO_QUALITY = 0.50
    MAX_BACKGROUND_NOISE = 0.70

    # ---------------------------------------------------------
    # LANGUAGE MARKERS
    # ---------------------------------------------------------

    MIXED_LANGUAGE_MARKERS = {
        "njan",
        "enikku",
        "ente",
        "cheythu",
        "cheythittundu",
        "und",
        "illa",
        "aanu",
        "oru",
        "pinne",
        "nalla"
    }

    # ---------------------------------------------------------
    # TEXT NORMALIZATION
    # ---------------------------------------------------------

    def normalize_text(self, text):
        """
        Clean and normalize transcript text.
        """

        if text is None:
            return ""

        text = str(text).strip()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        return text

    # ---------------------------------------------------------
    # TOKENIZATION
    # ---------------------------------------------------------

    def tokenize(self, text):
        """
        Convert text into lowercase words.
        """

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return []

        return normalized_text.lower().split()

    # ---------------------------------------------------------
    # MISSING ANSWER DETECTION
    # ---------------------------------------------------------

    def detect_missing_answer(self, transcript):
        """
        Detect whether the candidate provided
        an empty or missing answer.
        """

        normalized_text = self.normalize_text(transcript)

        return normalized_text == ""

    # ---------------------------------------------------------
    # POOR AUDIO DETECTION
    # ---------------------------------------------------------

    def detect_poor_audio(self, audio_quality):
        """
        Detect poor audio based on an audio-quality
        score between 0 and 1.

        Example:
        0.90 -> good
        0.70 -> acceptable
        0.30 -> poor
        """

        try:
            audio_quality = float(audio_quality)
        except (TypeError, ValueError):
            return True

        return audio_quality < self.MIN_AUDIO_QUALITY

    # ---------------------------------------------------------
    # BACKGROUND NOISE DETECTION
    # ---------------------------------------------------------

    def detect_background_noise(self, background_noise):
        """
        Detect excessive background noise.

        Noise value:
        0.0 -> no significant noise
        1.0 -> very high noise
        """

        try:
            background_noise = float(background_noise)
        except (TypeError, ValueError):
            return True

        return background_noise > self.MAX_BACKGROUND_NOISE

    # ---------------------------------------------------------
    # LANGUAGE MIXING DETECTION
    # ---------------------------------------------------------

    def detect_language_mixing(self, transcript):
        """
        Detect common language-mixing markers.

        This is a deterministic baseline detector.
        It is intended to identify obvious mixed-language
        responses rather than perform full language detection.
        """

        tokens = self.tokenize(transcript)

        if not tokens:
            return False

        for token in tokens:

            # Remove punctuation
            clean_token = re.sub(
                r"[^\w]",
                "",
                token
            )

            if clean_token in self.MIXED_LANGUAGE_MARKERS:
                return True

        return False

    # ---------------------------------------------------------
    # MAIN DETECTION METHOD
    # ---------------------------------------------------------

    def detect(
        self,
        transcript,
        audio_quality=1.0,
        background_noise=0.0
    ):
        """
        Detect all possible edge cases.

        Returns a structured detection object.
        """

        transcript = self.normalize_text(transcript)

        detected_errors = []

        # 1. Missing answer
        if self.detect_missing_answer(transcript):
            detected_errors.append("missing_answer")

        # 2. Poor audio
        if self.detect_poor_audio(audio_quality):
            detected_errors.append("poor_audio")

        # 3. Background noise
        if self.detect_background_noise(background_noise):
            detected_errors.append("background_noise")

        # 4. Language mixing
        if self.detect_language_mixing(transcript):
            detected_errors.append("language_mixing")

        # -----------------------------------------------------
        # Determine primary error
        # -----------------------------------------------------

        if detected_errors:

            # Priority order
            priority_order = [
                "missing_answer",
                "poor_audio",
                "background_noise",
                "language_mixing"
            ]

            primary_error = None

            for error in priority_order:

                if error in detected_errors:
                    primary_error = error
                    break

            return {
                "status": "edge_case",
                "primary_error": primary_error,
                "detected_errors": detected_errors,
                "transcript": transcript,
                "audio_quality": audio_quality,
                "background_noise": background_noise
            }

        # -----------------------------------------------------
        # Normal response
        # -----------------------------------------------------

        return {
            "status": "normal",
            "primary_error": None,
            "detected_errors": [],
            "transcript": transcript,
            "audio_quality": audio_quality,
            "background_noise": background_noise
        }

    # ---------------------------------------------------------
    # BATCH ANALYSIS
    # ---------------------------------------------------------

    def analyze_cases(self, test_cases):
        """
        Analyze multiple edge-case test cases.
        """

        results = []

        for case in test_cases:

            detection = self.detect(
                transcript=case.get(
                    "transcript",
                    ""
                ),
                audio_quality=case.get(
                    "audio_quality",
                    1.0
                ),
                background_noise=case.get(
                    "background_noise",
                    0.0
                )
            )

            expected_error = case.get(
                "expected_error"
            )

            actual_error = detection[
                "primary_error"
            ]

            matched = (
                actual_error == expected_error
            )

            results.append({
                "case_id": case.get(
                    "case_id",
                    "UNKNOWN"
                ),
                "expected_error": expected_error,
                "actual_error": actual_error,
                "matched": matched,
                "detection": detection
            })

        return results

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    def save_results(self, results):
        """
        Save edge-case detection results.
        """

        output_path = (
            Path(__file__).parent
            / "results"
            / "edge_case_detection_results.json"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        matched = sum(
            1
            for result in results
            if result["matched"]
        )

        mismatched = (
            len(results) - matched
        )

        accuracy = (
            (matched / len(results)) * 100
            if results
            else 0
        )

        report = {
            "report_type": "Edge Case Detection Results",
            "total_cases": len(results),
            "matched_cases": matched,
            "mismatched_cases": mismatched,
            "accuracy": round(accuracy, 2),
            "results": results,
            "created_at": (
                datetime.utcnow().isoformat()
                + "Z"
            )
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        return output_path


# =============================================================
# STANDALONE TEST
# =============================================================

if __name__ == "__main__":

    detector = EdgeCaseDetector()

    test_cases = [

        # -----------------------------------------------------
        # Normal response
        # -----------------------------------------------------

        {
            "case_id": "NORMAL_001",
            "transcript": (
                "I have three years of "
                "Python development experience."
            ),
            "audio_quality": 0.95,
            "background_noise": 0.10,
            "expected_error": None
        },

        # -----------------------------------------------------
        # Poor audio
        # -----------------------------------------------------

        {
            "case_id": "POOR_AUDIO_001",
            "transcript": (
                "I have three years of "
                "Python experience."
            ),
            "audio_quality": 0.30,
            "background_noise": 0.10,
            "expected_error": "poor_audio"
        },

        # -----------------------------------------------------
        # Missing answer
        # -----------------------------------------------------

        {
            "case_id": "MISSING_ANSWER_001",
            "transcript": "",
            "audio_quality": 0.95,
            "background_noise": 0.10,
            "expected_error": "missing_answer"
        },

        # -----------------------------------------------------
        # Background noise
        # -----------------------------------------------------

        {
            "case_id": "BACKGROUND_NOISE_001",
            "transcript": (
                "I have three years of "
                "Python experience."
            ),
            "audio_quality": 0.90,
            "background_noise": 0.85,
            "expected_error": "background_noise"
        },

        # -----------------------------------------------------
        # Language mixing
        # -----------------------------------------------------

        {
            "case_id": "LANGUAGE_MIXING_001",
            "transcript": (
                "I have three years experience, "
                "njan Python use cheythittundu."
            ),
            "audio_quality": 0.90,
            "background_noise": 0.10,
            "expected_error": "language_mixing"
        }
    ]

    results = detector.analyze_cases(
        test_cases
    )

    matched = sum(
        1
        for result in results
        if result["matched"]
    )

    print("\nEdge Case Detection Results")
    print("=" * 60)

    for result in results:

        print(
            f"{result['case_id']}: "
            f"expected={result['expected_error']}, "
            f"actual={result['actual_error']}, "
            f"matched={result['matched']}"
        )

    print("=" * 60)

    print(
        f"Total cases : {len(results)}"
    )

    print(
        f"Matched     : {matched}"
    )

    print(
        f"Mismatched  : "
        f"{len(results) - matched}"
    )

    print(
        f"Accuracy    : "
        f"{(matched / len(results)) * 100:.1f}%"
    )

    output_path = detector.save_results(
        results
    )

    print(
        f"\nResults saved to: {output_path}"
    )