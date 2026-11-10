import json
from pathlib import Path

from eligibility_engine.eligibility_engine import (
    EligibilityDecisionEngine
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DAY18_RESULTS_DIR = (
    PROJECT_ROOT
    / "day18_optimization"
    / "results"
)

ELIGIBILITY_ENGINE_DIR = (
    PROJECT_ROOT
    / "eligibility_engine"
)

RULES_FILE = (
    ELIGIBILITY_ENGINE_DIR
    / "eligibility_rules.json"
)

OUTPUT_DIR = (
    ELIGIBILITY_ENGINE_DIR
    / "results"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# LOAD JSON FILE
# =========================================================

def load_json(file_path: Path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# SAVE JSON FILE
# =========================================================

def save_json(
    data,
    file_path: Path
):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# LOAD ELIGIBILITY RULES
# =========================================================

def load_eligibility_rules():

    if not RULES_FILE.exists():

        raise FileNotFoundError(
            "Eligibility rules file not found:\n"
            f"{RULES_FILE}"
        )

    rules = load_json(
        RULES_FILE
    )

    if not isinstance(
        rules,
        dict
    ):

        raise ValueError(
            "eligibility_rules.json must contain "
            "a JSON object."
        )

    if "default_rules" not in rules:

        raise ValueError(
            "eligibility_rules.json must contain "
            "'default_rules'."
        )

    if "roles" not in rules:

        raise ValueError(
            "eligibility_rules.json must contain "
            "'roles'."
        )

    return rules


# =========================================================
# NORMALIZE ROLE NAME
# =========================================================

def normalize_role_name(role):

    if role is None:

        return ""

    role = str(
        role
    ).strip().lower()

    role = role.replace(
        "-",
        "_"
    )

    role = role.replace(
        " ",
        "_"
    )

    return role


# =========================================================
# GET ROLE RULES
# =========================================================

def get_role_rules(
    all_rules,
    target_role
):

    roles = all_rules.get(
        "roles",
        {}
    )

    normalized_role = normalize_role_name(
        target_role
    )

    # -----------------------------------------------------
    # Exact role match
    # -----------------------------------------------------

    if normalized_role in roles:

        return (
            roles[normalized_role],
            f"role: {normalized_role}"
        )

    # -----------------------------------------------------
    # Use default rules if role is not configured
    # -----------------------------------------------------

    return (
        all_rules.get(
            "default_rules",
            {}
        ),
        "default_rules"
    )


# =========================================================
# FIND DAY 18 ATS RESULT FILES
# =========================================================

def find_day18_results():

    if not DAY18_RESULTS_DIR.exists():

        return []

    return sorted(
        DAY18_RESULTS_DIR.glob(
            "*/day18_optimized_ats_score.json"
        )
    )


# =========================================================
# BUILD CANDIDATE INPUT
# =========================================================

def build_candidate_input(
    day18_result
):
    """
    Build additional candidate information.

    Day 18 currently does not provide reliable
    location or notice-period fields.

    Therefore these values remain None instead
    of inventing candidate information.
    """

    return {

        "location": None,

        "notice_period_days": None
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 80)
    print("        ZecPath DAY 21 ELIGIBILITY ENGINE")
    print("=" * 80)

    # =====================================================
    # LOAD RULE CONFIGURATION
    # =====================================================

    print()
    print(
        "Loading eligibility rules..."
    )

    try:

        all_rules = load_eligibility_rules()

    except Exception as error:

        print()
        print(
            "ERROR loading eligibility rules:"
        )

        print(
            str(error)
        )

        return

    print(
        "Eligibility rules loaded successfully."
    )

    print()
    print(
        "Rules file:"
    )

    print(
        RULES_FILE
    )

    # =====================================================
    # DAY 18 RESULTS DIRECTORY
    # =====================================================

    print()
    print(
        "Day 18 Results Directory:"
    )

    print(
        DAY18_RESULTS_DIR
    )

    result_files = find_day18_results()

    print()
    print(
        "Total Day 18 Results Found: "
        f"{len(result_files)}"
    )

    if not result_files:

        print()
        print(
            "ERROR: No Day 18 ATS result files found."
        )

        return

    # =====================================================
    # COUNTERS
    # =====================================================

    successful_count = 0
    failed_count = 0

    eligible_count = 0
    review_count = 0
    rejected_count = 0

    summary_results = []

    # =====================================================
    # PROCESS EACH CANDIDATE
    # =====================================================

    for result_file in result_files:

        print()
        print("-" * 80)

        candidate_folder = (
            result_file.parent.name
        )

        print(
            f"Processing: {candidate_folder}"
        )

        try:

            # =================================================
            # LOAD DAY 18 RESULT
            # =================================================

            day18_result = load_json(
                result_file
            )

            if not isinstance(
                day18_result,
                dict
            ):

                raise ValueError(
                    "Day 18 result must be a JSON object."
                )

            # =================================================
            # BASIC CANDIDATE INFORMATION
            # =================================================

            candidate_id = day18_result.get(
                "candidate_id",
                candidate_folder
            )

            target_role = day18_result.get(
                "target_role",
                "Unknown"
            )

            job_description = day18_result.get(
                "job_description",
                "Unknown"
            )

            # =================================================
            # GET ROLE-SPECIFIC RULES
            # =================================================

            recruiter_rules, rule_source = (
                get_role_rules(
                    all_rules,
                    target_role
                )
            )

            # =================================================
            # DISPLAY INFORMATION
            # =================================================

            print(
                f"Candidate ID : {candidate_id}"
            )

            print(
                f"Target Role  : {target_role}"
            )

            print(
                f"Rule Source  : {rule_source}"
            )

            # =================================================
            # BUILD CANDIDATE DATA
            # =================================================

            candidate = build_candidate_input(
                day18_result
            )

            # =================================================
            # CREATE ELIGIBILITY ENGINE
            # =================================================

            engine = EligibilityDecisionEngine(
                recruiter_rules
            )

            # =================================================
            # RUN ELIGIBILITY EVALUATION
            # =================================================

            result = engine.evaluate(
                day18_result=day18_result,
                candidate=candidate
            )

            # =================================================
            # ADD CONFIGURATION INFORMATION
            # =================================================

            result[
                "rule_source"
            ] = rule_source

            result[
                "applied_rules"
            ] = recruiter_rules

            # =================================================
            # EXTRACT DECISION
            # =================================================

            eligibility_data = result.get(
                "eligibility",
                {}
            )

            status = eligibility_data.get(
                "status",
                "Unknown"
            )

            reason = eligibility_data.get(
                "reason",
                "No reason available."
            )

            failed_rules = eligibility_data.get(
                "failed_rules",
                []
            )

            # =================================================
            # COUNT RESULT
            # =================================================

            successful_count += 1

            if status == "Eligible":

                eligible_count += 1

            elif status == "Review":

                review_count += 1

            elif status == "Rejected":

                rejected_count += 1

            # =================================================
            # ATS SCORE
            # =================================================

            ats_data = result.get(
                "ats",
                {}
            )

            ats_score = ats_data.get(
                "score"
            )

            # =================================================
            # DISPLAY RESULT
            # =================================================

            if ats_score is None:

                print(
                    "ATS Score    : N/A"
                )

            else:

                print(
                    f"ATS Score    : {ats_score:.2f}"
                )

            print(
                f"Eligibility  : {status}"
            )

            print(
                f"Reason       : {reason}"
            )

            if failed_rules:

                print(
                    "Failed Rules : "
                    + ", ".join(
                        failed_rules
                    )
                )

            else:

                print(
                    "Failed Rules : None"
                )

            # =================================================
            # SAVE INDIVIDUAL RESULT
            # =================================================

            candidate_output_dir = (
                OUTPUT_DIR
                / candidate_id
            )

            candidate_output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            output_file = (
                candidate_output_dir
                / "eligibility_result.json"
            )

            save_json(
                result,
                output_file
            )

            print(
                "Result saved: "
                f"{output_file}"
            )

            # =================================================
            # ADD TO SUMMARY
            # =================================================

            summary_results.append({

                "candidate_id":
                    candidate_id,

                "target_role":
                    target_role,

                "job_description":
                    job_description,

                "ats_score":
                    ats_score,

                "eligibility":
                    status,

                "reason":
                    reason,

                "failed_rules":
                    failed_rules,

                "rule_source":
                    rule_source
            })

        except Exception as error:

            failed_count += 1

            print()
            print(
                "ERROR processing "
                f"{result_file}:"
            )

            print(
                str(error)
            )

    # =====================================================
    # DAY 21 SUMMARY
    # =====================================================

    summary = {

        "engine":
            "ZecPath Day 21 Eligibility Decision Engine",

        "rules_file":
            str(RULES_FILE),

        "day18_results_directory":
            str(DAY18_RESULTS_DIR),

        "total_candidates":
            len(result_files),

        "successful":
            successful_count,

        "failed":
            failed_count,

        "eligible":
            eligible_count,

        "review":
            review_count,

        "rejected":
            rejected_count,

        "results":
            summary_results
    }

    # =====================================================
    # SAVE SUMMARY
    # =====================================================

    summary_file = (
        OUTPUT_DIR
        / "day21_eligibility_summary.json"
    )

    save_json(
        summary,
        summary_file
    )

    # =====================================================
    # PRINT SUMMARY TABLE
    # =====================================================

    print()
    print()
    print("=" * 80)
    print("             DAY 21 ELIGIBILITY SUMMARY")
    print("=" * 80)

    print()

    print(
        f"{'Candidate':<18}"
        f"{'Role':<30}"
        f"{'ATS':<10}"
        f"{'Decision':<12}"
    )

    print("-" * 80)

    for item in summary_results:

        candidate_id = item.get(
            "candidate_id",
            "Unknown"
        )

        role = item.get(
            "target_role",
            "Unknown"
        )

        ats = item.get(
            "ats_score"
        )

        decision = item.get(
            "eligibility",
            "Unknown"
        )

        if ats is None:

            ats_display = "N/A"

        else:

            ats_display = f"{ats:.2f}"

        print(
            f"{candidate_id:<18}"
            f"{role:<30}"
            f"{ats_display:<10}"
            f"{decision:<12}"
        )

    print("-" * 80)

    print(
        f"Total Candidates : "
        f"{len(result_files)}"
    )

    print(
        f"Successful       : "
        f"{successful_count}"
    )

    print(
        f"Failed           : "
        f"{failed_count}"
    )

    print(
        f"Eligible         : "
        f"{eligible_count}"
    )

    print(
        f"Review           : "
        f"{review_count}"
    )

    print(
        f"Rejected         : "
        f"{rejected_count}"
    )

    print()

    print(
        "Summary saved to:"
    )

    print(
        summary_file
    )

    print()
    print("=" * 80)

    print(
        "Day 21 eligibility evaluation completed."
    )

    print("=" * 80)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()