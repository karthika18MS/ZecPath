import os
import sys


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


from parsers.noisy_text_cleaner import (
    clean_noisy_resume_text
)


# ==========================================================
# INPUT
# ==========================================================

INPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "day18_optimization",
    "noisy_resume_sample.txt"
)


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "       ZecPath DAY 18 NOISY RESUME TEST"
    )
    print("=" * 70)

    if not os.path.exists(
        INPUT_PATH
    ):

        print(
            "\nERROR: Test file not found:"
        )

        print(
            INPUT_PATH
        )

        return

    # ------------------------------------------------------
    # Load noisy resume
    # ------------------------------------------------------

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        noisy_text = file.read()

    # ------------------------------------------------------
    # Clean
    # ------------------------------------------------------

    cleaned_text = (
        clean_noisy_resume_text(
            noisy_text
        )
    )

    # ------------------------------------------------------
    # Display original
    # ------------------------------------------------------

    print(
        "\n"
        + "-" * 70
    )

    print(
        "ORIGINAL NOISY TEXT"
    )

    print(
        "-" * 70
    )

    print(
        noisy_text
    )

    # ------------------------------------------------------
    # Display cleaned
    # ------------------------------------------------------

    print(
        "\n"
        + "-" * 70
    )

    print(
        "CLEANED TEXT"
    )

    print(
        "-" * 70
    )

    print(
        cleaned_text
    )

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    print(
        "\n"
        + "-" * 70
    )

    print(
        "CLEANING STATISTICS"
    )

    print(
        "-" * 70
    )

    print(
        f"Original characters : "
        f"{len(noisy_text)}"
    )

    print(
        f"Cleaned characters  : "
        f"{len(cleaned_text)}"
    )

    print(
        f"Original words      : "
        f"{len(noisy_text.split())}"
    )

    print(
        f"Cleaned words       : "
        f"{len(cleaned_text.split())}"
    )

    print(
        "\nNoisy resume handling test completed."
    )


if __name__ == "__main__":

    main()