# ZecPath Deliverable 3 - Stability Report

- Generated: 2026-10-14T12:38:20
- Overall status: **PASS_WITH_LIMITATIONS**

## Validation checks

| Check | Status | Details |
|---|---|---|
| Day 56 report | PASS | Day 56 report exists and contains valid JSON. |
| demo_data_used | REVIEW_REQUIRED | Demo data was used. Do not interpret demo results as real candidate results. |
| human_vs_ai_comparison_performed | REVIEW_REQUIRED | Human-vs-AI comparison has not been performed. |
| Cross-round weights | PASS | Weights: {'ats': 0.3, 'hr': 0.3, 'aptitude': 0.4}; total = 1.00. |
| Candidate ATS coverage | PASS | 8/8 candidates have valid ATS scores. |
| HR and aptitude source scores | PASS | 3/3 source score files contain valid scores. |
| Cross-round data completeness | REVIEW_REQUIRED | 1/8 candidates have all required cross-round scores in their candidate output. |

## Candidate ATS coverage

| Candidate | Status | ATS score | Details |
|---|---|---:|---|
| candidate_006 | PASS | 90.10 | Valid ATS score: 90.10/100. |
| candidate_007 | PASS | 89.33 | Valid ATS score: 89.33/100. |
| candidate_008 | PASS | 92.54 | Valid ATS score: 92.54/100. |
| candidate_009 | PASS | 91.92 | Valid ATS score: 91.92/100. |
| candidate_010 | PASS | 93.27 | Valid ATS score: 93.27/100. |
| candidate_011 | PASS | 91.56 | Valid ATS score: 91.56/100. |
| candidate_012 | PASS | 94.29 | Valid ATS score: 94.29/100. |
| candidate_013 | PASS | 37.90 | Valid ATS score: 37.90/100. |

## Cross-round coverage

| Candidate | Status | Missing fields | Details |
|---|---|---|---|
| candidate_006 | PASS | None | All required cross-round scores are present and valid. |
| candidate_007 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |
| candidate_008 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |
| candidate_009 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |
| candidate_010 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |
| candidate_011 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |
| candidate_012 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |
| candidate_013 | INCOMPLETE | hr_score, aptitude_score, cross_round_score | One or more required cross-round scores are missing. |

## Interpretation

- This checker validates available output files and scores.
- Missing data is reported as incomplete; it is not invented.
- Demo data does not establish real-world hiring accuracy.
- A successful stability check does not prove fairness or predictive accuracy.
- Human-vs-AI evaluation must be performed and documented separately.
