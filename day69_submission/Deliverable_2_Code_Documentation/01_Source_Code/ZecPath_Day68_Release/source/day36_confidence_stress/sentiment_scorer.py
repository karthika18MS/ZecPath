import json
import os
import re


class SentimentScorer:

    # Positive words commonly found in interview responses
    POSITIVE_WORDS = {
        "achieved",
        "achievement",
        "adaptable",
        "confident",
        "completed",
        "enjoy",
        "enjoyed",
        "excellent",
        "excited",
        "good",
        "great",
        "improved",
        "improvement",
        "motivated",
        "positive",
        "proud",
        "success",
        "successful",
        "successfully",
        "strong",
        "teamwork",
        "helpful",
        "learned",
        "growth",
        "comfortable",
        "effective"
    }

    # Negative words commonly found in responses
    NEGATIVE_WORDS = {
        "bad",
        "difficult",
        "difficulty",
        "failed",
        "failure",
        "frustrated",
        "frustration",
        "hate",
        "hated",
        "negative",
        "problem",
        "problems",
        "sad",
        "stress",
        "stressed",
        "struggle",
        "struggled",
        "weak",
        "worried",
        "worry",
        "confused",
        "confusion",
        "unable",
        "issue",
        "issues"
    }

    def normalize_text(self, text):
        """
        Convert text to lowercase and normalize spaces.
        """

        if not text:
            return ""

        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)

        return text

    def get_words(self, text):
        """
        Extract words from the response.
        """

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return []

        return re.findall(r"\b[\w']+\b", normalized_text)

    def detect_positive_signals(self, text):
        """
        Detect positive sentiment words.
        """

        words = self.get_words(text)

        positive_words = [
            word for word in words
            if word in self.POSITIVE_WORDS
        ]

        return positive_words

    def detect_negative_signals(self, text):
        """
        Detect negative sentiment words.
        """

        words = self.get_words(text)

        negative_words = [
            word for word in words
            if word in self.NEGATIVE_WORDS
        ]

        return negative_words

    def calculate_sentiment_score(
        self,
        positive_count,
        negative_count
    ):
        """
        Calculate sentiment score from 0 to 100.

        50 = neutral baseline.
        Positive signals increase the score.
        Negative signals decrease the score.
        """

        total_signals = positive_count + negative_count

        if total_signals == 0:
            return 50.0

        score = (
            50
            + (
                (positive_count - negative_count)
                / total_signals
            ) * 50
        )

        return round(
            max(0, min(100, score)),
            2
        )

    def classify_sentiment(self, score):
        """
        Classify sentiment based on score.
        """

        if score > 50:
            return "positive"

        if score < 50:
            return "negative"

        return "neutral"

    def analyze_response(
        self,
        candidate_id,
        question_id,
        response
    ):
        """
        Perform complete sentiment analysis.
        """

        positive_signals = self.detect_positive_signals(
            response
        )

        negative_signals = self.detect_negative_signals(
            response
        )

        positive_count = len(positive_signals)
        negative_count = len(negative_signals)

        sentiment_score = self.calculate_sentiment_score(
            positive_count,
            negative_count
        )

        sentiment = self.classify_sentiment(
            sentiment_score
        )

        return {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "response": response,
            "positive_signals": positive_signals,
            "positive_signal_count": positive_count,
            "negative_signals": negative_signals,
            "negative_signal_count": negative_count,
            "sentiment_score": sentiment_score,
            "sentiment": sentiment,
            "score_range": "0-100"
        }

    def save_result(self, result):
        """
        Save sentiment analysis result.
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
            "sentiment_analysis_results.json"
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

    scorer = SentimentScorer()

    sample_response = (
        "I really enjoyed working with my team. "
        "I successfully completed the project and "
        "learned many new technologies. "
        "The experience was excellent and helped "
        "me improve my skills."
    )

    result = scorer.analyze_response(
        candidate_id="candidate_006",
        question_id="HR_TEAM_001",
        response=sample_response
    )

    output_file = scorer.save_result(result)

    print("DAY 36 — SENTIMENT SCORING ENGINE")
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
        f"Positive Signals: "
        f"{result['positive_signals']}"
    )

    print(
        f"Positive Signal Count: "
        f"{result['positive_signal_count']}"
    )

    print(
        f"Negative Signals: "
        f"{result['negative_signals']}"
    )

    print(
        f"Negative Signal Count: "
        f"{result['negative_signal_count']}"
    )

    print(
        f"Sentiment Score: "
        f"{result['sentiment_score']}/100"
    )

    print(
        f"Sentiment: "
        f"{result['sentiment']}"
    )

    print(
        f"Saved Result: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()