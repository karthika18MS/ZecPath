import json
import os
import re


class CommunicationScorer:
    """
    Day 35 — Communication Skill Evaluation

    Evaluates candidate communication based on:
    - Fluency
    - Grammar quality
    - Vocabulary range
    - Clarity of explanation
    - Filler words
    - Answer structure

    Final communication score: 0–100
    """

    FILLER_WORDS = {
        "um",
        "uh",
        "hmm",
        "erm",
        "er",
        "ah",
        "like",
        "actually",
        "basically",
        "you know"
    }

    COMMON_VERBS = {
        "is", "am", "are", "was", "were",
        "have", "has", "had",
        "do", "did",
        "work", "worked",
        "use", "used",
        "make", "made",
        "get", "got",
        "go", "went"
    }

    TRANSITION_WORDS = {
        "first",
        "then",
        "next",
        "finally",
        "because",
        "therefore",
        "however",
        "also",
        "during",
        "after",
        "before"
    }

    def __init__(self):
        self.weights = {
            "fluency": 0.25,
            "grammar": 0.20,
            "vocabulary": 0.15,
            "clarity": 0.25,
            "structure": 0.15
        }

    # --------------------------------------------------
    # Text preprocessing
    # --------------------------------------------------

    def normalize_text(self, text):
        """
        Normalize candidate response text.
        """

        if not text:
            return ""

        text = str(text).strip()

        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text)

        return text

    def get_words(self, text):
        """
        Extract words from the response.
        """

        text = self.normalize_text(text)

        return re.findall(r"\b[a-zA-Z]+\b", text.lower())

    # --------------------------------------------------
    # Filler word detection
    # --------------------------------------------------

    def detect_filler_words(self, text):
        """
        Detect common filler words.
        """

        words = self.get_words(text)

        fillers = [
            word for word in words
            if word in self.FILLER_WORDS
        ]

        return {
            "filler_word_count": len(fillers),
            "filler_words": fillers
        }

    # --------------------------------------------------
    # Fluency
    # --------------------------------------------------

    def calculate_fluency(self, text):
        """
        Estimate fluency using sentence continuity,
        response length and filler frequency.
        """

        words = self.get_words(text)

        if not words:
            return 0.0

        word_count = len(words)

        filler_data = self.detect_filler_words(text)
        filler_count = filler_data["filler_word_count"]

        # Start with a reasonable baseline
        score = 70.0

        # Longer meaningful responses indicate continuity
        if word_count >= 20:
            score += 20
        elif word_count >= 10:
            score += 15
        elif word_count >= 5:
            score += 10
        else:
            score -= 15

        # Penalize excessive fillers
        score -= filler_count * 5

        return round(max(0, min(100, score)), 2)

    # --------------------------------------------------
    # Grammar quality
    # --------------------------------------------------

    def calculate_grammar(self, text):
        """
        Estimate basic grammar quality using
        sentence structure and common grammatical patterns.
        """

        words = self.get_words(text)

        if not words:
            return 0.0

        score = 70.0

        # Basic subject/verb indicators
        has_common_verb = any(
            word in self.COMMON_VERBS
            for word in words
        )

        if has_common_verb:
            score += 15

        # Sentence-ending punctuation
        normalized = self.normalize_text(text)

        if normalized.endswith((".", "!", "?")):
            score += 10

        # Extremely short responses provide less
        # evidence of grammatical ability
        if len(words) <= 2:
            score -= 20

        return round(max(0, min(100, score)), 2)

    # --------------------------------------------------
    # Vocabulary range
    # --------------------------------------------------

    def calculate_vocabulary(self, text):
        """
        Estimate vocabulary range using
        unique-word ratio and response length.
        """

        words = self.get_words(text)

        if not words:
            return 0.0

        unique_words = set(words)

        vocabulary_ratio = len(unique_words) / len(words)

        # Base score
        score = 50.0

        if vocabulary_ratio >= 0.80:
            score += 30
        elif vocabulary_ratio >= 0.65:
            score += 20
        elif vocabulary_ratio >= 0.50:
            score += 10

        # Longer answers provide more vocabulary evidence
        if len(words) >= 20:
            score += 15
        elif len(words) >= 10:
            score += 10

        return round(max(0, min(100, score)), 2)

    # --------------------------------------------------
    # Clarity
    # --------------------------------------------------

    def calculate_clarity(self, text):
        """
        Estimate clarity based on response length,
        fillers and sentence structure.
        """

        words = self.get_words(text)

        if not words:
            return 0.0

        score = 70.0

        filler_count = self.detect_filler_words(
            text
        )["filler_word_count"]

        # Reasonable length improves explanation clarity
        if 8 <= len(words) <= 60:
            score += 20
        elif len(words) > 60:
            score += 5
        else:
            score -= 10

        # Excessive fillers reduce clarity
        score -= filler_count * 5

        return round(max(0, min(100, score)), 2)

    # --------------------------------------------------
    # Answer structure
    # --------------------------------------------------

    def calculate_structure(self, text):
        """
        Estimate answer structure using transition words
        and sentence organization.
        """

        words = self.get_words(text)

        if not words:
            return 0.0

        score = 60.0

        transition_count = sum(
            1 for word in words
            if word in self.TRANSITION_WORDS
        )

        # Transition words indicate organization
        if transition_count >= 3:
            score += 30
        elif transition_count >= 2:
            score += 20
        elif transition_count >= 1:
            score += 10

        # Longer responses give more opportunity
        # to demonstrate structure
        if len(words) >= 15:
            score += 10

        return round(max(0, min(100, score)), 2)

    # --------------------------------------------------
    # Final communication score
    # --------------------------------------------------

    def calculate_final_score(
        self,
        fluency,
        grammar,
        vocabulary,
        clarity,
        structure
    ):
        """
        Calculate weighted communication score.
        """

        score = (
            fluency * self.weights["fluency"]
            + grammar * self.weights["grammar"]
            + vocabulary * self.weights["vocabulary"]
            + clarity * self.weights["clarity"]
            + structure * self.weights["structure"]
        )

        return round(max(0, min(100, score)), 2)

    # --------------------------------------------------
    # Complete analysis
    # --------------------------------------------------

    def analyze_response(
        self,
        candidate_id,
        question_id,
        response
    ):
        """
        Perform complete communication analysis.
        """

        text = self.normalize_text(response)

        words = self.get_words(text)

        filler_data = self.detect_filler_words(text)

        fluency = self.calculate_fluency(text)
        grammar = self.calculate_grammar(text)
        vocabulary = self.calculate_vocabulary(text)
        clarity = self.calculate_clarity(text)
        structure = self.calculate_structure(text)

        final_score = self.calculate_final_score(
            fluency,
            grammar,
            vocabulary,
            clarity,
            structure
        )

        result = {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "response": text,
            "word_count": len(words),
            "fluency_score": fluency,
            "grammar_score": grammar,
            "vocabulary_score": vocabulary,
            "clarity_score": clarity,
            "structure_score": structure,
            "filler_word_count": filler_data[
                "filler_word_count"
            ],
            "filler_words": filler_data[
                "filler_words"
            ],
            "communication_score": final_score,
            "score_range": "0-100"
        }

        return result

    # --------------------------------------------------
    # Save result
    # --------------------------------------------------

    def save_result(
        self,
        result,
        filename="communication_score_results.json"
    ):
        """
        Save communication analysis result.
        """

        results_dir = os.path.join(
            os.path.dirname(__file__),
            "results"
        )

        os.makedirs(results_dir, exist_ok=True)

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
                indent=4
            )

        return file_path


if __name__ == "__main__":

    scorer = CommunicationScorer()

    sample_response = (
        "During my final-year project, I worked "
        "with three team members. First, I handled "
        "the backend development using Python and "
        "Django. Then, I coordinated with the "
        "frontend team to integrate the APIs. "
        "Finally, we successfully completed the "
        "project together."
    )

    result = scorer.analyze_response(
        candidate_id="candidate_006",
        question_id="HR_TEAM_001",
        response=sample_response
    )

    file_path = scorer.save_result(result)

    print("DAY 35 — COMMUNICATION SCORING MODEL")
    print("=" * 45)
    print(f"Candidate: {result['candidate_id']}")
    print(f"Question ID: {result['question_id']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Fluency Score: {result['fluency_score']}")
    print(f"Grammar Score: {result['grammar_score']}")
    print(
        f"Vocabulary Score: "
        f"{result['vocabulary_score']}"
    )
    print(f"Clarity Score: {result['clarity_score']}")
    print(
        f"Structure Score: "
        f"{result['structure_score']}"
    )
    print(
        f"Filler Word Count: "
        f"{result['filler_word_count']}"
    )
    print(
        f"Communication Score: "
        f"{result['communication_score']}/100"
    )
    print(f"Saved Result: {file_path}")