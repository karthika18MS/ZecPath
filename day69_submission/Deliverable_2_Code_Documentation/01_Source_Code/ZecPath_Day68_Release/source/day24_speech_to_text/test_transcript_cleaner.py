from transcript_cleaner import TranscriptCleaner


def main():

    cleaner = TranscriptCleaner()

    test_cases = [
        {
            "name": "Filler words",
            "text": "Um, I have like three years, uh, of experience."
        },
        {
            "name": "Case normalization",
            "text": "I HAVE EXPERIENCE WITH PYTHON AND DJANGO"
        },
        {
            "name": "Punctuation",
            "text": "I have experience with python django and fastapi"
        },
        {
            "name": "Interrupted speech",
            "text": "I have worked with Python for three—"
        },
        {
            "name": "Partial answer",
            "text": "Three years"
        },
        {
            "name": "Silence",
            "text": ""
        }
    ]

    print("=" * 70)
    print("ZecPath - Day 24")
    print("Clean Transcript Processor Test")
    print("=" * 70)

    for test in test_cases:

        result = cleaner.clean(test["text"])

        print(f"\nTest: {test['name']}")
        print("-" * 70)

        print("Raw:")
        print(test["text"])

        print("\nCleaned:")
        print(result)

    print("\n" + "=" * 70)
    print("Testing completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()