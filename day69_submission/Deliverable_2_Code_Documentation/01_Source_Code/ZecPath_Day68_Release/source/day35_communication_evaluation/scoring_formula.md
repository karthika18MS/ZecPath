# Day 35 — Communication Skill Evaluation
## Scoring Formula Documentation

---

## 1. Overview

The Communication Scoring Model evaluates the quality of a
candidate's communication response during an AI HR interview.

The model evaluates the following communication dimensions:

1. Fluency
2. Grammar Quality
3. Vocabulary Range
4. Clarity of Explanation
5. Answer Structure

Filler words are also detected and used as a supporting indicator
for fluency and clarity.

The final communication score is normalized to a range of:

**0–100**

---

## 2. Communication Metrics

### 2.1 Fluency

Fluency measures how continuously and smoothly the candidate
communicates.

The model considers:

- Number of words
- Response length
- Filler word frequency

Base score:

**70**

Response length adjustment:

- 20 or more words → +20
- 10–19 words → +15
- 5–9 words → +10
- Less than 5 words → -15

Filler word penalty:

**5 points are deducted for each detected filler word.**

The final fluency score is restricted to:

**0–100**

---

### 2.2 Grammar Quality

Grammar quality provides a basic estimate of grammatical
organization in the candidate's response.

The model considers:

- Presence of common verbs
- Sentence-ending punctuation
- Response length

Base score:

**70**

Adjustments:

- Common grammatical verb detected → +15
- Response ends with `.`, `!`, or `?` → +10
- Response contains 2 or fewer words → -20

The final grammar score is restricted to:

**0–100**

---

### 2.3 Vocabulary Range

Vocabulary range estimates the variety of words used by the
candidate.

The model calculates the unique-word ratio:

**Vocabulary Ratio = Unique Words / Total Words**

Scoring:

- Ratio >= 0.80 → +30
- Ratio >= 0.65 → +20
- Ratio >= 0.50 → +10

Additional response-length adjustment:

- 20 or more words → +15
- 10–19 words → +10

Base score:

**50**

The final vocabulary score is restricted to:

**0–100**

---

### 2.4 Clarity of Explanation

Clarity measures how clearly the candidate explains an answer.

The model considers:

- Response length
- Filler words

Base score:

**70**

Response-length adjustment:

- 8–60 words → +20
- More than 60 words → +5
- Less than 8 words → -10

Filler word penalty:

**5 points are deducted for each detected filler word.**

The final clarity score is restricted to:

**0–100**

---

### 2.5 Answer Structure

Answer structure measures how well the candidate organizes
their explanation.

The model looks for transition and organization words such as:

- first
- then
- next
- finally
- because
- therefore
- however
- also
- during
- after
- before

Base score:

**60**

Transition-word adjustment:

- 3 or more transition words → +30
- 2 transition words → +20
- 1 transition word → +10

Additional adjustment:

- 15 or more words → +10

The final structure score is restricted to:

**0–100**

---

## 3. Filler Word Detection

The model detects common filler words such as:

- um
- uh
- hmm
- erm
- er
- ah
- like
- actually
- basically
- you know

The system stores both:

1. Filler word count
2. Detected filler words

Example:

```text
Candidate Response:
"Um, I think I worked with a team, uh, during my project."

Filler words:
um
uh

Filler word count:
2