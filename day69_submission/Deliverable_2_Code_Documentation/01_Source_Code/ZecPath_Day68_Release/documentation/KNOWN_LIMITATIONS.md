\# ZecPath – Known Limitations



\## 1. Demo Dataset



All candidate profiles, resumes, job descriptions, and candidate responses included in this release are synthetic demonstration data. They do not represent real candidates.



\## 2. Existing Placeholder Files



The following files were already empty in the original project and remain unchanged in this release:



\- `day63\_demo\_dataset/06\_end\_to\_end\_simulation/config/scoring\_weights.json`

\- `day63\_demo\_dataset/06\_end\_to\_end\_simulation/loaders/candidate\_loader.py`

\- `day63\_demo\_dataset/06\_end\_to\_end\_simulation/loaders/job\_description\_loader.py`

\- `day63\_demo\_dataset/06\_end\_to\_end\_simulation/loaders/resume\_loader.py`

\- `day63\_demo\_dataset/06\_end\_to\_end\_simulation/results/batch\_summary.json`

\- `day63\_demo\_dataset/06\_end\_to\_end\_simulation/validators/candidate\_validator.py`



These files are placeholders and should not be considered independently implemented or operational components.



\## 3. Validation Evidence



The Day 68 regression test suite completed successfully with 187 passing tests. The release smoke test also passed for the Day 63 ATS demo pipeline, including mandatory-skill enforcement and blocked-candidate handling.



\## 4. Usage Note



This release is intended for demonstration, evaluation, and further development. Review configuration and placeholder modules before extending or deploying the system.
