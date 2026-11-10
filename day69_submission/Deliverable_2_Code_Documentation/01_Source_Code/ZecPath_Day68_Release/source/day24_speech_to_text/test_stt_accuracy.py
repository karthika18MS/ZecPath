import json
import os
import re
from difflib import SequenceMatcher

import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from stt_processor import SpeechToTextProcessor


BASE_DIR = os.path.dirname(__file__)

AUDIO_DIR = os.path.join(
    BASE_DIR,
    "audio"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "stt_accuracy_results.json"
)


REFERENCE_TEXT = (
    "I have three years of experience in backend development. "
    "I have worked with Python, Django, FastAPI, Docker and PostgreSQL."
)


TEST_FILES = [
    ("indian", "clean", "indian_clean.wav"),
    ("indian", "low_noise", "indian_low_noise.wav"),
    ("indian", "medium_noise", "indian_medium_noise.wav"),
    ("indian", "high_noise", "indian_high_noise.wav"),

    ("american", "clean", "american_clean.wav"),
    ("american", "low_noise", "american_low_noise.wav"),
    ("american", "medium_noise", "american_medium_noise.wav"),
    ("american", "high_noise", "american_high_noise.wav"),

    ("british", "clean", "british_clean.wav"),
    ("british", "low_noise", "british_low_noise.wav"),
    ("british", "medium_noise", "british_medium_noise.wav"),
    ("british", "high_noise", "british_high_noise.wav")
]


def normalize_text(text):
    """
    Normalize text before comparison.
    """

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def calculate_word_accuracy(reference, predicted):
    """
    Calculate simple word-level accuracy.

    The score is based on the similarity between
    the reference and predicted word sequences.
    """

    reference_words = normalize_text(reference).split()
    predicted_words = normalize_text(predicted).split()

    if not reference_words:
        return 0.0

    matcher = SequenceMatcher(
        None,
        reference_words,
        predicted_words
    )

    matching_words = sum(
        block.size
        for block in matcher.get_matching_blocks()
    )

    accuracy = (
        matching_words / len(reference_words)
    ) * 100

    return round(accuracy, 2)


def main():

    print("=" * 70)
    print("ZecPath - Day 24")
    print("STT Accuracy Test")
    print("=" * 70)

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    print("\nReference transcript:")
    print(REFERENCE_TEXT)

    print("\nLoading Speech-to-Text model...")
    print("Please wait...")

    processor = SpeechToTextProcessor(
        model_size="base"
    )

    print("\nModel loaded successfully.")
    print("=" * 70)

    results = []

    for accent, noise_level, filename in TEST_FILES:

        audio_path = os.path.join(
            AUDIO_DIR,
            filename
        )

        print("\n")
        print("-" * 70)
        print(f"Accent     : {accent}")
        print(f"Noise      : {noise_level}")
        print(f"Audio file : {filename}")
        print("-" * 70)

        if not os.path.exists(audio_path):

            print("Status     : SKIPPED")
            print("Reason     : Audio file not found.")

            results.append({
                "test_id": f"{accent}_{noise_level}",
                "accent": accent,
                "noise_level": noise_level,
                "audio_file": filename,
                "status": "skipped",
                "reason": "Audio file not found",
                "reference_text": REFERENCE_TEXT,
                "transcribed_text": "",
                "accuracy_percent": None
            })

            continue

        try:

            transcription = processor.transcribe(
                audio_path
            )

            predicted_text = transcription["text"]

            accuracy = calculate_word_accuracy(
                REFERENCE_TEXT,
                predicted_text
            )

            print(f"Status     : SUCCESS")
            print(f"Language   : {transcription['language']}")
            print(
                f"Language probability: "
                f"{transcription['language_probability']}"
            )

            print(f"\nTranscription:")
            print(predicted_text)

            print(
                f"\nWord accuracy: "
                f"{accuracy}%"
            )

            results.append({
                "test_id": f"{accent}_{noise_level}",
                "accent": accent,
                "noise_level": noise_level,
                "audio_file": filename,
                "status": "success",
                "reference_text": REFERENCE_TEXT,
                "transcribed_text": predicted_text,
                "language": transcription["language"],
                "language_probability": transcription[
                    "language_probability"
                ],
                "accuracy_percent": accuracy
            })

        except Exception as error:

            print("Status     : FAILED")
            print(f"Error      : {error}")

            results.append({
                "test_id": f"{accent}_{noise_level}",
                "accent": accent,
                "noise_level": noise_level,
                "audio_file": filename,
                "status": "failed",
                "reason": str(error),
                "reference_text": REFERENCE_TEXT,
                "transcribed_text": "",
                "accuracy_percent": None
            })

    # --------------------------------------------------
    # Calculate summary
    # --------------------------------------------------

    successful_results = [
        result
        for result in results
        if result["status"] == "success"
    ]

    accuracies = [
        result["accuracy_percent"]
        for result in successful_results
        if result["accuracy_percent"] is not None
    ]

    if accuracies:

        overall_accuracy = round(
            sum(accuracies) / len(accuracies),
            2
        )

    else:

        overall_accuracy = None

    # --------------------------------------------------
    # Accent-wise summary
    # --------------------------------------------------

    accent_summary = {}

    for accent in [
        "indian",
        "american",
        "british"
    ]:

        accent_results = [
            result
            for result in successful_results
            if result["accent"] == accent
        ]

        accent_scores = [
            result["accuracy_percent"]
            for result in accent_results
            if result["accuracy_percent"] is not None
        ]

        if accent_scores:

            accent_summary[accent] = {
                "tests_completed": len(accent_scores),
                "average_accuracy_percent": round(
                    sum(accent_scores) / len(accent_scores),
                    2
                )
            }

        else:

            accent_summary[accent] = {
                "tests_completed": 0,
                "average_accuracy_percent": None
            }

    # --------------------------------------------------
    # Noise-wise summary
    # --------------------------------------------------

    noise_summary = {}

    for noise_level in [
        "clean",
        "low_noise",
        "medium_noise",
        "high_noise"
    ]:

        noise_results = [
            result
            for result in successful_results
            if result["noise_level"] == noise_level
        ]

        noise_scores = [
            result["accuracy_percent"]
            for result in noise_results
            if result["accuracy_percent"] is not None
        ]

        if noise_scores:

            noise_summary[noise_level] = {
                "tests_completed": len(noise_scores),
                "average_accuracy_percent": round(
                    sum(noise_scores) / len(noise_scores),
                    2
                )
            }

        else:

            noise_summary[noise_level] = {
                "tests_completed": 0,
                "average_accuracy_percent": None
            }

    # --------------------------------------------------
    # Final report
    # --------------------------------------------------

    report = {
        "report_name": "ZecPath STT Accuracy Test Report",
        "report_version": "1.0",
        "model": {
            "name": "Faster-Whisper",
            "model_size": "base",
            "device": "CPU",
            "compute_type": "int8"
        },
        "test_configuration": {
            "total_test_cases": len(TEST_FILES),
            "accents": [
                "indian",
                "american",
                "british"
            ],
            "noise_conditions": [
                "clean",
                "low_noise",
                "medium_noise",
                "high_noise"
            ],
            "reference_text": REFERENCE_TEXT
        },
        "summary": {
            "total_tests": len(TEST_FILES),
            "successful_tests": len(successful_results),
            "skipped_tests": len([
                result
                for result in results
                if result["status"] == "skipped"
            ]),
            "failed_tests": len([
                result
                for result in results
                if result["status"] == "failed"
            ]),
            "overall_average_accuracy_percent": overall_accuracy
        },
        "accent_summary": accent_summary,
        "noise_summary": noise_summary,
        "test_results": results
    }

    # --------------------------------------------------
    # Save JSON report
    # --------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n")
    print("=" * 70)
    print("STT ACCURACY TEST COMPLETED")
    print("=" * 70)

    print(
        f"Total tests      : {len(TEST_FILES)}"
    )

    print(
        f"Successful tests : {len(successful_results)}"
    )

    print(
        f"Overall accuracy : "
        f"{overall_accuracy}%"
    )

    print(
        f"\nReport saved to:"
    )

    print(OUTPUT_FILE)

    print("=" * 70)


if __name__ == "__main__":
    main()