\# ZecPath – AI-Powered Job Portal \& Automated Hiring Assistant



\*\*Release:\*\* v0.1.0-rc1

\*\*Release type:\*\* Validated demo release candidate

\*\*Python:\*\* 3.13.17



\## 1. Project Overview



ZecPath is an AI-powered recruitment assistance system designed to support resume screening, candidate evaluation, interview assessment, scoring and recruiter decision-making.



The system combines resume parsing, ATS scoring, eligibility checks, assessment-round scoring and recruiter reporting.



\## 2. Major Capabilities



\- Resume parsing and structured candidate information extraction

\- ATS scoring using skill, experience, education and semantic matching

\- Mandatory-skill validation

\- Candidate eligibility evaluation

\- AI-assisted HR interview scoring

\- Aptitude and logical reasoning evaluation

\- Technical skill and machine-test scoring

\- Cross-round score aggregation

\- Final candidate recommendations

\- Recruiter reports and structured JSON outputs

\- Logging, validation and error handling



\## 3. Technology Stack



\- Python 3.13

\- FastAPI

\- PyMuPDF

\- python-docx

\- NumPy and Pandas

\- Scikit-learn

\- PyTorch

\- Transformers and Sentence Transformers

\- Streamlit

\- Pytest



\## 4. Important Project Modules



\- `day17\_testing/` – ATS skill matching and testing

\- `day18\_optimization/` – Optimized ATS scoring and mandatory-skill safeguards

\- `day24\_speech\_to\_text/` – Speech and audio sample processing

\- `day37\_hr\_interview\_scoring/` – HR interview evaluation

\- `day38\_aptitude\_logic/` – Aptitude and logical reasoning scoring

\- `day41\_cross\_round\_scoring/` – Cross-round scoring

\- `day47\_technical\_skill\_scoring/` – Technical skill evaluation

\- `day50\_machine\_test\_scoring/` – Machine-test evaluation

\- `day63\_demo\_dataset/` – Demo dataset and end-to-end simulation

\- `day65\_final\_enhancements/` – Validation, recruiter API and final enhancements

\- `eligibility\_engine/` – Candidate eligibility evaluation

\- `tests/` – Project tests



\## 5. Installation



Use Python 3.13 and create a virtual environment:



```bash

python -m venv venv

```



Activate it on Windows:



```bash

venv\\Scripts\\activate

```



Install the project dependencies:



```bash

python -m pip install -r requirements.txt

```



Verify dependencies:



```bash

python -m pip check

```



\## 6. Testing



Run the test suite from the project root:



```bash

python -m pytest -v

```



The Day 68 validation run completed with:



\- 187 tests passed

\- 0 test failures

\- Test execution time: 1.51 seconds



\## 7. ATS Demo Validation



The validated Day 63 ATS demo processed 10 candidate records:



\- 8 candidates scored

\- 2 candidates blocked because resumes were missing

\- 0 processing errors



Mandatory-skill validation prevented candidates with missing mandatory skills from being shortlisted in the validated cases.



\## 8. Demo Data Notice



The included demo dataset and assessment outputs are for demonstration and testing. They must not be represented as live candidate records or actual recruitment decisions.



Missing assessment data must remain unavailable rather than being treated as a zero score.



\## 9. Human Review



ZecPath produces AI-assisted scores and recommendations. Recruiters must review candidate information and assessment evidence before making hiring decisions.



The current validation results do not establish production readiness, hiring accuracy, or freedom from bias.



\## 10. Release Information



Version: `0.1.0-rc1`



Release scope: Validated demo release candidate.



Validation includes Python compilation, module import checks, dependency consistency, ATS smoke testing and the project regression test suite.



For detailed test evidence, see the `validation/` directory.
