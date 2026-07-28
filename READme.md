Project Layout
Zecpath_AI/
│
├── ats_engine/
├── data/
├── interview_ai/
├── logs/
├── models/
├── parsers/
├── scoring/
├── screening_ai/
├── tests/
├── utils/
│
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
Folder Explanation
1. ats_engine/

Purpose:
This folder contains the Applicant Tracking System (ATS) logic.

Responsibilities:

Calculate ATS scores
Match resumes with job descriptions
Rank candidates
Shortlist eligible applicants

Example:
If a job requires Python, SQL, and Machine Learning, the ATS engine checks whether the uploaded resume contains these skills and assigns a score.

2. data/

Purpose:
Stores all datasets used by the AI system.

Examples:

Candidate resumes
Job descriptions
Sample interview questions
Training datasets

The AI models use this data for training and testing.

3. interview_ai/

Purpose:
Contains the AI interview modules.

Responsibilities:

Generate interview questions
Conduct HR interviews
Conduct technical interviews
Evaluate candidate responses

In future, this module may use Large Language Models (LLMs) to ask adaptive questions.

4. logs/

Purpose:
Stores application log files.

Current file:

app.log

Why it is needed:

Records application events
Tracks errors
Helps developers debug issues
Maintains execution history
5. models/

Purpose:
Stores trained AI and Machine Learning models.

Examples:

resume_parser.pkl

ats_model.pkl

interview_model.pt

Instead of training the model every time, the application loads it from this folder.

6. parsers/

Purpose:
Contains resume parsing modules.

Responsibilities:

Read PDF resumes
Extract candidate information
Identify skills, education, experience, and certifications
Convert resumes into structured data
7. scoring/

Purpose:
Calculates different candidate scores.

Examples:

ATS score
Interview score
Technical score
Communication score
Final recommendation score

These scores help recruiters compare candidates objectively.

8. screening_ai/

Purpose:
Handles AI-based screening before interviews.

Responsibilities:

Voice screening
Speech-to-text conversion
Natural Language Processing (NLP)
Initial candidate evaluation

This module filters candidates before they reach the interview stage.

9. tests/

Purpose:
Contains automated test cases.

Current file:

test_sample.py

Responsibilities:

Verify code correctness
Detect bugs
Ensure future code changes do not break existing functionality

Testing improves software quality.

10. utils/

Purpose:
Stores common utility files used across the project.

Current files:

config.py

logger.py
config.py

Stores application settings such as:

Application name
Version
Author
Debug mode
logger.py

Configures the logging system and writes logs to app.log.

Keeping common utilities in one place avoids code duplication.

File Explanation
main.py

Purpose:
This is the entry point of the application.

When you run:

python main.py

Python starts executing from this file.

Currently it:

Imports configuration values
Initializes the logger
Displays application information
Records application start and finish events
README.md

Purpose:
Provides documentation for the project.

It explains:

Project overview
Features
Folder structure
Installation steps
Technologies used
Usage instructions

Anyone opening the GitHub repository can understand the project by reading this file.

requirements.txt

Purpose:
Lists all Python libraries required by the project.

Example:

numpy
pandas
fastapi
pytest
torch
transformers

Installing dependencies is easy:

pip install -r requirements.txt
.gitignore

Purpose:
Specifies files and folders that Git should not upload.

Examples:

venv/
__pycache__/
.env
logs/

Ignoring these prevents unnecessary or sensitive files from being stored in the repository.

Overall Project Flow
User
   │
   ▼
main.py
   │
   ├── Reads configuration (config.py)
   ├── Initializes logging (logger.py)
   ├── Uses ATS Engine
   ├── Uses Screening AI
   ├── Uses Interview AI
   ├── Uses Scoring Module
   ├── Reads/Writes Data
   └── Saves logs in app.log