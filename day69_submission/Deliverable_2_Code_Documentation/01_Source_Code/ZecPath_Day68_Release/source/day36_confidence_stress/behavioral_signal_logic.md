# Day 36 — Behavioral Signal Logic Documentation

## 1. Overview

The Behavioral Signal Logic module is designed to analyze observable communication patterns in candidate responses during an AI-based HR interview.

The system uses rule-based indicators to identify:

- Hesitation
- Uncertainty
- Repeated words
- Long pauses
- Speaking pace
- Sentiment
- Confidence indicators

The purpose is to provide structured communication signals that can be used by the AI screening and HR interview system.

These indicators describe response characteristics. They should not be treated as definitive measurements of a candidate's psychological or emotional state.

---

# 2. Objective

The main objective is to identify communication patterns that may indicate how confidently and clearly a candidate is responding.

The system processes a candidate response and produces structured behavioral information.

The overall flow is:

Candidate Response
        ↓
Text Normalization
        ↓
Behavioral Signal Detection
        ↓
Confidence Analysis
        ↓
Sentiment Analysis
        ↓
Structured Behavioral Output


---

# 3. Behavioral Signals

The system analyzes the following signals.

## 3.1 Hesitation

Hesitation refers to words or phrases that indicate the candidate is pausing or thinking before giving an answer.

Examples include:

- um
- uh
- hmm
- erm
- er
- ah
- I think
- I guess
- maybe
- perhaps
- probably

The system searches the response for these patterns.

Example:

"I think I worked on a backend project. Maybe I can explain more."

Detected:

- I think
- maybe

Hesitation count:

2

---

# 4. Uncertainty

Uncertainty indicators are phrases that suggest the candidate is not completely certain about the information being provided.

Examples:

- I'm not sure
- im not sure
- not sure
- I don't know
- I dont know
- possibly
- might be
- could be
- I believe
- as far as I know
- approximately
- around

Example:

"As far as I know, I worked on approximately three projects."

The system records the detected uncertainty phrases.

---

# 5. Repeated Words

Repeated words are detected when the same word occurs immediately more than once.

Example:

"I, I developed the APIs using Python."

Detected repeated word:

"I"

The system records:

- repetition_detected
- repetition_count
- repeated_words

This can be used as an observable speech-pattern indicator.

---

# 6. Long Pauses

Long pauses can indicate that the candidate took additional time before continuing the response.

The current system uses:

```text
Long Pause Threshold = 2 seconds