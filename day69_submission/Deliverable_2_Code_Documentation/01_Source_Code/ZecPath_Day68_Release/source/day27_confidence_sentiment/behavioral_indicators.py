import json
import os
from datetime import datetime, timezone


class BehavioralIndicators:
    """
    Creates communication strength indicators by combining
    confidence, sentiment, and contradiction signals.

    These indicators describe communication behavior only.
    They are not psychological or personality assessments.
    """

    STRONG_SCORE = 80
    MODERATE_SCORE = 60

    # --------------------------------------------------
    # Score classification
    # --------------------------------------------------

    def classify_score(self, score):
        """
        Classify a score into a communication strength level.
        """

        if score >= self.STRONG_SCORE:
            return "strong"

        elif score >= self.MODERATE_SCORE:
            return "moderate"

        return "needs_improvement"

    # --------------------------------------------------
    # Confidence indicator
    # --------------------------------------------------

    def calculate_confidence_indicator(
        self,
        hesitation_count,
        uncertainty_count,
        pace_classification,
        answer_status="valid"
    ):
        """
        Calculate communication confidence indicator.

        Hesitation and uncertainty signals reduce the score.
        Very slow or very fast pace receives a small adjustment.
        """

        score = 100

        # Hesitation impact
        score -= hesitation_count * 10

        # Uncertainty impact
        score -= uncertainty_count * 10

        # Pace impact
        if pace_classification in ["slow", "fast"]:
            score -= 5

        # Answer status impact
        if answer_status == "vague":
            score -= 20

        elif answer_status == "off_topic":
            score -= 30

        elif answer_status == "no_response":
            score = 0

        # Keep score within 0-100
        score = max(
            0,
            min(100, score)
        )

        return round(score, 2)

    # --------------------------------------------------
    # Clarity indicator
    # --------------------------------------------------

    def calculate_clarity_indicator(
        self,
        response_length,
        hesitation_count,
        answer_status
    ):
        """
        Calculate communication clarity indicator.
        """

        if answer_status == "no_response":
            return 0.0

        word_count = response_length.get(
            "word_count",
            0
        )

        if word_count == 0:
            return 0.0

        # Base score
        score = 100

        # Very short response
        if word_count <= 3:
            score -= 20

        # Reasonable response
        elif word_count <= 30:
            score = 100

        # Very long response
        else:
            score -= 5

        # Hesitation impact
        score -= hesitation_count * 5

        # Answer status impact
        if answer_status == "vague":
            score -= 20

        elif answer_status == "off_topic":
            score -= 40

        score = max(
            0,
            min(100, score)
        )

        return round(score, 2)

    # --------------------------------------------------
    # Engagement indicator
    # --------------------------------------------------

    def calculate_engagement_indicator(
        self,
        response_length,
        sentiment,
        answer_status
    ):
        """
        Calculate communication engagement indicator.

        Response length and sentiment are used as
        communication signals.
        """

        if answer_status == "no_response":
            return 0.0

        word_count = response_length.get(
            "word_count",
            0
        )

        # Base engagement
        score = 60

        # Response length
        if word_count >= 15:
            score += 20

        elif word_count >= 7:
            score += 15

        elif word_count >= 4:
            score += 10

        else:
            score -= 10

        # Sentiment
        if sentiment == "positive":
            score += 15

        elif sentiment == "negative":
            score -= 10

        # Answer status
        if answer_status == "vague":
            score -= 20

        elif answer_status == "off_topic":
            score -= 30

        score = max(
            0,
            min(100, score)
        )

        return round(score, 2)

    # --------------------------------------------------
    # Consistency indicator
    # --------------------------------------------------

    def calculate_consistency_indicator(
        self,
        contradiction_detected
    ):
        """
        Calculate consistency based on contradiction detection.
        """

        if contradiction_detected:
            return 30.0

        return 100.0

    # --------------------------------------------------
    # Overall communication strength
    # --------------------------------------------------

    def calculate_communication_strength(
        self,
        confidence,
        clarity,
        engagement,
        consistency
    ):
        """
        Calculate the overall communication strength.

        Equal weighting is used for all four indicators.
        """

        score = (
            confidence
            + clarity
            + engagement
            + consistency
        ) / 4

        return round(
            score,
            2
        )

    # --------------------------------------------------
    # Build complete behavioral report
    # --------------------------------------------------

    def build_indicators(
        self,
        candidate_id,
        question_id,
        confidence_analysis,
        sentiment_analysis,
        contradiction_analysis,
        answer_status="valid"
    ):
        """
        Build the complete behavioral indicators report.
        """

        # ----------------------------------------------
        # Extract confidence information
        # ----------------------------------------------

        hesitation = confidence_analysis.get(
            "hesitation",
            {}
        )

        uncertainty = confidence_analysis.get(
            "uncertainty",
            {}
        )

        response_length = confidence_analysis.get(
            "response_length",
            {}
        )

        pace = confidence_analysis.get(
            "pace",
            {}
        )

        hesitation_count = hesitation.get(
            "count",
            0
        )

        uncertainty_count = uncertainty.get(
            "count",
            0
        )

        pace_classification = pace.get(
            "classification",
            "unknown"
        )

        # ----------------------------------------------
        # Extract sentiment
        # ----------------------------------------------

        sentiment_data = sentiment_analysis.get(
            "sentiment_analysis",
            sentiment_analysis
        )

        sentiment = sentiment_data.get(
            "sentiment",
            "neutral"
        )

        sentiment_score = sentiment_data.get(
            "sentiment_score",
            50.0
        )

        # ----------------------------------------------
        # Extract contradiction
        # ----------------------------------------------

        contradiction_data = contradiction_analysis.get(
            "contradiction_analysis",
            contradiction_analysis
        )

        contradiction_detected = contradiction_data.get(
            "detected",
            False
        )

        # ----------------------------------------------
        # Calculate indicators
        # ----------------------------------------------

        confidence_score = (
            self.calculate_confidence_indicator(
                hesitation_count,
                uncertainty_count,
                pace_classification,
                answer_status
            )
        )

        clarity_score = (
            self.calculate_clarity_indicator(
                response_length,
                hesitation_count,
                answer_status
            )
        )

        engagement_score = (
            self.calculate_engagement_indicator(
                response_length,
                sentiment,
                answer_status
            )
        )

        consistency_score = (
            self.calculate_consistency_indicator(
                contradiction_detected
            )
        )

        communication_strength = (
            self.calculate_communication_strength(
                confidence_score,
                clarity_score,
                engagement_score,
                consistency_score
            )
        )

        # ----------------------------------------------
        # Build result
        # ----------------------------------------------

        result = {

            "candidate_id": candidate_id,

            "question_id": question_id,

            "communication_indicators": {

                "confidence": {
                    "score": confidence_score,
                    "level": self.classify_score(
                        confidence_score
                    )
                },

                "clarity": {
                    "score": clarity_score,
                    "level": self.classify_score(
                        clarity_score
                    )
                },

                "engagement": {
                    "score": engagement_score,
                    "level": self.classify_score(
                        engagement_score
                    )
                },

                "consistency": {
                    "score": consistency_score,
                    "level": self.classify_score(
                        consistency_score
                    )
                },

                "communication_strength": {
                    "score": communication_strength,
                    "level": self.classify_score(
                        communication_strength
                    )
                }
            },

            "behavioral_signals": {

                "hesitation_count": hesitation_count,

                "uncertainty_count": uncertainty_count,

                "response_word_count": response_length.get(
                    "word_count",
                    0
                ),

                "pace": pace_classification,

                "sentiment": sentiment,

                "sentiment_score": sentiment_score,

                "contradiction_detected": (
                    contradiction_detected
                )
            },

            "answer_status": answer_status,

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
        Save behavioral indicators report as JSON.
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

    builder = BehavioralIndicators()

    # --------------------------------------------------
    # Example output from Deliverable 1
    # --------------------------------------------------

    confidence_analysis = {

        "response_length": {
            "word_count": 14,
            "character_count": 82
        },

        "pace": {
            "duration_seconds": 8.0,
            "words_per_minute": 105.0,
            "classification": "normal"
        },

        "hesitation": {
            "detected": False,
            "count": 0,
            "patterns": []
        },

        "uncertainty": {
            "detected": False,
            "count": 0,
            "patterns": []
        }
    }

    # --------------------------------------------------
    # Example output from Deliverable 2
    # --------------------------------------------------

    sentiment_analysis = {

        "sentiment_analysis": {

            "sentiment": "positive",

            "sentiment_score": 100.0,

            "positive_count": 3,

            "negative_count": 0,

            "positive_words": [
                "enjoy",
                "successfully",
                "confident"
            ],

            "negative_words": []
        }
    }

    # --------------------------------------------------
    # Example contradiction result
    # --------------------------------------------------

    contradiction_analysis = {

        "contradiction_analysis": {

            "detected": False,

            "count": 0,

            "types": [],

            "details": []
        }
    }

    # --------------------------------------------------
    # Generate behavioral report
    # --------------------------------------------------

    result = builder.build_indicators(

        candidate_id="candidate_006",

        question_id="BACKEND_SKILLS_001",

        confidence_analysis=confidence_analysis,

        sentiment_analysis=sentiment_analysis,

        contradiction_analysis=contradiction_analysis,

        answer_status="valid"
    )

    print("=" * 70)
    print("ZecPath - Day 27")
    print("BEHAVIORAL INDICATORS REPORT")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # --------------------------------------------------
    # Save report
    # --------------------------------------------------

    filename = (
        "candidate_006_behavioral_indicators.json"
    )

    saved_path = builder.save_result(
        result,
        filename
    )

    print("\nBehavioral indicators saved to:")
    print(saved_path)

    print("=" * 70)