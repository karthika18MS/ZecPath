import json
from datetime import datetime, timezone
from pathlib import Path


class ConversationStateMachine:
    """
    Manages the state and transitions of an AI candidate screening conversation.
    """

    STATES = {
        "START",
        "ASKING_QUESTION",
        "WAITING_FOR_RESPONSE",
        "PROCESSING_RESPONSE",
        "FOLLOW_UP",
        "CLARIFICATION",
        "RETRY",
        "REDIRECT",
        "NEXT_QUESTION",
        "SCREENING_COMPLETED",
        "SCREENING_FAILED"
    }

    RESPONSE_TYPES = {
        "valid",
        "vague",
        "no_response",
        "confused",
        "off_topic",
        "repeated"
    }

    def __init__(self, candidate_id, job_id):
        self.candidate_id = candidate_id
        self.job_id = job_id

        self.current_state = "START"
        self.state_history = ["START"]

        self.retry_count = 0
        self.follow_up_count = 0

        self.current_question_id = None
        self.current_question = None

        self.last_response_type = None

    # ---------------------------------------------------------
    # State Transition
    # ---------------------------------------------------------

    def transition(self, new_state):
        """
        Move the conversation from the current state to a new state.
        """

        if new_state not in self.STATES:
            raise ValueError(f"Invalid conversation state: {new_state}")

        self.current_state = new_state
        self.state_history.append(new_state)

        return self.current_state

    # ---------------------------------------------------------
    # Start Conversation
    # ---------------------------------------------------------

    def start_conversation(self, question_id, question):
        """
        Start the screening conversation with the first question.
        """

        self.current_question_id = question_id
        self.current_question = question

        self.transition("ASKING_QUESTION")
        self.transition("WAITING_FOR_RESPONSE")

        return self.get_state()

    # ---------------------------------------------------------
    # Response Processing
    # ---------------------------------------------------------

    def process_response(
        self,
        response_type,
        question_id=None,
        question=None,
        max_retries=2,
        max_follow_ups=2
    ):
        """
        Process a candidate response and transition
        to the appropriate conversation state.
        """

        if response_type not in self.RESPONSE_TYPES:
            raise ValueError(
                f"Invalid response type: {response_type}"
            )

        if question_id:
            self.current_question_id = question_id

        if question:
            self.current_question = question

        self.last_response_type = response_type

        self.transition("PROCESSING_RESPONSE")

        # -----------------------------------------------------
        # Valid response
        # -----------------------------------------------------

        if response_type == "valid":
            self.retry_count = 0
            self.follow_up_count = 0
            self.transition("NEXT_QUESTION")

        # -----------------------------------------------------
        # Vague response
        # -----------------------------------------------------

        elif response_type == "vague":

            if self.follow_up_count < max_follow_ups:
                self.follow_up_count += 1
                self.transition("FOLLOW_UP")
                self.transition("WAITING_FOR_RESPONSE")
            else:
                self.transition("NEXT_QUESTION")

        # -----------------------------------------------------
        # No response / silence
        # -----------------------------------------------------

        elif response_type == "no_response":

            if self.retry_count < max_retries:
                self.retry_count += 1
                self.transition("RETRY")
                self.transition("WAITING_FOR_RESPONSE")
            else:
                self.transition("SCREENING_FAILED")

        # -----------------------------------------------------
        # Confused response
        # -----------------------------------------------------

        elif response_type == "confused":
            self.transition("CLARIFICATION")
            self.transition("WAITING_FOR_RESPONSE")

        # -----------------------------------------------------
        # Off-topic response
        # -----------------------------------------------------

        elif response_type == "off_topic":
            self.transition("REDIRECT")
            self.transition("WAITING_FOR_RESPONSE")

        # -----------------------------------------------------
        # Repeated response
        # -----------------------------------------------------

        elif response_type == "repeated":

            if self.follow_up_count < max_follow_ups:
                self.follow_up_count += 1
                self.transition("FOLLOW_UP")
                self.transition("WAITING_FOR_RESPONSE")
            else:
                self.transition("NEXT_QUESTION")

        return self.get_state()

    # ---------------------------------------------------------
    # Complete Screening
    # ---------------------------------------------------------

    def complete_screening(self):
        """
        Mark the screening as successfully completed.
        """

        self.transition("SCREENING_COMPLETED")

        return self.get_state()

    # ---------------------------------------------------------
    # Fail Screening
    # ---------------------------------------------------------

    def fail_screening(self):
        """
        Mark the screening as failed.
        """

        self.transition("SCREENING_FAILED")

        return self.get_state()

    # ---------------------------------------------------------
    # Get Current State
    # ---------------------------------------------------------

    def get_state(self):
        """
        Return the current conversation state.
        """

        return {
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "current_question_id": self.current_question_id,
            "current_question": self.current_question,
            "current_state": self.current_state,
            "state_history": self.state_history,
            "retry_count": self.retry_count,
            "follow_up_count": self.follow_up_count,
            "last_response_type": self.last_response_type
        }

    # ---------------------------------------------------------
    # Save Result
    # ---------------------------------------------------------

    def save_result(
        self,
        result,
        filename="conversation_state_machine_results.json"
    ):
        """
        Save state-machine result to the results folder.
        """

        results_dir = Path(__file__).resolve().parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        result["created_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        output_path = results_dir / filename

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4
            )

        return output_path


# -------------------------------------------------------------
# Example Execution
# -------------------------------------------------------------

if __name__ == "__main__":

    candidate_id = "candidate_006"
    job_id = "JOB_BACKEND_001"

    question_id = "BACKEND_EXP_001"

    question = (
        "How many years of backend development "
        "experience do you have?"
    )

    # Create state machine
    state_machine = ConversationStateMachine(
        candidate_id=candidate_id,
        job_id=job_id
    )

    # Start conversation
    state_machine.start_conversation(
        question_id=question_id,
        question=question
    )

    # Candidate provides a valid answer
    result = state_machine.process_response(
        response_type="valid",
        question_id=question_id,
        question=question
    )

    # Save result
    output_path = state_machine.save_result(result)

    print("\nConversation State Machine Result:")
    print(json.dumps(result, indent=4))

    print(
        f"\nResult saved to: {output_path}"
    )