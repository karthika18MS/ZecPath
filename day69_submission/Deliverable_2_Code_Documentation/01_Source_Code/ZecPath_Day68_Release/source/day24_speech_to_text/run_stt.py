import json
import os
import sys


# Add the Day 24 folder to Python's import path
DAY24_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    DAY24_DIR
)

from stt_processor import SpeechToTextProcessor


AUDIO_FILE = os.path.join(
    DAY24_DIR,
    "audio",
    "sample.wav"
)

OUTPUT_FILE = os.path.join(
    DAY24_DIR,
    "results",
    "sample_transcription.json"
)


def main():

    print("=" * 70)
    print("ZecPath - Day 24")
    print("Speech-to-Text Processor")
    print("=" * 70)

    # ---------------------------------------------
    # Check audio file
    # ---------------------------------------------

    if not os.path.exists(AUDIO_FILE):

        print("\nAudio file not found:")
        print(AUDIO_FILE)

        print(
            "\nPlease place a WAV audio file named "
            "'sample.wav' inside:"
        )

        print(
            os.path.join(
                DAY24_DIR,
                "audio"
            )
        )

        return

    # ---------------------------------------------
    # Load model
    # ---------------------------------------------

    print("\nLoading Speech-to-Text model...")
    print("Model: Faster-Whisper base")
    print("Device: CPU")
    print("Compute type: int8")

    processor = SpeechToTextProcessor(
        model_size="base"
    )

    print("\nModel loaded successfully.")

    # ---------------------------------------------
    # Transcribe audio
    # ---------------------------------------------

    print("\nTranscribing audio...")

    result = processor.transcribe(
        AUDIO_FILE
    )

    # ---------------------------------------------
    # Create results directory
    # ---------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    # ---------------------------------------------
    # Save result
    # ---------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ---------------------------------------------
    # Display result
    # ---------------------------------------------

    print("\nSpeech-to-Text completed successfully.")

    print(
        f"\nDetected language: "
        f"{result['language']}"
    )

    print(
        f"Language confidence: "
        f"{result['language_probability']}"
    )

    print(
        f"\nTranscript:"
    )

    print(
        result["text"]
    )

    print(
        f"\nNumber of segments: "
        f"{len(result['segments'])}"
    )

    print(
        f"\nResult saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)


if __name__ == "__main__":
    main()