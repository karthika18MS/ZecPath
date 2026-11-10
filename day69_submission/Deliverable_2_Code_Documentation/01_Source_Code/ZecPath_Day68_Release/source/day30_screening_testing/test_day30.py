import json
import os
import unittest

from simulated_screening_calls import SimulatedScreeningCalls
from intent_optimizer import ImprovedIntentClassifier
from scoring_optimizer import ImprovedScoringModel
from conversation_optimizer import OptimizedConversationFlow


class TestDay30Simulation(unittest.TestCase):

    def test_simulation_cases_exist(self):
        simulator = SimulatedScreeningCalls()

        test_cases = simulator.get_test_cases()

        self.assertEqual(len(test_cases), 10)


class TestDay30IntentOptimization(unittest.TestCase):

    def setUp(self):
        self.classifier = ImprovedIntentClassifier()

    def test_confused_response(self):
        result = self.classifier.classify_response(
            "I'm confused. What do you mean?",
            "experience"
        )

        self.assertEqual(result["response_type"], "confused")

    def test_off_topic_education(self):
        result = self.classifier.classify_response(
            "I completed my MCA in Computer Applications.",
            "experience"
        )

        self.assertEqual(result["response_type"], "off_topic")
        self.assertEqual(result["intent"], "education")

    def test_off_topic_location(self):
        result = self.classifier.classify_response(
            "I live in Kerala.",
            "skills"
        )

        self.assertEqual(result["response_type"], "off_topic")
        self.assertEqual(result["intent"], "location")

    def test_valid_experience(self):
        result = self.classifier.classify_response(
            "I have three years of backend development experience.",
            "experience"
        )

        self.assertEqual(result["response_type"], "valid")


class TestDay30ScoringOptimization(unittest.TestCase):

    def setUp(self):
        self.scorer = ImprovedScoringModel()

    def test_strong_response(self):
        result = self.scorer.calculate_response_score(
            "valid",
            "experience",
            9,
            10,
            10,
            9
        )

        self.assertEqual(result["score"], 95.0)

    def test_vague_response(self):
        result = self.scorer.calculate_response_score(
            "vague",
            "experience",
            4,
            4,
            3,
            5
        )

        self.assertEqual(result["score"], 40.0)

    def test_confused_response(self):
        result = self.scorer.calculate_response_score(
            "confused",
            "experience",
            4,
            5,
            4,
            6
        )

        self.assertEqual(result["score"], 47.5)

    def test_off_topic_response(self):
        result = self.scorer.calculate_response_score(
            "off_topic",
            "skills",
            8,
            1,
            2,
            7
        )

        self.assertEqual(result["score"], 45.0)

    def test_no_response(self):
        result = self.scorer.calculate_response_score(
            "no_response",
            "skills",
            0,
            0,
            0,
            0
        )

        self.assertEqual(result["score"], 0.0)


class TestDay30ConversationOptimization(unittest.TestCase):

    def setUp(self):
        self.flow = OptimizedConversationFlow()

    def test_confusion_clarification(self):
        result = self.flow.decide_action(
            answer="I'm confused. What do you mean?",
            question="How many years of backend development experience do you have?",
            question_category="experience"
        )

        self.assertEqual(result["action"], "clarification")

    def test_off_topic_redirect(self):
        result = self.flow.decide_action(
            answer="I completed my MCA in Computer Applications.",
            question="How many years of backend development experience do you have?",
            question_category="experience"
        )

        self.assertEqual(result["action"], "redirect")

    def test_vague_follow_up(self):
        result = self.flow.decide_action(
            answer="I have some experience.",
            question="How many years of backend development experience do you have?",
            question_category="experience"
        )

        self.assertEqual(result["action"], "follow_up")

    def test_silence_retry(self):
        result = self.flow.decide_action(
            answer="",
            question="What technical skills do you have?",
            question_category="skills"
        )

        self.assertEqual(result["action"], "retry")

    def test_valid_next_question(self):
        result = self.flow.decide_action(
            answer="I have three years of backend development experience.",
            question="How many years of backend development experience do you have?",
            question_category="experience"
        )

        self.assertEqual(result["action"], "next_question")

    def test_retry_limit(self):
        result = self.flow.decide_action(
            answer="",
            question="What technical skills do you have?",
            question_category="skills",
            retry_count=2
        )

        self.assertEqual(result["action"], "screening_failed")

    def test_follow_up_limit(self):
        result = self.flow.decide_action(
            answer="I have some experience.",
            question="How many years of backend development experience do you have?",
            question_category="experience",
            follow_up_count=2
        )

        self.assertEqual(result["action"], "next_question")


class TestDay30Results(unittest.TestCase):

    def test_conversation_result_file_exists(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "results",
            "conversation_optimization_results.json"
        )

        self.assertTrue(os.path.exists(path))

    def test_conversation_result_is_optimized(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "results",
            "conversation_optimization_results.json"
        )

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.assertEqual(data["matched_cases"], 6)
        self.assertEqual(data["mismatched_cases"], 0)
        self.assertEqual(data["agreement_percentage"], 100.0)

    def test_intent_result_file_exists(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "results",
            "intent_optimization_results.json"
        )

        self.assertTrue(os.path.exists(path))

    def test_scoring_result_file_exists(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "results",
            "scoring_optimization_results.json"
        )

        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":

    print("=" * 60)
    print("DAY 30 — SCREENING SYSTEM TESTING & OPTIMIZATION")
    print("=" * 60)

    print("\nTest Areas:")
    print("1. Screening simulation")
    print("2. Intent optimization")
    print("3. Scoring optimization")
    print("4. Conversation optimization")
    print("5. Result validation")

    print("\nRunning tests...\n")

    unittest.main(verbosity=2)