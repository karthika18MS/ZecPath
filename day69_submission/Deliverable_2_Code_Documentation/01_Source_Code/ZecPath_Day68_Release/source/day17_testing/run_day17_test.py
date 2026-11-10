import os
import sys
import json

from parsers.extractor import extract_resume


# ==========================================================
# ZecPath Day 17 Test Runner
# ==========================================================


# ==========================================================
# STEP 1: Check Candidate ID
# ==========================================================

if len(sys.argv) < 2:

    print("\nUsage:")

    print(
        "python -m day17_testing.run_day17_test candidate_006"
    )

    print("\nExample:")

    print(
        "python -m day17_testing.run_day17_test candidate_007"
    )

    sys.exit(1)


candidate_id = sys.argv[1]


# ==========================================================
# STEP 2: Project Paths
# ==========================================================

BASE_DIR = "day17_testing"


TEST_CASE_FILE = os.path.join(
    BASE_DIR,
    "test_cases.json"
)


RESUMES_DIR = os.path.join(
    BASE_DIR,
    "resumes"
)


JOB_DESCRIPTION_DIR = os.path.join(
    BASE_DIR,
    "job_descriptions"
)


RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)


# ==========================================================
# STEP 3: Check test_cases.json
# ==========================================================

if not os.path.exists(TEST_CASE_FILE):

    print(
        "\nError: test_cases.json not found."
    )

    print(
        TEST_CASE_FILE
    )

    sys.exit(1)


# ==========================================================
# STEP 4: Read Test Cases
# ==========================================================

with open(
    TEST_CASE_FILE,
    "r",
    encoding="utf-8"
) as file:

    test_cases = json.load(
        file
    )


# ==========================================================
# STEP 5: Check Candidate
# ==========================================================

if candidate_id not in test_cases:

    print(
        f"\nError: {candidate_id} "
        "not found in test_cases.json."
    )

    print(
        "\nAvailable candidates:"
    )

    for candidate in test_cases:

        print(
            "•",
            candidate
        )

    sys.exit(1)


# ==========================================================
# STEP 6: Read Candidate Configuration
# ==========================================================

candidate_config = test_cases[
    candidate_id
]


target_role = candidate_config[
    "target_role"
]


job_description_name = candidate_config[
    "job_description"
]


# ==========================================================
# STEP 7: Find Resume
# ==========================================================
#
# Supports:
#
# candidate_006.docx
# candidate_006.pdf
#
# ==========================================================

possible_extensions = [
    ".docx",
    ".pdf"
]


resume_path = None


for extension in possible_extensions:

    possible_path = os.path.join(
        RESUMES_DIR,
        candidate_id + extension
    )

    if os.path.exists(
        possible_path
    ):

        resume_path = possible_path

        break


# ==========================================================
# Check Resume
# ==========================================================

if resume_path is None:

    print(
        "\nError: Resume not found for:"
    )

    print(
        candidate_id
    )

    print(
        "\nExpected:"
    )

    print(
        os.path.join(
            RESUMES_DIR,
            candidate_id + ".docx"
        )
    )

    print(
        "or"
    )

    print(
        os.path.join(
            RESUMES_DIR,
            candidate_id + ".pdf"
        )
    )

    sys.exit(1)


# ==========================================================
# STEP 8: Find Job Description
# ==========================================================

job_description_path = os.path.join(
    JOB_DESCRIPTION_DIR,
    job_description_name
)


if not os.path.exists(
    job_description_path
):

    print(
        "\nError: Job description not found:"
    )

    print(
        job_description_path
    )

    sys.exit(1)


# ==========================================================
# STEP 9: Create Candidate Result Folder
# ==========================================================

candidate_result_folder = os.path.join(
    RESULTS_DIR,
    candidate_id
)


os.makedirs(
    candidate_result_folder,
    exist_ok=True
)


# ==========================================================
# STEP 10: Display Test Information
# ==========================================================

print(
    "\n=============================================="
)

print(
    "       ZecPath DAY 17 INPUT VALIDATION"
)

print(
    "==============================================\n"
)


print(
    "Candidate ID     :",
    candidate_id
)

print(
    "Resume           :",
    resume_path
)

print(
    "Target Role      :",
    target_role
)

print(
    "Job Description  :",
    job_description_path
)


# ==========================================================
# STEP 11: Resume Extraction
# ==========================================================

print(
    "\n----------------------------------------------"
)

print(
    "STEP 1: RESUME EXTRACTION"
)

print(
    "----------------------------------------------\n"
)


try:

    cleaned_text = extract_resume(
        resume_path
    )

    print(
        "Resume extraction successful."
    )

except Exception as error:

    print(
        "\nResume extraction failed:"
    )

    print(
        error
    )

    sys.exit(1)


# ==========================================================
# STEP 12: Save Cleaned Resume
# ==========================================================

cleaned_resume_file = os.path.join(
    candidate_result_folder,
    "cleaned_resume.txt"
)


with open(
    cleaned_resume_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        cleaned_text
    )


# ==========================================================
# STEP 13: Read Job Description
# ==========================================================

print(
    "\n----------------------------------------------"
)

print(
    "STEP 2: JOB DESCRIPTION"
)

print(
    "----------------------------------------------\n"
)


try:

    with open(
        job_description_path,
        "r",
        encoding="utf-8"
    ) as file:

        job_description = file.read()

    print(
        "Job description loaded successfully."
    )

except Exception as error:

    print(
        "\nJob description loading failed:"
    )

    print(
        error
    )

    sys.exit(1)


# ==========================================================
# STEP 14: Save Job Description
# ==========================================================

job_description_output = os.path.join(
    candidate_result_folder,
    "job_description.txt"
)


with open(
    job_description_output,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        job_description
    )


# ==========================================================
# STEP 15: Create Test Information
# ==========================================================

test_information = {

    "candidate_id":
        candidate_id,

    "target_role":
        target_role,

    "resume_file":
        resume_path,

    "job_description_file":
        job_description_path,

    "resume_extraction":
        "SUCCESS",

    "job_description_loading":
        "SUCCESS"

}


# ==========================================================
# STEP 16: Save Test Information
# ==========================================================

test_information_file = os.path.join(
    candidate_result_folder,
    "test_information.json"
)


with open(
    test_information_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        test_information,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==========================================================
# STEP 17: Final Validation Result
# ==========================================================

print(
    "\n=============================================="
)

print(
    "       DAY 17 INPUT VALIDATION RESULT"
)

print(
    "==============================================\n"
)


print(
    "Candidate:",
    candidate_id
)

print(
    "Target Role:",
    target_role
)

print(
    "Resume extraction: SUCCESS"
)

print(
    "Job description loading: SUCCESS"
)


print(
    "\nFiles saved in:"
)

print(
    candidate_result_folder
)