# ZecPath Day 56 - End-to-End AI Test Report

- Candidate ID: `candidate_006`
- Target role: Backend Developer
- Generated UTC: 2026-10-13T09:31:55.025783+00:00
- Overall status: **PASS_WITH_DEMO_DATA**
- Demonstration assessment data used: **Yes**
- AI versus human comparison: **Not performed**

## 1. Test summary

- Stages attempted: 12
- Stages passed: 12
- Stages failed: 0
- Output checks passed: 8
- Output checks failed: 0
- Score checks passed: 7
- Score checks failed: 0
- Total execution time: 53.072 seconds

## 2. Stage execution results

| Stage | Status | Time (seconds) | Demo data |
|---|---|---:|---|
| Resume extraction and input validation | PASS | 0.4033 | No |
| Skill matching | PASS | 0.0883 | No |
| Optimized semantic matching batch | PASS | 25.7279 | No |
| Experience matching | PASS | 0.0993 | No |
| Education matching | PASS | 0.0914 | No |
| Final ATS scoring | PASS | 0.0893 | No |
| Day 18 optimized ATS batch | PASS | 25.9294 | No |
| Day 21 eligibility engine | PASS | 0.2341 | No |
| Day 37 HR interview scoring - demonstration data | PASS | 0.0966 | Yes |
| Day 38 logical reasoning - demonstration data | PASS | 0.0989 | Yes |
| Day 38 scenario evaluation - demonstration data | PASS | 0.0828 | Yes |
| Day 41 cross-round scoring | PASS | 0.1044 | No |

## 3. Output file validation

| Check | Status | Details |
|---|---|---|
| Day 17 semantic matching output | PASS | JSON file exists and is readable. |
| Day 17 final ATS output | PASS | JSON file exists and is readable. |
| Day 18 optimized ATS output | PASS | JSON file exists and is readable. |
| Eligibility output | PASS | JSON file exists and is readable. |
| HR interview output | PASS | JSON file exists and is readable. |
| Logical reasoning output | PASS | JSON file exists and is readable. |
| Scenario evaluation output | PASS | JSON file exists and is readable. |
| Cross-round output | PASS | JSON file exists and is readable. |

## 4. Score validation

| Assessment | Status | Score |
|---|---|---:|
| Day 17 semantic similarity score | PASS | 0.82 |
| Day 17 final ATS score | PASS | 90.10 |
| Day 18 optimized ATS score | PASS | 90.10 |
| HR interview score | PASS | 91.47 |
| Logical reasoning score | PASS | 86.75 |
| Scenario evaluation score | PASS | 89.90 |
| Cross-round score | PASS | 89.80 |

## 5. Candidate assessment scores

| Assessment | Score |
|---|---:|
| Semantic similarity | 0.82 |
| ATS | 90.10 |
| Optimized ATS | 90.10 |
| HR interview | 91.47 |
| Logical reasoning | 86.75 |
| Scenario evaluation | 89.90 |
| Cross-round | 89.80 |

- Eligibility decision: Eligible
- Cross-round status: Complete

## 6. Candidate identity checks

| Assessment | Expected ID | Actual ID | Status |
|---|---|---|---|
| Day 17 semantic matching | candidate_006 | candidate_006 | PASS |
| HR interview | candidate_006 | candidate_006 | PASS |
| Logical reasoning | candidate_006 | candidate_006 | PASS |
| Scenario evaluation | candidate_006 | candidate_006 | PASS |

## 7. Limitations

- The Day 18 batch and eligibility runners process multiple candidates.
- HR, logical reasoning, and scenario assessment use demonstration inputs.
- A valid output does not by itself prove that the scoring result is accurate.
- Human-versus-AI comparison has not been performed.
- The optimized semantic batch processes configured candidates in one run; its stage time is the batch process duration.
- Model loading and network activity may affect execution time.
- Final hiring decisions require appropriate human review.

## 8. Conclusion

The recorded test status is **PASS_WITH_DEMO_DATA**. Review every failed stage and validation check before claiming that the entire pipeline passed. Demonstration assessments support integration testing but do not establish real-world hiring accuracy.
