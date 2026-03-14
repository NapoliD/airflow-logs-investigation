#!/usr/bin/env python3
"""
Fetch Airflow Task Logs via REST API

This script retrieves task instance information and logs from
the Airflow REST API. Works with MWAA and self-hosted Airflow.

Usage:
    # For MWAA (uses AWS IAM authentication)
    python fetch_api_logs.py --mwaa-env prod-data-pipeline --dag-id my_dag --task-id my_task --run-id scheduled__2024-01-15T10:00:00+00:00

    # For self-hosted Airflow (uses basic auth)
    python fetch_api_logs.py --base-url http://localhost:8080 --username admin --password admin --dag-id my_dag --task-id my_task --run-id scheduled__2024-01-15T10:00:00+00:00

Requirements:
    - requests
    - boto3 (for MWAA authentication)
"""

import argparse
import base64
import json
import sys
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)


def get_mwaa_token(environment_name: str, region: str = "us-east-1") -> tuple:
    """Get MWAA web login token and hostname."""
    try:
        import boto3
    except ImportError:
        print("Error: boto3 is required for MWAA. Install with: pip install boto3")
        sys.exit(1)

    client = boto3.client("mwaa", region_name=region)

    response = client.create_web_login_token(Name=environment_name)

    web_server_hostname = response["WebServerHostname"]
    web_token = response["WebToken"]

    return f"https://{web_server_hostname}", web_token


def get_session_for_mwaa(base_url: str, web_token: str) -> requests.Session:
    """Create authenticated session for MWAA."""
    session = requests.Session()

    # Exchange web token for session cookie
    login_url = f"{base_url}/aws_mwaa/login"
    login_response = session.post(
        login_url,
        data={"token": web_token},
        allow_redirects=True
    )

    if login_response.status_code != 200:
        print(f"Warning: Login may have failed (status: {login_response.status_code})")

    return session


def get_session_for_basic_auth(username: str, password: str) -> requests.Session:
    """Create authenticated session with basic auth."""
    session = requests.Session()
    session.auth = (username, password)
    return session


def get_dag_runs(session: requests.Session, base_url: str, dag_id: str, limit: int = 10) -> list:
    """Get recent DAG runs."""
    url = urljoin(base_url, f"/api/v1/dags/{dag_id}/dagRuns")

    response = session.get(url, params={"limit": limit, "order_by": "-execution_date"})
    response.raise_for_status()

    return response.json().get("dag_runs", [])


def get_task_instances(session: requests.Session, base_url: str, dag_id: str, run_id: str) -> list:
    """Get task instances for a DAG run."""
    url = urljoin(base_url, f"/api/v1/dags/{dag_id}/dagRuns/{run_id}/taskInstances")

    response = session.get(url)
    response.raise_for_status()

    return response.json().get("task_instances", [])


def get_task_logs(session: requests.Session, base_url: str, dag_id: str, run_id: str, task_id: str, try_number: int = 1) -> str:
    """Get logs for a specific task instance attempt."""
    url = urljoin(
        base_url,
        f"/api/v1/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs/{try_number}"
    )

    response = session.get(url)
    response.raise_for_status()

    return response.text


def format_state(state: str) -> str:
    """Format task state with indicator."""
    indicators = {
        "success": "[OK]",
        "failed": "[FAIL]",
        "running": "[RUN]",
        "queued": "[WAIT]",
        "upstream_failed": "[SKIP]",
        "skipped": "[SKIP]"
    }
    return indicators.get(state, f"[{state.upper()}]")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Airflow task information and logs via REST API"
    )

    # Connection options
    conn_group = parser.add_mutually_exclusive_group(required=True)
    conn_group.add_argument(
        "--mwaa-env",
        help="MWAA environment name (uses AWS IAM auth)"
    )
    conn_group.add_argument(
        "--base-url",
        help="Airflow webserver base URL (for non-MWAA)"
    )

    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region for MWAA (default: us-east-1)"
    )
    parser.add_argument(
        "--username",
        help="Username for basic auth (non-MWAA)"
    )
    parser.add_argument(
        "--password",
        help="Password for basic auth (non-MWAA)"
    )

    # Query options
    parser.add_argument(
        "--dag-id",
        required=True,
        help="Airflow DAG ID"
    )
    parser.add_argument(
        "--run-id",
        help="Specific DAG Run ID (optional, lists recent runs if not specified)"
    )
    parser.add_argument(
        "--task-id",
        help="Specific Task ID (optional, lists all tasks if not specified)"
    )
    parser.add_argument(
        "--attempt",
        type=int,
        default=1,
        help="Task attempt number (default: 1)"
    )

    # Output options
    parser.add_argument(
        "--list-runs",
        action="store_true",
        help="List recent DAG runs and exit"
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List task instances and exit"
    )
    parser.add_argument(
        "--output",
        help="Output file for logs"
    )

    args = parser.parse_args()

    # Setup authentication
    if args.mwaa_env:
        print(f"Connecting to MWAA environment: {args.mwaa_env}")
        base_url, web_token = get_mwaa_token(args.mwaa_env, args.region)
        session = get_session_for_mwaa(base_url, web_token)
        print(f"  Base URL: {base_url}")
    else:
        if not args.username or not args.password:
            print("Error: --username and --password required for non-MWAA connections")
            sys.exit(1)
        base_url = args.base_url.rstrip("/")
        session = get_session_for_basic_auth(args.username, args.password)
        print(f"Connecting to: {base_url}")

    # List DAG runs
    if args.list_runs or not args.run_id:
        print(f"\nRecent runs for DAG '{args.dag_id}':\n")
        runs = get_dag_runs(session, base_url, args.dag_id)

        for run in runs:
            state = format_state(run["state"])
            print(f"  {state} {run['dag_run_id']}")
            print(f"       State:      {run['state']}")
            print(f"       Start:      {run.get('start_date', 'N/A')}")
            print(f"       End:        {run.get('end_date', 'N/A')}")
            print()

        if args.list_runs:
            return

        if not args.run_id:
            print("Specify --run-id to see task details")
            return

    # List task instances
    print(f"\nTask instances for run '{args.run_id}':\n")
    tasks = get_task_instances(session, base_url, args.dag_id, args.run_id)

    for task in tasks:
        state = format_state(task["state"])
        print(f"  {state} {task['task_id']}")
        print(f"       State:    {task['state']}")
        print(f"       Attempts: {task['try_number']}/{task.get('max_tries', 'N/A')}")
        print(f"       Duration: {task.get('duration', 'N/A')}s")
        print()

    if args.list_tasks or not args.task_id:
        if not args.task_id:
            print("Specify --task-id to fetch logs")
        return

    # Get task logs
    print(f"Fetching logs for task '{args.task_id}' (attempt {args.attempt})...")

    try:
        logs = get_task_logs(
            session,
            base_url,
            args.dag_id,
            args.run_id,
            args.task_id,
            args.attempt
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(logs)
            print(f"Logs written to: {args.output}")
        else:
            print("\n" + "=" * 60)
            print(logs)
            print("=" * 60)

    except requests.HTTPError as e:
        print(f"Error fetching logs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
