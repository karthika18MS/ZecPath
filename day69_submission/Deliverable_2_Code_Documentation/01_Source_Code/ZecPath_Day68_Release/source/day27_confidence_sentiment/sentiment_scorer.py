import json
import os
import re
from datetime import datetime, timezone


class SentimentScorer:
    """
    Rule-based sentiment scoring module for candidate responses.

    The module identifies positive, negative, and neutral
    communication signals from the candidate's answer.

    This is a communication-level sentiment indicator.
    It is not a psychological or personality assessment.
    """

    # --------------------------------------------------
    # Positive sentiment words
    # --------------------------------------------------

    POSITIVE_WORDS = [
        "confident",
        "confidence",
        "enjoy",
        "enjoyed",
        "enjoying",
        "good",
        "great",
        "excellent",
        "success",
        "successful",
        "successfully",
        "achieved",
        "achievement",
        "improved",
        "improvement",
        "positive",
        "interested",
        "interest",
        "motivated",
        "motivation",
        "excited",
        "exciting",
        "love",
        "like",
        "comfortable",
        "strong",
        "strength",
        "effective",
        "beneficial",
        "progress",
        "growth"
    ]

    # --------------------------------------------------
    # Negative sentiment words
    # --------------------------------------------------

    NEGATIVE_WORDS = [
        "difficult",
        "difficulty",
        "difficulties",
        "problem",
        "problems",
        "failed",
        "failure",
        "bad",
        "poor",
        "negative",
        "hate",
        "hated",
        "dislike",
        "worried",
        "worry",
        "frustrated",
        "frustration",
        "confused",
        "confusion",
        "unable",
        "struggle",
        "struggled",
        "struggling",
        "weak",
        "weakness",
        "issue",
        "issues",
        "challenge",
        "challenges",
        "stress",
        "stressed"
    ]

    # --------------------------------------------------
    # Text normalization
    # --------------------------------------------------

    def normalize_text(self, text):
        """
        Convert text to lowercase and normalize whitespace.
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
    # Tokenization
    # --------------------------------------------------

    def tokenize(self, text):
        """
        Convert normalized text into individual words.
        """

        normalized_text = self.normalize_text(text)

        return re.findall(
            r"\b[\w'-]+\b",
            normalized_text
        )

    # --------------------------------------------------
    # Positive word detection
    # --------------------------------------------------

    def detect_positive_words(self, text):
        """
        Detect positive sentiment words.
        """

        tokens = self.tokenize(text)

        detected_words = []

        for word in tokens:

            if word in self.POSITIVE_WORDS:
                detected_words.append(word)

        return detected_words

    # --------------------------------------------------
    # Negative word detection
    # --------------------------------------------------

    def detect_negative_words(self, text):
        """
        Detect negative sentiment words.
        """

        tokens = self.tokenize(text)

        detected_words = []

        for word in tokens:

            if word in self.NEGATIVE_WORDS:
                detected_words.append(word)

        return detected_words

    # --------------------------------------------------
    # Sentiment score
    # --------------------------------------------------

    def calculate_sentiment_score(
        self,
        positive_count,
        negative_count
    ):
        """
        Calculate sentiment score between 0 and 100.

        100 = strongly positive
        50  = neutral
        0   = strongly negative
        """

        total_signals = (
            positive_count
            + negative_count
        )

        # No sentiment signals
        if total_signals == 0:
            return 50.0

        score = 50 + (
            (
                positive_count
                - negative_count
            )
            / total_signals
        ) * 50

        return round(
            score,
            2
        )

    # --------------------------------------------------
    # Sentiment classification
    # --------------------------------------------------

    def classify_sentiment(self, score):
        """
        Classify sentiment based on score.
        """

        if score > 50:
            return "positive"

        elif score < 50:
            return "negative"

        return "neutral"

    # --------------------------------------------------
    # Complete sentiment scoring
    # --------------------------------------------------

    def score_response(self, text):
        """
        Detect sentiment words and calculate
        the sentiment score.
        """

        positive_words = (
            self.detect_positive_words(text)
        )

        negative_words = (
            self.detect_negative_words(text)
        )

        positive_count = len(
            positive_words
        )

        negative_count = len(
            negative_words
        )

        sentiment_score = (
            self.calculate_sentiment_score(
                positive_count,
                negative_count
            )
        )

        sentiment = (
            self.classify_sentiment(
                sentiment_score
            )
        )

        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_words": positive_words,
            "negative_words": negative_words
        }

    # --------------------------------------------------
    # Complete response analysis
    # --------------------------------------------------

    def analyze_response(
        self,
        candidate_id,
        question_id,
        answer
    ):
        """
        Create a complete sentiment analysis object.
        """

        normalized_answer = (
            self.normalize_text(answer)
        )

        sentiment_result = (
            self.score_response(
                normalized_answer
            )
        )

        result = {

            "candidate_id": candidate_id,

            "question_id": question_id,

            "raw_answer": answer,

            "normalized_answer": normalized_answer,

            "sentiment_analysis": sentiment_result,

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
        Save sentiment analysis as JSON
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

    scorer = SentimentScorer()

    candidate_answer = (
        "I really enjoy backend development. "
        "I successfully completed several projects "
        "and I am confident working with Python."
    )

    result = scorer.analyze_response(
        candidate_id="candidate_006",
        question_id="BACKEND_SKILLS_001",
        answer=candidate_answer
    )

    print("=" * 70)
    print("ZecPath - Day 27")
    print("SENTIMENT SCORING")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    filename = (
        "candidate_006_sentiment_analysis.json"
    )

    saved_path = scorer.save_result(
        result,
        filename
    )

    print("\nSentiment analysis saved to:")
    print(saved_path)

    print("=" * 70)