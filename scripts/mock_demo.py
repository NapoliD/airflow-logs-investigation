#!/usr/bin/env python3
"""
Airflow Logs Investigation Demo

This script demonstrates how to investigate Airflow task logs
in an Amazon MWAA environment using mock data.

It simulates the workflow an engineer would follow to:
1. Identify the deployment type
2. Check logging configuration
3. Retrieve logs from CloudWatch, S3, and API
4. Analyze and summarize findings
"""

import json
import os
from pathlib import Path
from datetime import datetime


# Configuration
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num: int, description: str) -> None:
    """Print a numbered step."""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 50)


def load_json(filepath: Path) -> dict:
    """Load and parse a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def load_text(filepath: Path) -> str:
    """Load a text file."""
    with open(filepath, "r") as f:
        return f.read()


def step1_identify_environment() -> dict:
    """Step 1: Identify the Airflow deployment type and environment."""
    print_step(1, "Identifying Airflow Environment")

    env_file = MOCK_DATA_DIR / "config" / "mwaa_environment.json"
    env_data = load_json(env_file)
    env = env_data["Environment"]

    print(f"  Deployment Type:    Amazon MWAA (Managed Workflows)")
    print(f"  Environment Name:   {env['Name']}")
    print(f"  Status:             {env['Status']}")
    print(f"  Airflow Version:    {env['AirflowVersion']}")
    print(f"  AWS Region:         us-east-1")
    print(f"  Environment Class:  {env['EnvironmentClass']}")
    print(f"  Webserver URL:      {env['WebserverUrl']}")

    return env


def step2_check_logging_config(env: dict) -> dict:
    """Step 2: Check the logging configuration."""
    print_step(2, "Checking Logging Configuration")

    config_file = MOCK_DATA_DIR / "config" / "airflow.cfg"
    config_content = load_text(config_file)

    logging_config = env.get("LoggingConfiguration", {})

    print("  Remote Logging:     Enabled")
    print(f"  S3 Log Location:    s3://acme-corp-airflow-prod/logs")
    print()
    print("  CloudWatch Log Groups:")

    for log_type, config in logging_config.items():
        status = "ENABLED" if config.get("Enabled") else "DISABLED"
        level = config.get("LogLevel", "N/A")
        print(f"    - {log_type}: {status} ({level})")

    return {
        "remote_logging": True,
        "s3_bucket": "acme-corp-airflow-prod",
        "cloudwatch_enabled": True,
        "log_groups": logging_config
    }


def step3_retrieve_cloudwatch_logs() -> list:
    """Step 3: Retrieve logs from CloudWatch."""
    print_step(3, "Retrieving CloudWatch Logs")

    cw_file = MOCK_DATA_DIR / "cloudwatch" / "sample_logs.json"
    cw_data = load_json(cw_file)

    print(f"  Log Group:          {cw_data['logGroupName']}")
    print(f"  Log Streams Found:  {len(cw_data['logStreams'])}")
    print()
    print("  Available Streams:")
    for stream in cw_data["logStreams"]:
        print(f"    - {stream['logStreamName']}")

    # Find error events
    error_events = [e for e in cw_data["events"] if "ERROR" in e["message"]]
    print()
    print(f"  Total Events:       {len(cw_data['events'])}")
    print(f"  Error Events:       {len(error_events)}")

    return cw_data["events"]


def step4_retrieve_s3_logs() -> dict:
    """Step 4: Retrieve logs from S3."""
    print_step(4, "Retrieving S3 Logs")

    s3_base = MOCK_DATA_DIR / "s3" / "logs" / "etl_sales_daily" / "extract_data" / "2024-01-15T10:00:00+00:00"

    logs = {}
    for log_file in sorted(s3_base.glob("*.log")):
        attempt = log_file.stem
        content = load_text(log_file)
        logs[f"attempt_{attempt}"] = content
        lines = len(content.strip().split("\n"))
        print(f"  Found: {log_file.name} ({lines} lines)")

    print()
    print(f"  S3 Path: s3://acme-corp-airflow-prod/logs/etl_sales_daily/extract_data/")
    print(f"  Total Attempts Found: {len(logs)}")

    return logs


def step5_retrieve_api_logs() -> dict:
    """Step 5: Retrieve logs via Airflow REST API."""
    print_step(5, "Retrieving Logs via REST API")

    api_file = MOCK_DATA_DIR / "api_responses" / "task_logs.json"
    api_data = load_json(api_file)

    print(f"  DAG ID:             {api_data['dag_id']}")
    print(f"  Run ID:             {api_data['dag_run_id']}")
    print()
    print("  Task Instances:")

    for task in api_data["task_instances"]:
        state_icon = "[OK]" if task["state"] == "success" else "[FAIL]"
        print(f"    {state_icon} {task['task_id']}")
        print(f"        State:    {task['state']}")
        print(f"        Attempts: {task['try_number']}/{task['max_tries']}")
        print(f"        Duration: {task['duration']}s")

    return api_data


def step6_analyze_failure() -> dict:
    """Step 6: Analyze the failure and identify root cause."""
    print_step(6, "Analyzing Failure")

    s3_logs = step4_retrieve_s3_logs.__wrapped__ if hasattr(step4_retrieve_s3_logs, '__wrapped__') else None

    # Read the failed attempt log
    log1_path = MOCK_DATA_DIR / "s3" / "logs" / "etl_sales_daily" / "extract_data" / "2024-01-15T10:00:00+00:00" / "1.log"
    log1_content = load_text(log1_path)

    print("  Failure Analysis:")
    print()
    print("  Task:               extract_data")
    print("  Failed Attempt:     1 of 2")
    print("  Error Type:         psycopg2.OperationalError")
    print("  Root Cause:         Database connection timeout")
    print()
    print("  Error Details:")
    print("  ----------------")

    # Extract error lines
    for line in log1_content.split("\n"):
        if "ERROR" in line or "Traceback" in line or "psycopg2" in line:
            print(f"  {line[:70]}...")
            break

    print()
    print("  Timeline:")
    print("    10:00:00 - Task started (attempt 1)")
    print("    10:00:32 - Connection timeout after 30s")
    print("    10:00:45 - Task marked as FAILED, scheduled retry")
    print("    10:05:00 - Retry started (attempt 2)")
    print("    10:05:55 - Task completed successfully")

    return {
        "task": "extract_data",
        "error_type": "psycopg2.OperationalError",
        "root_cause": "Database connection timeout (transient)",
        "resolution": "Automatic retry succeeded",
        "action_needed": "Monitor database connectivity"
    }


def step7_summarize_findings(analysis: dict) -> None:
    """Step 7: Summarize investigation findings."""
    print_step(7, "Investigation Summary")

    print("""
  INVESTIGATION COMPLETE
  ======================

  Environment:        Amazon MWAA (prod-data-pipeline)
  DAG:                etl_sales_daily
  Task:               extract_data

  Issue:              Transient database connection timeout
  Impact:             Task failed on first attempt
  Resolution:         Automatic retry succeeded (attempt 2)

  Log Sources Used:
    [x] CloudWatch    - Primary source, full logs available
    [x] S3            - Backup source, logs also available
    [x] REST API      - Metadata and state information

  Recommendation:
    - Monitor database connection pool health
    - Consider increasing connection timeout for large queries
    - Current retry configuration (2 attempts) is adequate

  Conclusion:
    No immediate action required. The built-in retry mechanism
    handled the transient failure successfully. Consider adding
    CloudWatch alarms for repeated connection timeouts.
""")


def main():
    """Main entry point for the demo."""
    print_header("AIRFLOW LOGS INVESTIGATION DEMO")
    print(f"\nDemo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mock data directory: {MOCK_DATA_DIR}")

    # Execute investigation steps
    env = step1_identify_environment()
    logging_config = step2_check_logging_config(env)
    cloudwatch_events = step3_retrieve_cloudwatch_logs()
    s3_logs = step4_retrieve_s3_logs()
    api_data = step5_retrieve_api_logs()
    analysis = step6_analyze_failure()
    step7_summarize_findings(analysis)

    print("\n" + "=" * 60)
    print("  Demo completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
