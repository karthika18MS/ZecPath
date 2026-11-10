from eligibility_engine.eligibility_engine import EligibilityDecisionEngine


# ---------------------------------------------------------
# JOB RULES
# ---------------------------------------------------------

job_rules = {
    "job_role": "python_developer",

    "ats": {
        "eligible_min": 75,
        "review_min": 60
    },

    "mandatory_skills": [
        "python",
        "sql",
        "git"
    ],

    "experience": {
        "min_years": 2,
        "max_years": 5
    },

    "location": {
        "allowed": [
            "kochi",
            "thiruvananthapuram"
        ]
    },

    "availability": {
        "max_days": 30
    }
}


# ---------------------------------------------------------
# CANDIDATE
# ---------------------------------------------------------

candidate = {
    "candidate_id": "C001",

    "skills": [
        "Python",
        "SQL",
        "Git",
        "Pandas"
    ],

    "experience": 3,

    "location": "Kochi",

    "notice_period_days": 15
}


# ---------------------------------------------------------
# ATS OUTPUT
# ---------------------------------------------------------

ats_result = {
    "candidate_id": "C001",
    "job_id": "J001",
    "ats_score": 82
}


# ---------------------------------------------------------
# CREATE ENGINE
# ---------------------------------------------------------

engine = EligibilityDecisionEngine(job_rules)


# ---------------------------------------------------------
# EVALUATE CANDIDATE
# ---------------------------------------------------------

result = engine.evaluate(
    candidate=candidate,
    ats_result=ats_result
)


# ---------------------------------------------------------
# DISPLAY RESULT
# ---------------------------------------------------------

print("\n================================")
print("   ZecPath Eligibility Result")
print("================================")

print("Candidate ID :", result["candidate_id"])
print("Job ID       :", result["job_id"])
print("Job Role     :", result["job_role"])
print("ATS Score    :", result["ats_score"])
print("Eligibility  :", result["eligibility"])
print("Reason       :", result["reason"])

print("\nFailed Rules:")
print(result["failed_rules"])

print("\nDetailed Checks:")

for rule, details in result["details"].items():
    print(f"\n{rule}:")
    print(details)