# ZecPath – Bias Reduction Documentation

## 1. Purpose

The purpose of the bias-reduction approach in ZecPath is to improve the
fairness, consistency, and transparency of automated resume evaluation.

The system focuses primarily on job-related information such as:

- Skills
- Relevant experience
- Education
- Semantic similarity between resume and job description

The system attempts to avoid using non-essential personal attributes
for candidate scoring.

---

## 2. Sources of Potential Bias

Automated resume screening can produce biased results when irrelevant
candidate information influences the evaluation.

Potential sources of bias include:

- Name
- Gender-related information
- Age
- Photograph
- Personal address
- Marital status
- Nationality
- Other non-job-related personal information

These attributes should not contribute to the ATS score when they are
not relevant to the job requirements.

---

## 3. Job-Related Scoring Parameters

ZecPath uses job-related scoring parameters.

The main scoring components are:

1. Skill Match
2. Experience Relevance
3. Education Alignment
4. Semantic Similarity

These components are combined to produce the ATS score.

Example:

    Skill Match          → 35%
    Experience Relevance → 25%
    Education Alignment  → 15%
    Semantic Similarity  → 25%

The weights can be configured according to the target role.

---

## 4. Skill Matching and Bias Reduction

The system does not rely only on exact keyword matching.

Different representations of the same skill can occur in resumes.

Examples:

    Python
    PYTHON
    Python Programming

These can be normalized to:

    python

Similarly:

    Mongo
    Mongo DB
    MongoDB

can be normalized to:

    mongodb

This reduces the possibility that formatting or terminology differences
unfairly reduce a candidate's skill score.

---

## 5. Semantic Similarity

Semantic similarity is used to reduce excessive dependence on exact
keywords.

The system generates embeddings for:

- Resume
- Job Description

The embeddings are compared using cosine similarity.

This allows the system to identify semantic relationships between
resume content and job requirements.

For example, a candidate may describe a skill differently from the
exact wording used in the job description.

Semantic matching can help identify relevant meaning even when the
exact keyword is not present.

---

## 6. Score Normalization

Different scoring components may use different numerical ranges.

The normalization logic converts available scores into a common
0–100 scale.

For example:

    0.71 → 71.00
    0.85 → 85.00

Scores are also restricted to the valid range:

    Minimum = 0
    Maximum = 100

This makes the scoring components easier to compare and combine.

---

## 7. Missing Data Handling

A candidate may not provide all information.

For example:

- Experience may be missing.
- Education information may be incomplete.
- A scoring component may not be available.

The system does not automatically assign a zero score to missing
information.

Instead, unavailable components can be excluded from the weighted
calculation and the remaining weights can be normalized.

This reduces the risk of unfairly penalizing candidates because of
missing information.

---

## 8. Personal Attribute Masking

Non-essential personal attributes should not be used as scoring
parameters.

Examples include:

- Name
- Photograph
- Age
- Gender
- Marital status
- Personal address

The scoring framework should focus on job-related qualifications.

For example:

    Skills
    Experience
    Education
    Job relevance

should contribute to candidate evaluation.

Personal characteristics that are not required for the role should not
contribute to the score.

---

## 9. Transparent Scoring

ZecPath provides a component-level scoring breakdown.

Example:

    Skill Match          : 70
    Experience Relevance : 85
    Education Alignment  : 90
    Semantic Similarity  : 75

The final score is calculated from these components.

This makes the result more explainable than using a single unexplained
score.

---

## 10. Fair Score Calculation

The fair score is calculated using available scoring components.

Conceptually:

    Fair Score =
        Weighted Score of Available Components
        ---------------------------------------
             Total Available Weight

For example, if one component is missing, the available components
can be reweighted rather than automatically assigning zero to the
missing component.

---

## 11. Bias Indicators

The system should be evaluated for indicators that may suggest
unfair scoring.

Important indicators include:

- Large differences in scores caused by irrelevant information
- Excessive dependence on exact keywords
- Missing-data penalties
- Inconsistent score ranges
- Personal information influencing the score
- Unexpected differences between candidates with similar
  qualifications

These indicators should be reviewed during system testing.

---

## 12. Fairness Improvements Implemented

The ZecPath scoring framework includes the following fairness
improvements:

### 12.1 Text Normalization

Text is converted into a standard representation.

Example:

    PYTHON
    Python
    python

becomes:

    python

### 12.2 Skill Alias Normalization

Common variations are mapped to standard skill names.

Example:

    DRF
    Django REST

can be mapped to:

    django rest framework

### 12.3 Score Normalization

Scores are converted to a common 0–100 scale.

### 12.4 Missing Data Handling

Missing scoring components are handled without automatically
assigning an unfair zero score.

### 12.5 Semantic Matching

Semantic similarity reduces excessive dependence on exact
keyword matching.

### 12.6 Job-Related Evaluation

The scoring framework focuses on qualifications relevant to the
target job.

---

## 13. Example

Consider two candidates.

### Candidate A

    Python
    Django
    FastAPI
    MongoDB
    4 years experience

### Candidate B

    Python Programming
    Django REST Framework
    Mongo DB
    4 years experience

Without normalization, the systems may identify differences in the
skill names.

After normalization:

### Candidate A

    python
    django
    fastapi
    mongodb

### Candidate B

    python
    django rest framework
    mongodb

This produces a more consistent representation for further
evaluation.

---

## 14. Limitations

The bias-reduction approach does not guarantee that the entire
recruitment process is completely free from bias.

Potential limitations include:

- Resume formatting differences
- Incomplete candidate information
- Bias present in the original job description
- Bias in training or evaluation data
- Limitations of semantic models
- Incorrect skill normalization
- Errors in resume parsing

Therefore, automated scoring should support recruiter decision-making
rather than completely replace human review.

---

## 15. Human Review

Candidates in uncertain or borderline scoring ranges should be
available for manual review.

The system can classify candidates into categories such as:

    Strong Match
    Good Match
    Moderate Match
    Poor Match

Candidates with insufficient information or borderline scores can be
flagged for recruiter review.

---

## 16. Transparency

The system should provide recruiters with:

- Final ATS score
- Individual component scores
- Matching status
- Recommendation
- Strengths
- Areas to review
- Normalization information
- Missing-data information

This allows recruiters to understand why a candidate received a
particular score.

---

## 17. Audit and Monitoring

The scoring system should be periodically reviewed.

Recommended checks include:

1. Compare scores of candidates with similar qualifications.
2. Check whether irrelevant personal information affects scores.
3. Check whether missing information causes unfair penalties.
4. Review keyword and semantic matching behavior.
5. Check score distributions.
6. Review borderline candidates manually.
7. Update normalization rules when necessary.

---

## 18. Conclusion

ZecPath's bias-reduction approach aims to make resume screening more
consistent, transparent, and job-focused.

The system improves fairness through:

- Resume normalization
- Skill normalization
- Score normalization
- Semantic similarity
- Missing-data handling
- Job-related scoring
- Explainable score breakdown
- Human review for uncertain cases

The objective is not to eliminate all possible bias automatically,
but to reduce avoidable sources of bias and make the candidate
evaluation process more transparent and consistent.