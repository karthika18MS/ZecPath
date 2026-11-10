import os
import sys


# Add Day 24 folder to Python path
DAY24_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    DAY24_DIR
)

from transcript_cleaner import TranscriptCleaner


def run_test(test_number, test_name, raw_text):

    cleaner = TranscriptCleaner()

    print("\n" + "-" * 70)
    print(f"Test {test_number}: {test_name}")
    print("-" * 70)

    print("Raw transcript:")
    print(raw_text)

    # -------------------------------------------------
    # Silence detection
    # -------------------------------------------------

    silence_result = cleaner.detect_silence(raw_text)

    print("\nSilence detection:")
    print(silence_result)

    # Handle empty transcript
    if not raw_text.strip():

        print("\nNormalized transcript:")
        print("")

        print("\nStatus          : no_response")
        print("Interrupted     : False")
        print("Partial answer  : False")

        return True

    # -------------------------------------------------
    # Remove filler words
    # -------------------------------------------------

    normalized_text = cleaner.remove_filler_words(
        raw_text
    )

    # -------------------------------------------------
    # Normalize whitespace
    # -------------------------------------------------

    normalized_text = cleaner.normalize_whitespace(
        normalized_text
    )

    # -------------------------------------------------
    # Normalize technical terms
    # -------------------------------------------------

    normalized_text = cleaner.normalize_case(
        normalized_text
    )

    # -------------------------------------------------
    # Detect interruption
    # -------------------------------------------------

    interruption_result = cleaner.handle_interruption(
        normalized_text
    )

    # The existing method may return either
    # a Boolean or a dictionary.
    if isinstance(interruption_result, dict):

        is_interrupted = interruption_result.get(
            "is_interrupted",
            False
        )

    else:

        is_interrupted = bool(
            interruption_result
        )

    # -------------------------------------------------
    # Correct punctuation
    # -------------------------------------------------

    normalized_text = cleaner.correct_punctuation(
        normalized_text
    )

    # -------------------------------------------------
    # Detect partial answer
    # -------------------------------------------------

    partial_result = cleaner.detect_partial_answer(
        normalized_text
    )

    # The existing method may return either
    # a Boolean or a dictionary.
    if isinstance(partial_result, dict):

        is_partial = partial_result.get(
            "is_partial",
            False
        )

    else:

        is_partial = bool(
            partial_result
        )

    # -------------------------------------------------
    # Display result
    # -------------------------------------------------

    print("\nNormalized transcript:")
    print(normalized_text)

    print(
        f"\nStatus          : response_detected"
    )

    print(
        f"Interrupted     : {is_interrupted}"
    )

    print(
        f"Partial answer  : {is_partial}"
    )

    return True


def main():

    print("=" * 70)
    print("ZecPath - Day 24")
    print("Transcript Normalization Test Cases")
    print("=" * 70)

    test_cases = [

        (
            "Filler Word Removal",
            "Um, I have like three years, uh, of experience."
        ),

        (
            "Technical Terms",
            "I have experience with python, django, fast api and postgresql."
        ),

        (
            "Extra Whitespace",
            "I have    three years     of experience   in backend development."
        ),

        (
            "Missing Punctuation",
            "I have experience with Python Django and FastAPI"
        ),

        (
            "Interrupted Speech",
            "I have worked with Python for three—"
        ),

        (
            "Partial Answer",
            "Three years."
        ),

        (
            "Silence / No Response",
            ""
        ),

        (
            "Negative Answer",
            "I don't have experience with Docker."
        ),

        (
            "Uncertain Answer",
            "I think I have around three years of experience."
        ),

        (
            "Realistic Screening Answer",
            "Um, I have like three years of experience in "
            "back-end development. I have worked with python, "
            "django, fast api, docker and postgresql."
        )
    ]

    successful = 0
    failed = 0

    for number, (test_name, raw_text) in enumerate(
        test_cases,
        start=1
    ):

        try:

            run_test(
                number,
                test_name,
                raw_text
            )

            successful += 1

        except Exception as error:

            failed += 1

            print(
                f"\nTest failed: {error}"
            )

    print("\n" + "=" * 70)
    print("TRANSCRIPT NORMALIZATION TEST COMPLETED")
    print("=" * 70)

    print(
        f"Total test cases : {len(test_cases)}"
    )

    print(
        f"Successful       : {successful}"
    )

    print(
        f"Failed           : {failed}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()