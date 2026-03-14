"""
Airflow API Tools

Tools for querying the Airflow REST API to get task metadata,
DAG run information, and execution states.
"""

import json
from pathlib import Path
from typing import Optional, List

from langchain_core.tools import tool


MOCK_DATA_DIR = Path(__file__).parent.parent.parent / "mock_data"


@tool
def get_dag_runs(dag_id: str, limit: int = 10) -> str:
    """
    Get recent DAG runs for a specific DAG.

    Args:
        dag_id: The DAG ID to query
        limit: Maximum number of runs to return (default: 10)

    Returns:
        List of DAG runs with their states, start times, and end times.

    Use this tool to see the execution history of a DAG and identify failed runs.
    """
    api_file = MOCK_DATA_DIR / "api_responses" / "task_logs.json"

    if not api_file.exists():
        return "API data not available."

    with open(api_file) as f:
        api_data = json.load(f)

    if api_data.get("dag_id") != dag_id:
        return f"No data found for dag_id={dag_id}"

    runs = api_data.get("dag_runs", [])

    if not runs:
        return f"No runs found for dag_id={dag_id}"

    result = f"DAG Runs for '{dag_id}':\n\n"

    for run in runs[:limit]:
        state_icon = "✓" if run["state"] == "success" else "✗" if run["state"] == "failed" else "○"
        result += f"{state_icon} Run ID: {run['dag_run_id']}\n"
        result += f"  State: {run['state']}\n"
        result += f"  Start: {run.get('start_date', 'N/A')}\n"
        result += f"  End: {run.get('end_date', 'N/A')}\n"
        result += f"  Type: {run.get('run_type', 'N/A')}\n\n"

    return result


@tool
def get_task_instances(dag_id: str, run_id: str) -> str:
    """
    Get all task instances for a specific DAG run.

    Args:
        dag_id: The DAG ID
        run_id: The specific run ID to query

    Returns:
        List of task instances with their states, attempt counts, and durations.

    Use this tool to see which tasks succeeded or failed in a DAG run.
    """
    api_file = MOCK_DATA_DIR / "api_responses" / "task_logs.json"

    if not api_file.exists():
        return "API data not available."

    with open(api_file) as f:
        api_data = json.load(f)

    if api_data.get("dag_id") != dag_id:
        return f"No data found for dag_id={dag_id}"

    if api_data.get("dag_run_id") != run_id:
        return f"No data found for run_id={run_id}"

    tasks = api_data.get("task_instances", [])

    if not tasks:
        return f"No task instances found for dag_id={dag_id}, run_id={run_id}"

    result = f"Task Instances for '{dag_id}' / '{run_id}':\n\n"

    for task in tasks:
        state = task.get("state", "unknown")
        state_icon = "✓" if state == "success" else "✗" if state == "failed" else "○"

        result += f"{state_icon} Task: {task['task_id']}\n"
        result += f"  State: {state}\n"
        result += f"  Attempts: {task.get('try_number', '?')}/{task.get('max_tries', '?')}\n"
        result += f"  Duration: {task.get('duration', 'N/A')}s\n"
        result += f"  Operator: {task.get('operator', 'N/A')}\n"
        result += f"  Start: {task.get('start_date', 'N/A')}\n"
        result += f"  End: {task.get('end_date', 'N/A')}\n\n"

    return result


@tool
def get_task_status(dag_id: str, task_id: str, run_id: Optional[str] = None) -> str:
    """
    Get the current status of a specific task.

    Args:
        dag_id: The DAG ID
        task_id: The task ID to check
        run_id: Optional specific run ID (uses latest if not provided)

    Returns:
        Detailed task status including state, attempts, timing, and execution details.

    Use this tool to get detailed information about a specific task's execution.
    """
    api_file = MOCK_DATA_DIR / "api_responses" / "task_logs.json"

    if not api_file.exists():
        return "API data not available."

    with open(api_file) as f:
        api_data = json.load(f)

    if api_data.get("dag_id") != dag_id:
        return f"No data found for dag_id={dag_id}"

    tasks = api_data.get("task_instances", [])
    matching_task = None

    for task in tasks:
        if task.get("task_id") == task_id:
            matching_task = task
            break

    if not matching_task:
        return f"No task found with task_id={task_id}"

    state = matching_task.get("state", "unknown")
    attempts = matching_task.get("try_number", 1)
    max_tries = matching_task.get("max_tries", 1)

    result = f"Task Status Report\n"
    result += f"{'='*40}\n\n"
    result += f"DAG ID: {dag_id}\n"
    result += f"Task ID: {task_id}\n"
    result += f"Run ID: {api_data.get('dag_run_id', 'N/A')}\n\n"

    result += f"Current State: {state.upper()}\n"
    result += f"Attempts: {attempts} of {max_tries}\n"

    if attempts > 1:
        result += f"Note: Task required {attempts} attempts to complete\n"

    result += f"\nTiming:\n"
    result += f"  Started: {matching_task.get('start_date', 'N/A')}\n"
    result += f"  Ended: {matching_task.get('end_date', 'N/A')}\n"
    result += f"  Duration: {matching_task.get('duration', 'N/A')} seconds\n"

    result += f"\nExecution Details:\n"
    result += f"  Operator: {matching_task.get('operator', 'N/A')}\n"
    result += f"  Hostname: {matching_task.get('hostname', 'N/A')}\n"
    result += f"  Pool: {matching_task.get('pool', 'N/A')}\n"
    result += f"  Queue: {matching_task.get('queue', 'N/A')}\n"

    return result
