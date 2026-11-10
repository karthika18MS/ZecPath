# ZecPath AI Screening Metadata Standards

## 1. Purpose

This document defines the metadata standards used for AI screening
conversations in the ZecPath system.

Metadata provides consistent identification, tracking, and validation
of candidates, jobs, screening questions, transcript interactions,
timestamps, and transcription confidence.

The standards ensure that voice screening data can be reliably processed
by downstream AI components.

---

## 2. Metadata Fields

The following metadata fields are mandatory for screening interactions:

| Field | Data Type | Required | Description |
|---|---|---|---|
| candidate_id | String | Yes | Unique identifier of the candidate |
| job_id | String | Yes | Unique identifier of the job |
| question_id | String | Yes | Identifier of the screening question |
| timestamp | ISO 8601 datetime | Yes | Time at which the interaction occurred |
| confidence | Float | Yes | Speech-to-text confidence score between 0 and 1 |

---

## 3. Candidate ID

### Field

`candidate_id`

### Type

String

### Required

Yes

### Description

Identifies the candidate participating in the screening call.

### Format

Existing ZecPath candidate identifiers should be used.

Example:

```text
candidate_006
candidate_007
candidate_008