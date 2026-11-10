# Day 29 – Error-Handling Flow Design

## 1. Purpose

The Error-Handling Flow Design defines how the ZecPath AI screening system handles unexpected, incomplete, unclear, or unsuitable candidate responses during an AI screening call.

The goal is to keep the conversation polite, controlled, and recoverable without unnecessarily terminating the screening.

The error-handling design works together with:

- Day 25 – Answer Understanding
- Day 26 – Screening Scoring
- Day 27 – Confidence & Sentiment Analysis
- Day 29 – AI Call Flow Logic
- Day 29 – Conversation State Machine

---

## 2. Error Types

The screening system handles the following response situations:

| Error / Situation | Description | Handling |
|---|---|---|
| Silence | Candidate does not provide an answer | Retry |
| Vague answer | Candidate provides insufficient information | Follow-up |
| Confusion | Candidate does not understand the question | Clarification |
| Off-topic answer | Candidate responds to an unrelated topic | Redirect |
| Repeated answer | Candidate repeats an earlier answer | Follow-up |
| Retry limit exceeded | Candidate repeatedly fails to provide a usable answer | Fail screening |

---

## 3. General Error-Handling Flow

```text
Candidate Response
        |
        v
Response Analysis
        |
        v
Identify Response Type
        |
        +-------------------+
        |                   |
        v                   v
     Valid              Problem
        |                   |
        v                   v
 Next Question       Identify Error Type
                            |
          +---------+-------+--------+---------+
          |         |                |         |
          v         v                v         v
       Silence   Confusion       Off-topic   Vague/
          |         |                |        Repeated
          v         v                v         v
        Retry   Clarification     Redirect  Follow-up
          |         |                |         |
          +---------+----------------+---------+
                            |
                            v
                    Candidate Responds
                            |
                            v
                    Process Again