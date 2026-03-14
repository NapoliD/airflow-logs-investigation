# Airflow Logs Investigation Guide — Portfolio Project Plan

## Project Goal

Build a portfolio-ready project that demonstrates how to investigate Airflow task logs in an AWS-based environment, using a realistic **Amazon MWAA** scenario, mock data, and executable example scripts.

The project should show not only technical knowledge of Airflow and AWS logging sources, but also a structured troubleshooting approach that could be used in a real production investigation.

---

## Final Deliverables

The project should include these core deliverables:

1. **English README**

   * Clear project overview
   * Architecture and investigation flow
   * Setup and demo instructions
   * Key learning outcomes

2. **Mock investigation scenario**

   * Realistic Amazon MWAA environment
   * Example DAG runs and task failures
   * Simulated logs from the main Airflow log sources

3. **Runnable demo script**

   * Reads mock data
   * Simulates a real investigation workflow
   * Shows how logs are located and interpreted

4. **Completed investigation report**

   * Documents findings from the mock scenario
   * Shows what was checked, what was found, and the conclusion

---

## Scope

### Included

* Amazon MWAA as the deployment model
* CloudWatch as the primary logging source
* S3 as the secondary logging source
* Airflow API as an alternative source
* Mock data that simulates a successful troubleshooting investigation
* English project documentation

### Excluded from the first version

* EKS-based Airflow deployments
* Full test suite
* Production-grade CLI tooling
* Multiple environments or multi-account support

---

## Technical Scenario

The project will simulate a completed log investigation in the following fictional environment:

| Field                | Simulated Value                   |
| -------------------- | --------------------------------- |
| AWS Account          | `123456789012`                    |
| AWS Region           | `us-east-1`                       |
| MWAA Environment     | `prod-data-pipeline`              |
| Airflow Version      | `2.8.1`                           |
| S3 Bucket            | `acme-corp-airflow-prod`          |
| CloudWatch Log Group | `airflow-prod-data-pipeline-Task` |

### Example DAG

Primary DAG used in the demo:

* `etl_sales_daily`

### Example Tasks

* `extract_data` → fails once, then retries
* `load_to_warehouse` → succeeds

This keeps the first version simple while still showing a realistic investigation path.

---

## Project Structure

```bash
airflow-logs-investigation/
├── README.md
├── README_esp.md
├── docs/
│   └── investigate_airflow_logs.md
├── templates/
│   └── investigation_report.md
├── examples/
│   └── completed_investigation_report.md
├── mock_data/
│   ├── cloudwatch/
│   │   └── sample_logs.json
│   ├── s3/
│   │   └── logs/
│   │       └── etl_sales_daily/
│   │           └── extract_data/
│   │               └── 2024-01-15T10:00:00+00:00/
│   │                   ├── 1.log
│   │                   └── 2.log
│   ├── api_responses/
│   │   └── task_logs.json
│   └── config/
│       ├── airflow.cfg
│       └── mwaa_environment.json
└── scripts/
    ├── mock_demo.py
    ├── fetch_cloudwatch_logs.py
    ├── fetch_s3_logs.py
    ├── fetch_api_logs.py
    └── requirements.txt
```

---

## Implementation Phases

## Phase 1 — Define the mock scenario ✅

Create a realistic troubleshooting case based on Amazon MWAA.

### Tasks

* Define the simulated AWS and Airflow environment
* Define the DAG and task instances
* Decide the failure pattern
* Define where the logs are stored and how they will be accessed

### Output

* Stable scenario to be reused across all docs and scripts

---

## Phase 2 — Create mock data ✅

Build only the minimum set of mock files needed to make the project believable and runnable.

### Files to create

* `mock_data/cloudwatch/sample_logs.json`
* `mock_data/s3/logs/.../1.log`
* `mock_data/s3/logs/.../2.log`
* `mock_data/api_responses/task_logs.json`
* `mock_data/config/airflow.cfg`
* `mock_data/config/mwaa_environment.json`

### Content guidelines

The logs should include realistic pipeline-style issues, such as:

* transient connection failure
* retry behavior
* stack trace excerpt
* successful rerun after retry

### Output

* Local mock data set that supports the full demo

---

## Phase 3 — Build the demo script ✅

Create a script that simulates how an engineer would investigate the issue.

### Primary script

* `scripts/mock_demo.py`

### What it should do

* Load environment metadata
* Identify the Airflow deployment type
* Check the configured logging destinations
* Read the CloudWatch mock logs
* Read the S3 fallback logs
* Read API-based task logs
* Summarize findings

### Goal

This script should be the main "showcase" artifact of the repo.

### Output

* A runnable demo that proves the project works end to end

---

## Phase 4 — Write the completed investigation report ✅

Create a sample investigation report based on the mock scenario.

### File

* `examples/completed_investigation_report.md`

### It should include

* Incident context
* Environment details
* Investigation steps
* Log sources checked
* Evidence collected
* Root cause summary
* Final conclusion
* Recommended next actions

### Output

* A polished example of operational and troubleshooting documentation

---

## Phase 5 — Create the English README ✅

Translate the project positioning into a clean English README suitable for GitHub.

### File

* `README.md`

### Sections to include

* Project overview
* Why this project matters
* Logging architecture in Airflow/MWAA
* Included mock data
* How to run the demo
* Example outputs
* Skills demonstrated

### Keep

* `README_esp.md` as the Spanish version

### Output

* Public-facing repo documentation ready for recruiters or clients

---

## Phase 6 — Add optional support scripts ✅

Once the demo works, add standalone example scripts for each log source.

### Files

* `scripts/fetch_cloudwatch_logs.py`
* `scripts/fetch_s3_logs.py`
* `scripts/fetch_api_logs.py`

### Expected level

Intermediate quality:

* clear functions
* basic error handling
* simple arguments if needed
* readable code for portfolio purposes

### Output

* Extra examples showing source-specific retrieval patterns

---

## Phase 7 — Documentation improvements

After the main project is complete, improve the supporting documentation.

### Optional additions

* English versions of:

  * `docs/investigate_airflow_logs.md`
  * `templates/investigation_report.md`
  * `checklists/airflow_logs_checklist.md`
* "Quick Demo" section in README
* "How to adapt to a real AWS environment" section

### Output

* More complete documentation without blocking the first release

---

## Recommended Execution Order

1. Define the MWAA mock scenario ✅
2. Create the mock data ✅
3. Build `mock_demo.py` ✅
4. Write the completed investigation report ✅
5. Create `README.md` in English ✅
6. Add optional source-specific scripts ✅
7. Expand documentation if needed (optional)

---

## Default Decisions

To avoid blocking progress, the project will proceed with these choices:

### Documentation

* Translate **only the README** in the first iteration

### Script complexity

* Use an **intermediate** level
* Readable, functional, and presentable
* No need for enterprise-grade abstraction yet

### Log realism

* Include **realistic pipeline-related errors**
* Avoid overly generic placeholder logs

### Deployment scope

* Focus on **Amazon MWAA only**
* Do not add EKS in version 1

---

## Success Criteria

The project will be considered complete when:

* The repo has a clear English README
* The mock MWAA scenario is coherent and realistic
* The demo script runs successfully using mock data
* The investigation report looks like a real troubleshooting artifact
* A reviewer can understand how Airflow logs are investigated in AWS from this project alone

---

## Portfolio Value

This project should help demonstrate skills in:

* Airflow operations knowledge
* AWS logging architecture
* MWAA troubleshooting
* production-style debugging workflow
* technical documentation
* Python automation for operational support

It is not just a tutorial repo. It should look like a practical investigation toolkit with a realistic case study.

---

## Suggested One-Line Positioning for GitHub

**Investigating Airflow task logs in Amazon MWAA using CloudWatch, S3, and API-based retrieval, with realistic mock data and an end-to-end troubleshooting demo.**
