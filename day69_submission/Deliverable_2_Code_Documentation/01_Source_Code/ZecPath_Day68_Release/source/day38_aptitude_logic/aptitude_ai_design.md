# Day 38 — Aptitude AI Design

## 1. Overview

The Aptitude AI module is designed to add cognitive and situational evaluation to the ZecPath HR Interview system.

The module evaluates how a candidate:

- Understands a problem
- Reasons through a situation
- Makes decisions
- Explains their thinking
- Approaches problem-solving

The objective is not only to check whether the final answer is correct, but also to evaluate the structure and clarity of the candidate's reasoning.

---

## 2. Objective

The objective of the Aptitude AI module is:

> To add cognitive and situational evaluation into the HR interview process.

The module introduces two major question types:

1. Logical Reasoning Questions
2. Situational Judgment Questions

The candidate's response is analyzed and converted into structured evaluation scores.

---

## 3. Aptitude AI Architecture

The overall architecture is:

Candidate
    ↓
Aptitude Question Selection
    ↓
Question Presented to Candidate
    ↓
Candidate Response
    ↓
Response Processing
    ↓
Question Type Identification
    ├── Logical Reasoning
    └── Situational Judgment
    ↓
Answer / Reasoning Analysis
    ↓
Score Calculation
    ↓
Aptitude Evaluation Result


---

## 4. Major Components

### 4.1 Aptitude Question Bank

The question bank stores the questions used by the Aptitude AI module.

Each question contains information such as:

- Question ID
- Category
- Difficulty
- Question text
- Expected answer type
- Scoring information

The question bank allows questions to be selected systematically instead of hard-coding them inside the scoring logic.

---

### 4.2 Question Selection

The system selects an appropriate question based on the configured question information.

Question selection can consider:

- Aptitude category
- Difficulty
- Candidate profile
- Role
- Question type

The selected question is then presented to the candidate.

---

### 4.3 Candidate Response Capture

After the question is presented, the candidate provides an answer.

The response may originate from the existing ZecPath screening/interview input pipeline.

The response can contain:

- Text
- Reasoning steps
- Decision
- Explanation
- Conclusion

The response is passed to the Aptitude AI evaluation layer.

---

## 5. Logical Reasoning Questions

Logical reasoning questions evaluate the candidate's ability to analyze information and reach a logical conclusion.

Examples of reasoning areas include:

- Logical relationships
- Sequence and pattern reasoning
- Problem analysis
- Decision reasoning
- Cause and effect
- Structured problem solving

The system should focus on the candidate's reasoning process rather than only matching an exact sentence.

---

## 6. Situational Judgment Questions

Situational judgment questions present realistic situations and ask the candidate what they would do.

Example:

> A teammate introduces an issue shortly before an important project deadline. What would you do?

The system evaluates whether the candidate:

1. Identifies the problem
2. Understands the impact
3. Considers possible actions
4. Chooses an appropriate action
5. Explains the reason for the decision
6. Considers the expected outcome

---

## 7. Ideal Answer Structure

For reasoning and situational questions, an ideal answer can be represented as:

Problem
    ↓
Problem Understanding
    ↓
Analysis
    ↓
Possible Options
    ↓
Decision
    ↓
Reasoning
    ↓
Expected Outcome

The candidate does not need to use these exact words.

The structure is used as an evaluation framework for identifying relevant reasoning elements.

---

## 8. Logical Thinking Evaluation

The Aptitude AI evaluates logical thinking using several parameters.

### 8.1 Problem Understanding

Measures whether the candidate correctly understands the given problem or situation.

### 8.2 Reasoning

Measures whether the candidate provides logical steps connecting the problem to the conclusion.

### 8.3 Decision Quality

Measures whether the candidate selects a reasonable decision based on the information available.

### 8.4 Explanation Clarity

Measures whether the candidate can clearly explain their reasoning.

### 8.5 Conclusion

Measures whether the candidate reaches a logical and relevant conclusion.

These parameters are later used by the Logical Reasoning Scoring Model.

---

## 9. Problem-Solving Clarity

Problem-solving clarity evaluates whether the candidate explains their approach in a structured way.

A structured response may follow:

1. Identify the problem
2. Analyze the situation
3. Consider possible solutions
4. Select an approach
5. Explain why the approach was selected
6. Describe the expected result

This allows the system to evaluate the candidate's problem-solving process rather than only the final answer.

---

## 10. Difficulty Levels

Aptitude questions can be organized into different difficulty levels:

- Easy
- Medium
- Hard

Difficulty is stored as question metadata.

Example:

```text
Question ID: APT_LOGIC_001
Category: logical_reasoning
Difficulty: medium