ZecPath -- Reusable End-to-End Simulation Environment
Day 63/64 deliverable: configurable end-to-end simulation for
processing candidate datasets through ATS, assessment, cross-round
scoring, final decision, and reporting stages.
1. Overview
This simulation environment connects the existing ZecPath modules into
one reusable workflow. It is designed to:
Read candidate data from a configurable dataset root.
Validate the dataset structure and supported input files.
Load candidate profiles, resumes, job descriptions, and assessment
responses.
Run the ATS and assessment pipelines.
Reuse existing ATS results to avoid executing ATS scoring twice.
Combine available round scores and produce final decision records.
Generate candidate-level, batch, and performance reports.
Record stage status and execution details in a simulation summary.
The current tested dataset is `day63_demo_dataset`. The successful
end-to-end run executed all 12 configured stages. Dataset validation was
reported as `INCOMPLETE` because resumes were missing for CAND007 and
CAND010; those candidates were blocked from ATS processing. A successful
pipeline run does not mean every candidate has complete input data.
2. Project structure
The simulation directory is:
``` text
day63_demo_dataset/
└── 06_end_to_end_simulation/
    ├── README.md
    ├── batch_process_resumes.py
    ├── config_loader.py
    ├── cross_round_scoring_engine.py
    ├── run_simulation.py
    ├── test_ats_result_reuse.py
    ├── adapters/
    │   ├── aptitude_adapter.py
    │   ├── ats_adapter.py
    │   ├── generate_machine_test_demo_data.py
    │   ├── hr_adapter.py
    │   ├── jd_adapter.py
    │   ├── machine_test_adapter.py
    │   ├── resume_adapter.py
    │   └── technical_adapter.py
    ├── config/
    │   ├── cross_round_weights.json
    │   ├── dataset_schema.json
    │   ├── pipeline_config.json
    │   └── scoring_weights.json
    ├── loaders/
    │   ├── candidate_loader.py
    │   ├── dataset_loader.py
    │   ├── job_description_loader.py
    │   └── resume_loader.py
    ├── outputs/
    │   ├── [pipeline result JSON files]
    │   ├── batch_report.json
    │   ├── batch_report.md
    │   ├── performance_report.json
    │   ├── performance_report.md
    │   ├── simulation_run_summary.json
    │   └── candidate_results/
    ├── pipeline/
    │   ├── aptitude_pipeline.py
    │   ├── ats_input_pipeline.py
    │   ├── ats_pipeline.py
    │   ├── ats_scoring_pipeline.py
    │   ├── cross_round_pipeline.py
    │   ├── final_decision_pipeline.py
    │   ├── hr_pipeline.py
    │   ├── machine_test_pipeline.py
    │   └── technical_pipeline.py
    ├── reporting/
    │   ├── batch_report.py
    │   ├── candidate_report.py
    │   └── performance_report.py
    ├── results/
    └── validators/
        ├── candidate_validator.py
        ├── input_validator.py
        └── score_validator.py
```
The dataset root is separate from the simulation code. It contains the
input folders:
``` text
<dataset_root>/
├── 01_candidate_profiles/
├── 02_sample_resumes/
├── 03_job_descriptions/
└── 04_candidate_responses/
    ├── hr_responses/
    ├── aptitude_responses/
    ├── technical_responses/
    └── machine_test_responses/
```
The `outputs/` folder is created under the simulation directory, not
inside the dataset root.
3. Requirements and setup
Run commands from the project root, for example:
``` cmd
cd /d D:\ZecPath-AI
venv\Scripts\activate
```
Use the project's existing virtual environment and install the
dependencies required by the integrated ZecPath modules. The simulation
uses Python modules already present in the project, including the ATS,
HR, aptitude, technical, and machine-test engines, plus their required
third-party packages.
The ATS semantic-matching stage uses the
`sentence-transformers/all-MiniLM-L6-v2` model. Ensure the model is
available locally or that the environment can access the model when it
is first needed.
4. Configure the dataset
Edit:
``` text
06_end_to_end_simulation/config/pipeline_config.json
```
The configuration has three sections: `dataset`, `execution`, and
`reporting`.
Example:
``` json
{
    "module": "ZecPath Day 63 End-to-End Simulation",
    "dataset": {
        "dataset_name": "day63_demo_dataset",
        "dataset_root": "D:/ZecPath-AI/day63_demo_dataset",
        "dataset_type": "DEMO_DATASET"
    },
    "execution": {
        "timeout_seconds": 900,
        "continue_on_stage_failure": false,
        "validate_outputs": true
    },
    "reporting": {
        "generate_candidate_reports": true,
        "generate_batch_report": true,
        "generate_performance_report": true
    }
}
```
Dataset configuration fields
---
Field                               Purpose
---
`dataset_name`                      Human-readable dataset identifier
used in reports.
`dataset_root`                      Absolute path or
project-root-relative path to the
dataset directory.
`dataset_type`                      Dataset classification, for example
`DEMO_DATASET` or an appropriate
label for another dataset.
If `dataset_root` is relative, the configuration loader resolves it
relative to the project root. The directory must already exist.
Execution settings
`timeout_seconds`: maximum allowed execution time for an individual
stage, in seconds.
`continue_on_stage_failure`: controls whether the orchestrator
continues after a stage failure.
`validate_outputs`: enables output validation where supported by the
orchestrator.
Reporting settings
`generate_candidate_reports`: enables candidate report generation.
`generate_batch_report`: enables batch report generation.
`generate_performance_report`: enables performance report
generation.
The configuration loader checks that required sections and dataset
fields exist, that the timeout is a positive integer, and that boolean
settings have boolean values.
5. Dataset input requirements
The dataset must follow the directory and file conventions described by
`config/dataset_schema.json`.
Candidate profiles
Location: `01_candidate_profiles/`
Format: JSON files.
Each profile must contain a non-empty `candidate_id`.
Profiles associate a candidate with a job using the dataset's
candidate/job identifiers.
Resumes
Location: `02_sample_resumes/`
Supported formats in the configured schema: PDF and DOCX.
Resume files are discovered using the candidate identifier/file
naming convention implemented by the resume loader.
A missing resume is treated as missing input; it should not be
represented as a valid ATS score.
Job descriptions
Location: `03_job_descriptions/`
Format: TXT.
The loader locates job descriptions using the job identifier and the
configured filename convention.
Candidate responses
HR: `04_candidate_responses/hr_responses/`
Aptitude: `04_candidate_responses/aptitude_responses/`
Technical: `04_candidate_responses/technical_responses/`
Machine test: `04_candidate_responses/machine_test_responses/`
Response files use JSON and the candidate-specific naming
conventions expected by the corresponding adapters.
Machine-test input validation also checks the required task,
test-result, and review-score fields defined in `dataset_schema.json`.
Important: Use the actual schema file as the authoritative
definition of required JSON keys and nested fields. This README
describes the directory layout and high-level requirements; it does not
replace schema validation.
6. Validate and inspect configuration
From the project root:
``` cmd
python day63_demo_dataset\06_end_to_end_simulation\config_loader.py
```
This displays the resolved configuration and reports whether
configuration loading succeeded.
Validate the dataset:
``` cmd
python day63_demo_dataset\06_end_to_end_simulation\validators\input_validator.py
```
Review the validation report and correct missing directories, invalid
JSON, unsupported files, or missing required fields before expecting
every candidate to complete all stages.
7. Run the complete simulation
From the project root:
``` cmd
python day63_demo_dataset\06_end_to_end_simulation\run_simulation.py
```
The orchestrator runs the configured stages in dependency order:
`ATS_INPUT` -- loads candidate profiles, resumes, and job
descriptions; prepares ATS input and identifies blocked records.
`ATS_SCORING` -- scores candidates with available ATS input.
`ATS` -- integrates ATS results and eligibility processing. It
reuses existing ATS input/scoring outputs instead of executing ATS
scoring again.
`HR` -- processes HR interview response data.
`APTITUDE` -- processes aptitude and logical-reasoning/scenario
response data.
`TECHNICAL` -- processes technical interview response data.
`MACHINE_TEST` -- processes machine-test records through the
machine-test scoring engine.
`CROSS_ROUND` -- combines available assessment scores using
configured round weights and tracks score coverage.
`FINAL_DECISION` -- generates the final decision status from the
cross-round results and eligibility rules.
`CANDIDATE_REPORT` -- creates an individual JSON and Markdown report
for each candidate/job result.
`BATCH_REPORT` -- creates an aggregate batch JSON and Markdown
report.
`PERFORMANCE_REPORT` -- summarizes pipeline status, execution-time
information, and validation metrics.
A stage may be marked successful even when some candidate records are
incomplete or blocked. Always inspect the dataset validation report and
candidate-level statuses as well as the overall pipeline status.
8. Run individual reporting modules
These commands are useful when the final decision output already exists
and only a report needs to be regenerated.
``` cmd
python day63_demo_dataset\06_end_to_end_simulation\reporting\candidate_report.py
python day63_demo_dataset\06_end_to_end_simulation\reporting\batch_report.py
python day63_demo_dataset\06_end_to_end_simulation\reporting\performance_report.py
```
Run the full orchestrator for the normal end-to-end workflow.
9. Output files
Generated files are stored under:
``` text
06_end_to_end_simulation/outputs/
```
Important outputs include:
---
Output                                   Description
---
`dataset_validation_report.json`         Dataset structure, profile, resume,
JD, and response validation
details.
`ats_input_results.json`                 Prepared ATS inputs and
missing/blocked input statuses.
`ats_scoring_results.json`               ATS scoring-stage output.
`ats_pipeline_results.json`              Integrated ATS and eligibility
pipeline output.
`hr_pipeline_results.json`               HR pipeline output.
`aptitude_pipeline_results.json`         Aptitude pipeline output.
`technical_pipeline_results.json`        Technical interview pipeline
output.
`machine_test_pipeline_results.json`     Machine-test pipeline output.
`cross_round_pipeline_results.json`      Cross-round scoring output.
`final_decision_pipeline_results.json`   Final candidate decision records.
`candidate_results/`                     Individual candidate/job JSON and
Markdown reports.
`batch_report.json` / `batch_report.md`  Aggregate candidate and decision
summary.
`performance_report.json` /              Performance summary for the
`performance_report.md`                  integrated pipelines.
`simulation_run_summary.json`            Overall stage statuses and
execution summary.
Some adapters also write intermediate result files such as
`hr_results.json`, `aptitude_results.json`, `technical_results.json`,
and `machine_test_results.json`.
10. Score and decision interpretation
Cross-round scoring uses the weights configured in
`config/cross_round_weights.json`. The engine normalizes across
available round scores and records score coverage. A missing assessment
score is not automatically treated as zero.
Eligibility is a separate gate from the unified score. Final decision
statuses can include:
`ELIGIBLE_FOR_NEXT_STAGE`
`MANUAL_REVIEW`
`NOT_ELIGIBLE`
`BLOCKED_PENDING_ATS`
Check the generated result JSON for the exact status, score coverage,
and reason fields.
11. Missing input and error handling
Examples of expected conditions:
Missing resume: candidate is blocked from ATS input.
Missing response: the relevant assessment can be incomplete or not
provided.
Invalid JSON: the file should be reported as invalid by the relevant
validator or loader.
Missing required directory or configuration field: configuration or
dataset validation should report the issue.
Failed dependency stage: dependent stages may be skipped according
to the orchestrator's dependency and failure-handling logic.
Do not interpret a missing assessment as a score of zero unless the
scoring policy explicitly defines that behavior. Resolve missing inputs
and rerun the simulation when complete results are required.
12. Test with another dataset
The simulation is intended to use a different dataset by changing
configuration rather than editing the Python source.
Create a second dataset directory under the project root or at
another accessible path.
Arrange its candidate profiles, resumes, job descriptions, and
response folders according to the same schema and naming
conventions.
Copy the existing `pipeline_config.json` as a backup.
Change only the dataset identity and root in `pipeline_config.json`,
for example:
``` json
"dataset": {
    "dataset_name": "second_test_dataset",
    "dataset_root": "D:/ZecPath-AI/second_test_dataset",
    "dataset_type": "TEST_DATASET"
}
```
Keep the `execution` and `reporting` sections as required.
Run dataset validation and inspect its report.
Run the simulation:
``` cmd
python day63_demo_dataset\06_end_to_end_simulation\run_simulation.py
```
Confirm that the logs and output metadata identify
`second_test_dataset`, and that input files were read from its
configured root.
Important verification: The current end-to-end run proves the first
dataset works. The second-dataset requirement is not complete until a
second dataset has actually been tested. Some modules in the broader
project may still contain dataset-specific assumptions; if the second
run reads from the original dataset, writes to an unexpected location,
or fails due to a hardcoded path, treat that as a portability defect to
fix before claiming the environment is fully reusable.
Restore the original configuration after the test if you want to return
to `day63_demo_dataset`.
13. Current test status
The recorded test run for `day63_demo_dataset` reported:
12 stages executed.
12 successful stages.
0 failed stages.
0 skipped stages.
Overall pipeline status: `SUCCESS`.
Dataset validation: `INCOMPLETE`.
Missing resumes: CAND007 and CAND010.
ATS-ready candidates: 8 of 10.
Cross-round scored candidates: 9 of 10.
Final decisions: 3 eligible, 2 manual review, 3 not eligible, and 2
blocked pending ATS.
The reporting modules were also executed individually:
Candidate reports: 10 generated, 0 failed.
Batch report: generated successfully for 10 candidates.
Performance report: 7 of 7 monitored pipelines successful, with 0
reported validation errors.
These figures describe the tested demo dataset and may change when a
different dataset is configured.
14. Data quality and responsible interpretation
The current dataset contains simulated/demo assessment data. In
particular, machine-test scores and review values are marked as
simulated. HR, aptitude, and technical outputs in this demo workflow
should not be represented as verified human evaluations unless they have
actually been collected and assessed by qualified reviewers.
The simulation demonstrates pipeline integration, data handling, scoring
orchestration, and reporting. Its generated scores and decisions are not
validated hiring recommendations and should not be used as the sole
basis for real recruitment decisions.
15. Troubleshooting checklist
Confirm the virtual environment is activated.
Run commands from the project root.
Confirm `config/pipeline_config.json` contains a valid JSON object.
Confirm `dataset_root` points to the intended dataset directory.
Check that all required dataset subdirectories exist.
Check candidate IDs, job IDs, filenames, and response JSON structure
against `dataset_schema.json`.
Review `dataset_validation_report.json` before investigating
candidate-level blocks.
Review `simulation_run_summary.json` for failed or skipped stages.
Check that the local sentence-transformer model is available for ATS
semantic matching.
Do not treat a library deprecation warning as a pipeline failure
when the stage reports success; schedule the library migration
separately.
---
End of README -- ZecPath Reusable End-to-End Simulation Environment