import sys
import unittest
from pathlib import Path

from error_handling_flow import ErrorHandlingFlow
# ---------------------------------------------------------
# Import Day 29 modules
# ---------------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from ai_call_flow import AICallFlow
from conversation_state_machine import ConversationStateMachine


class TestAICallFlow(unittest.TestCase):
    """
    Tests for Deliverable 1:
    AI Call Flow Logic
    """

    def setUp(self):
        self.flow = AICallFlow()

        self.candidate_id = "candidate_006"
        self.job_id = "JOB_BACKEND_001"
        self.question_id = "BACKEND_EXP_001"

        self.question = (
            "How many years of backend development "
            "experience do you have?"
        )

    # -----------------------------------------------------
    # Test 1: Valid response
    # -----------------------------------------------------

    def test_valid_response(self):
        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="valid",
            intent="experience",
            current_answer=(
                "I have three years of backend development experience."
            ),
            previous_answers=[]
        )

        self.assertEqual(
            result["response_type"],
            "valid"
        )

        self.assertEqual(
            result["decision"]["action"],
            "next_question"
        )

        self.assertFalse(
            result["decision"]["requires_follow_up"]
        )

    # -----------------------------------------------------
    # Test 2: Vague response
    # -----------------------------------------------------

    def test_vague_response(self):
        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="vague",
            intent="experience",
            current_answer="I have some experience.",
            previous_answers=[]
        )

        self.assertEqual(
            result["response_type"],
            "vague"
        )

        self.assertEqual(
            result["decision"]["action"],
            "follow_up"
        )

        self.assertTrue(
            result["decision"]["requires_follow_up"]
        )

    # -----------------------------------------------------
    # Test 3: No response / silence
    # -----------------------------------------------------

    def test_no_response(self):
        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="no_response",
            intent="no_response",
            current_answer="",
            previous_answers=[]
        )

        self.assertEqual(
            result["response_type"],
            "no_response"
        )

        self.assertEqual(
            result["decision"]["action"],
            "retry"
        )

        # Retry is different from follow-up.
        # Therefore requires_follow_up should be False.
        self.assertFalse(
            result["decision"]["requires_follow_up"]
        )

    # -----------------------------------------------------
    # Test 4: Confused response
    # -----------------------------------------------------

    def test_confused_response(self):
        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="confused",
            intent="confused",
            current_answer="I don't understand the question.",
            previous_answers=[]
        )

        self.assertEqual(
            result["response_type"],
            "confused"
        )

        self.assertEqual(
            result["decision"]["action"],
            "clarification"
        )

    # -----------------------------------------------------
    # Test 5: Off-topic response
    # -----------------------------------------------------

    def test_off_topic_response(self):
        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="off_topic",
            intent="off_topic",
            current_answer=(
                "I really enjoy working in technology."
            ),
            previous_answers=[]
        )

        self.assertEqual(
            result["response_type"],
            "off_topic"
        )

        self.assertEqual(
            result["decision"]["action"],
            "redirect"
        )

    # -----------------------------------------------------
    # Test 6: Repeated answer
    # -----------------------------------------------------

    def test_repeated_answer(self):
        previous_answer = (
            "I have three years of backend development experience."
        )

        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="valid",
            intent="experience",
            current_answer=previous_answer,
            previous_answers=[previous_answer]
        )

        self.assertEqual(
            result["response_type"],
            "repeated"
        )

        self.assertEqual(
            result["decision"]["action"],
            "follow_up"
        )

    # -----------------------------------------------------
    # Test 7: Follow-up question generation
    # -----------------------------------------------------

    def test_follow_up_question(self):
        follow_up = self.flow.get_follow_up_question(
            question_category="experience",
            response_type="vague"
        )

        self.assertIsInstance(
            follow_up,
            str
        )

        self.assertTrue(
            len(follow_up) > 0
        )

    # -----------------------------------------------------
    # Test 8: Clarification question
    # -----------------------------------------------------

    def test_clarification_question(self):
        clarification = self.flow.get_clarification_question(
            self.question
        )

        self.assertIsInstance(
            clarification,
            str
        )

        self.assertTrue(
            len(clarification) > 0
        )

    # -----------------------------------------------------
    # Test 9: Redirect question
    # -----------------------------------------------------

    def test_redirect_question(self):
        redirect = self.flow.get_redirect_question(
            self.question
        )

        self.assertIsInstance(
            redirect,
            str
        )

        self.assertTrue(
            len(redirect) > 0
        )

    # -----------------------------------------------------
    # Test 10: Result structure
    # -----------------------------------------------------

    def test_result_structure(self):
        result = self.flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="valid",
            intent="experience",
            current_answer=(
                "I have three years of backend development experience."
            ),
            previous_answers=[]
        )

        required_fields = [
            "candidate_id",
            "job_id",
            "question_id",
            "question",
            "question_category",
            "answer_status",
            "intent",
            "response_type",
            "decision",
            "next_prompt"
        ]

        for field in required_fields:
            self.assertIn(
                field,
                result
            )

        self.assertIn(
            "action",
            result["decision"]
        )

        self.assertIn(
            "reason",
            result["decision"]
        )

        self.assertIn(
            "requires_follow_up",
            result["decision"]
        )


class TestConversationStateMachine(unittest.TestCase):
    """
    Tests for Deliverable 2:
    Conversation State Machine
    """

    def setUp(self):
        self.candidate_id = "candidate_006"
        self.job_id = "JOB_BACKEND_001"
        self.question_id = "BACKEND_EXP_001"

        self.question = (
            "How many years of backend development "
            "experience do you have?"
        )

    # -----------------------------------------------------
    # Test 11: Initial state
    # -----------------------------------------------------

    def test_initial_state(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state = state_machine.get_state()

        self.assertEqual(
            state["current_state"],
            "START"
        )

        self.assertEqual(
            state["state_history"],
            ["START"]
        )

        self.assertEqual(
            state["retry_count"],
            0
        )

        self.assertEqual(
            state["follow_up_count"],
            0
        )

    # -----------------------------------------------------
    # Test 12: Start conversation
    # -----------------------------------------------------

    def test_start_conversation(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        result = state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        self.assertEqual(
            result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertEqual(
            result["current_question_id"],
            self.question_id
        )

        self.assertIn(
            "ASKING_QUESTION",
            result["state_history"]
        )

        self.assertIn(
            "WAITING_FOR_RESPONSE",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 13: Valid response transition
    # -----------------------------------------------------

    def test_valid_response_transition(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.process_response(
            response_type="valid",
            question_id=self.question_id,
            question=self.question
        )

        self.assertEqual(
            result["current_state"],
            "NEXT_QUESTION"
        )

        self.assertEqual(
            result["last_response_type"],
            "valid"
        )

    # -----------------------------------------------------
    # Test 14: Vague response transition
    # -----------------------------------------------------

    def test_vague_response_transition(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.process_response(
            response_type="vague",
            question_id=self.question_id,
            question=self.question
        )

        self.assertEqual(
            result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertEqual(
            result["follow_up_count"],
            1
        )

        self.assertIn(
            "FOLLOW_UP",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 15: No response retry
    # -----------------------------------------------------

    def test_no_response_retry(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.process_response(
            response_type="no_response",
            question_id=self.question_id,
            question=self.question
        )

        self.assertEqual(
            result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertEqual(
            result["retry_count"],
            1
        )

        self.assertIn(
            "RETRY",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 16: Retry limit
    # -----------------------------------------------------

    def test_retry_limit(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        # Retry 1
        state_machine.process_response(
            response_type="no_response"
        )

        # Retry 2
        state_machine.process_response(
            response_type="no_response"
        )

        # Retry limit exceeded
        result = state_machine.process_response(
            response_type="no_response"
        )

        self.assertEqual(
            result["retry_count"],
            2
        )

        self.assertEqual(
            result["current_state"],
            "SCREENING_FAILED"
        )

    # -----------------------------------------------------
    # Test 17: Confused response transition
    # -----------------------------------------------------

    def test_confused_response_transition(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.process_response(
            response_type="confused"
        )

        self.assertEqual(
            result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertIn(
            "CLARIFICATION",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 18: Off-topic response transition
    # -----------------------------------------------------

    def test_off_topic_response_transition(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.process_response(
            response_type="off_topic"
        )

        self.assertEqual(
            result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertIn(
            "REDIRECT",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 19: Repeated response transition
    # -----------------------------------------------------

    def test_repeated_response_transition(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.process_response(
            response_type="repeated"
        )

        self.assertEqual(
            result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertEqual(
            result["follow_up_count"],
            1
        )

        self.assertIn(
            "FOLLOW_UP",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 20: Follow-up limit
    # -----------------------------------------------------

    def test_follow_up_limit(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        # Follow-up 1
        state_machine.process_response(
            response_type="vague"
        )

        # Follow-up 2
        state_machine.process_response(
            response_type="vague"
        )

        # Follow-up limit reached
        result = state_machine.process_response(
            response_type="vague"
        )

        self.assertEqual(
            result["follow_up_count"],
            2
        )

        self.assertEqual(
            result["current_state"],
            "NEXT_QUESTION"
        )

    # -----------------------------------------------------
    # Test 21: Screening completion
    # -----------------------------------------------------

    def test_screening_completion(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.complete_screening()

        self.assertEqual(
            result["current_state"],
            "SCREENING_COMPLETED"
        )

        self.assertIn(
            "SCREENING_COMPLETED",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 22: Screening failure
    # -----------------------------------------------------

    def test_screening_failure(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        result = state_machine.fail_screening()

        self.assertEqual(
            result["current_state"],
            "SCREENING_FAILED"
        )

        self.assertIn(
            "SCREENING_FAILED",
            result["state_history"]
        )

    # -----------------------------------------------------
    # Test 23: State history
    # -----------------------------------------------------

    def test_state_history(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        state_machine.process_response(
            response_type="valid"
        )

        result = state_machine.get_state()

        expected_states = [
            "START",
            "ASKING_QUESTION",
            "WAITING_FOR_RESPONSE",
            "PROCESSING_RESPONSE",
            "NEXT_QUESTION"
        ]

        self.assertEqual(
            result["state_history"],
            expected_states
        )

    # -----------------------------------------------------
    # Test 24: Result structure
    # -----------------------------------------------------

    def test_state_result_structure(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        result = state_machine.get_state()

        required_fields = [
            "candidate_id",
            "job_id",
            "current_question_id",
            "current_question",
            "current_state",
            "state_history",
            "retry_count",
            "follow_up_count",
            "last_response_type"
        ]

        for field in required_fields:
            self.assertIn(
                field,
                result
            )

    # -----------------------------------------------------
    # Test 25: Invalid response type
    # -----------------------------------------------------

    def test_invalid_response_type(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        with self.assertRaises(ValueError):
            state_machine.process_response(
                response_type="invalid_response_type"
            )

    # -----------------------------------------------------
    # Test 26: Invalid state transition
    # -----------------------------------------------------

    def test_invalid_state_transition(self):
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        with self.assertRaises(ValueError):
            state_machine.transition(
                "INVALID_STATE"
            )


class TestDay29Integration(unittest.TestCase):
    """
    Integration tests connecting:
    Deliverable 1 -> Deliverable 2
    """

    def setUp(self):
        self.candidate_id = "candidate_006"
        self.job_id = "JOB_BACKEND_001"
        self.question_id = "BACKEND_EXP_001"

        self.question = (
            "How many years of backend development "
            "experience do you have?"
        )

    # -----------------------------------------------------
    # Test 27: Valid flow integration
    # -----------------------------------------------------

    def test_valid_flow_integration(self):
        # Deliverable 1
        flow = AICallFlow()

        flow_result = flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="valid",
            intent="experience",
            current_answer=(
                "I have three years of backend development experience."
            ),
            previous_answers=[]
        )

        action = flow_result["decision"]["action"]

        self.assertEqual(
            action,
            "next_question"
        )

        # Deliverable 2
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        state_result = state_machine.process_response(
            response_type=flow_result["response_type"]
        )

        self.assertEqual(
            state_result["current_state"],
            "NEXT_QUESTION"
        )

    # -----------------------------------------------------
    # Test 28: Vague flow integration
    # -----------------------------------------------------

    def test_vague_flow_integration(self):
        # Deliverable 1
        flow = AICallFlow()

        flow_result = flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="vague",
            intent="experience",
            current_answer="I have some experience.",
            previous_answers=[]
        )

        self.assertEqual(
            flow_result["decision"]["action"],
            "follow_up"
        )

        # Deliverable 2
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        state_result = state_machine.process_response(
            response_type=flow_result["response_type"]
        )

        self.assertEqual(
            state_result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertEqual(
            state_result["follow_up_count"],
            1
        )

    # -----------------------------------------------------
    # Test 29: No-response flow integration
    # -----------------------------------------------------

    def test_no_response_flow_integration(self):
        # Deliverable 1
        flow = AICallFlow()

        flow_result = flow.analyze_response(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            question_id=self.question_id,
            question=self.question,
            question_category="experience",
            answer_status="no_response",
            intent="no_response",
            current_answer="",
            previous_answers=[]
        )

        self.assertEqual(
            flow_result["decision"]["action"],
            "retry"
        )

        # Deliverable 2
        state_machine = ConversationStateMachine(
            candidate_id=self.candidate_id,
            job_id=self.job_id
        )

        state_machine.start_conversation(
            question_id=self.question_id,
            question=self.question
        )

        state_result = state_machine.process_response(
            response_type=flow_result["response_type"]
        )

        self.assertEqual(
            state_result["current_state"],
            "WAITING_FOR_RESPONSE"
        )

        self.assertEqual(
            state_result["retry_count"],
            1
        )
class TestErrorHandlingFlow(unittest.TestCase):
    """Tests for Day 29 Deliverable 3."""

    def setUp(self):
        self.error_handler = ErrorHandlingFlow()

        self.question = (
            "How many years of backend development "
            "experience do you have?"
        )

    def test_no_response_retry(self):
        result = self.error_handler.handle_error(
            error_type="no_response",
            question=self.question,
            retry_count=0
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

        self.assertFalse(
            result["screening_failed"]
        )

        self.assertEqual(
            result["retry_count"],
            1
        )

    def test_no_response_second_retry(self):
        result = self.error_handler.handle_error(
            error_type="no_response",
            question=self.question,
            retry_count=1
        )

        self.assertEqual(
            result["action"],
            "retry"
        )

        self.assertEqual(
            result["retry_count"],
            2
        )

    def test_no_response_failure(self):
        result = self.error_handler.handle_error(
            error_type="no_response",
            question=self.question,
            retry_count=2
        )

        self.assertEqual(
            result["action"],
            "screening_failed"
        )

        self.assertTrue(
            result["screening_failed"]
        )

        self.assertIn(
            "Thank you",
            result["message"]
        )

    def test_confusion_handling(self):
        result = self.error_handler.handle_error(
            error_type="confused",
            question=self.question
        )

        self.assertEqual(
            result["action"],
            "clarification"
        )

        self.assertFalse(
            result["screening_failed"]
        )

        self.assertIn(
            "another way",
            result["message"]
        )

    def test_vague_response_follow_up(self):
        result = self.error_handler.handle_error(
            error_type="vague",
            question_category="experience",
            follow_up_count=0
        )

        self.assertEqual(
            result["action"],
            "follow_up"
        )

        self.assertTrue(
            result["requires_follow_up"]
        )

        self.assertEqual(
            result["follow_up_count"],
            1
        )

    def test_vague_response_follow_up_limit(self):
        result = self.error_handler.handle_error(
            error_type="vague",
            question_category="experience",
            follow_up_count=2
        )

        self.assertEqual(
            result["action"],
            "next_question"
        )

        self.assertFalse(
            result["requires_follow_up"]
        )

    def test_off_topic_handling(self):
        result = self.error_handler.handle_error(
            error_type="off_topic",
            question=self.question
        )

        self.assertEqual(
            result["action"],
            "redirect"
        )

        self.assertFalse(
            result["screening_failed"]
        )

        self.assertIn(
            "Coming back",
            result["message"]
        )

    def test_repeated_answer_follow_up(self):
        result = self.error_handler.handle_error(
            error_type="repeated",
            question_category="experience",
            follow_up_count=0
        )

        self.assertEqual(
            result["action"],
            "follow_up"
        )

        self.assertTrue(
            result["requires_follow_up"]
        )

        self.assertEqual(
            result["follow_up_count"],
            1
        )

    def test_repeated_answer_limit(self):
        result = self.error_handler.handle_error(
            error_type="repeated",
            question_category="experience",
            follow_up_count=2
        )

        self.assertEqual(
            result["action"],
            "next_question"
        )

        self.assertFalse(
            result["requires_follow_up"]
        )

    def test_complete_error_result_structure(self):
        result = self.error_handler.analyze_response(
            candidate_id="candidate_006",
            job_id="JOB_BACKEND_001",
            question_id="BACKEND_EXP_001",
            question=self.question,
            question_category="experience",
            error_type="no_response",
            retry_count=0
        )

        self.assertIn(
            "candidate_id",
            result
        )

        self.assertIn(
            "job_id",
            result
        )

        self.assertIn(
            "question_id",
            result
        )

        self.assertIn(
            "error_handling",
            result
        )

        self.assertIn(
            "created_at",
            result
        )

    def test_invalid_error_type(self):
        with self.assertRaises(ValueError):
            self.error_handler.handle_error(
                error_type="invalid_error"
            )

# ---------------------------------------------------------
# Run Tests
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("DAY 29 - COMBINED TEST SUITE")
    print("=" * 60)

    print("Testing:")
    print("1. AI Call Flow Logic")
    print("2. Conversation State Machine")
    print("3. Deliverable 1 -> Deliverable 2 Integration")

    print("=" * 60 + "\n")

    unittest.main(verbosity=2)