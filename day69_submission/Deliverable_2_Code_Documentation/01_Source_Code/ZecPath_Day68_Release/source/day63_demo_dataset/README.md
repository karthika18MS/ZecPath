# ZecPath – Day 63 Demo Dataset

**Project:** ZecPath – AI-Powered Job Portal & Automated Hiring Assistant

**Day:** 63

**Deliverable:** Demo Dataset Creation

**Version:** 1.0

---

## 1. Introduction

The Day 63 Demo Dataset is created to demonstrate and test the complete functionality of the ZecPath AI-powered hiring system.

It contains fictional candidate profiles, sample resumes, job descriptions, interview responses and expected hiring pipeline scenarios.

The dataset is designed to represent different candidate types and real-world recruitment situations.

## 2. Objective

The main objective is to prepare realistic sample data to demonstrate the complete hiring pipeline.

The dataset supports testing of:

- Resume processing
- ATS matching
- Candidate screening
- Eligibility evaluation
- HR interview scoring
- Aptitude assessment
- Technical interview evaluation
- Cross-round scoring

## 3. Folder Structure

```text
day63_demo_dataset/
│
├── 01_candidate_profiles/
│   ├── candidate_001.json
│   ├── candidate_002.json
│   ├── candidate_003.json
│   ├── candidate_004.json
│   ├── candidate_005.json
│   ├── candidate_006.json
│   ├── candidate_007.json
│   ├── candidate_008.json
│   ├── candidate_009.json
│   └── candidate_010.json
│
├── 02_sample_resumes/
│   ├── excellent/
│   ├── average/
│   ├── poor/
│   ├── fresher/
│   └── experienced/
│
├── 03_job_descriptions/
│   ├── JD001_mern_developer.txt
│   ├── JD002_python_developer.txt
│   └── JD003_java_developer.txt
│
├── 04_candidate_responses/
│   ├── hr_responses/
│   ├── aptitude_responses/
│   └── technical_responses/
│
├── 05_expected_scenarios/
│   ├── candidate_scenarios.json
│   └── expected_pipeline_scenarios.json
│
└── README.md
```

## 4. Candidate Categories

The dataset contains 10 fictional candidates.

| Candidate ID | Candidate Type | Target Role |
|---|---|---|
| CAND001 | Excellent | MERN Developer |
| CAND002 | Average | Python Developer |
| CAND003 | Weak | MERN Developer |
| CAND004 | Fresher | Java Developer |
| CAND005 | Experienced | Java Developer |
| CAND006 | Strong Technical | Python Developer |
| CAND007 | Missing Mandatory Skill | MERN Developer |
| CAND008 | Poor Resume | Python Developer |
| CAND009 | Communication Focused | MERN Developer |
| CAND010 | Incomplete Assessment | Java Developer |

## 5. Job Description Details

Three sample job descriptions are included.

### JD001 – MERN Stack Developer

- Experience: 2–4 years
- Mandatory skills: React.js, Node.js, Express.js, MongoDB and JavaScript.
- Preferred skills: REST APIs, Git and JWT Authentication.

### JD002 – Python Developer

- Experience: 1–3 years
- Mandatory skills: Python, Django and SQL.
- Preferred skills: Flask, Pandas, NumPy and Scikit-learn.

### JD003 – Java Developer

- Experience: 3–6 years
- Mandatory skills: Java, Spring Boot and SQL.
- Preferred skills: Hibernate, Microservices, REST APIs and Maven.

## 6. Candidate Response Data

Three types of interview and assessment responses are included.

### HR Responses

Contains candidate answers for:

- Self-introduction
- Strengths and weaknesses
- Teamwork
- Problem-solving
- Motivation
- Job-related questions

### Aptitude Responses

Contains:

- Logical reasoning questions
- Numerical reasoning
- Pattern recognition
- Scenario-based problem-solving

### Technical Responses

Contains role-based technical questions for:

- MERN Stack
- Python
- Java

Questions include conceptual and scenario-based problems.

## 7. Expected Testing Scenarios

The dataset contains different test scenarios:

1. Strong candidate evaluation.
2. Average candidate evaluation.
3. Weak candidate evaluation.
4. Fresher eligibility checking.
5. Experienced candidate evaluation.
6. AI and Python specialization.
7. Missing mandatory skill validation.
8. Poor resume evaluation.
9. Communication versus technical evaluation.
10. Incomplete assessment handling.

## 8. Hiring Pipeline

The demo dataset supports the following hiring workflow:

```text
Candidate Profile
       |
       v
Resume Processing
       |
       v
ATS Matching
       |
       v
Candidate Screening
       |
       v
Eligibility Evaluation
       |
       v
HR Interview
       |
       v
Aptitude Assessment
       |
       v
Technical Interview
       |
       v
Cross-Round Evaluation
       |
       v
Final Candidate Evaluation
```

## 9. Data Format

The dataset uses:

- JSON files for candidate profiles and interview responses.
- PDF files for sample resumes.
- TXT files for job descriptions.
- JSON files for expected testing scenarios.
- Markdown for dataset documentation.

## 10. Testing Guidelines

1. Load candidate profiles.
2. Extract text from sample resumes.
3. Process the corresponding job descriptions.
4. Run the ATS matching engine.
5. Run the candidate screening and eligibility modules.
6. Evaluate HR interview responses.
7. Evaluate aptitude responses.
8. Evaluate technical interview responses.
9. Run cross-round evaluation where sufficient results exist.
10. Compare actual engine outputs with the expected scenario behaviour.

## 11. Data Validation

Before executing the demo:

- Verify that candidate IDs are unique.
- Verify that job IDs match the candidate profiles.
- Ensure resume filenames match their candidate profiles.
- Validate all JSON files.
- Check that the job descriptions contain the expected skills.
- Ensure that assessment responses use consistent candidate IDs.
- Preserve incomplete assessment records.
- Verify that no artificial scores are treated as actual engine results.

## 12. Important Notes

- All candidate information is fictional and created only for testing.
- Expected scenarios describe intended system behaviour, not actual generated results.
- Actual ATS and interview scores must be generated by the existing ZecPath evaluation modules.
- Missing assessment data must not be replaced with fabricated scores.
- The configured scoring weights and eligibility rules should be taken from the active ZecPath configuration.

## 13. Expected Outcome

After completing the demo dataset, ZecPath should have structured sample data to demonstrate resume processing, candidate-job matching, candidate screening, interview evaluation and the complete hiring pipeline.

The dataset also provides test cases for identifying missing skills, evaluating different experience levels and handling incomplete candidate assessments.

---

**End of Day 63 – Deliverable 1: Demo Dataset**