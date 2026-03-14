"""
Log Retrieval Tools

Tools for searching and retrieving Airflow logs from various sources.
These tools work with mock data for demo purposes but can be adapted
for real AWS environments.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from langchain_core.tools import tool


# Path to mock data (relative to this file)
MOCK_DATA_DIR = Path(__file__).parent.parent.parent / "mock_data"


@tool
def list_available_logs(dag_id: Optional[str] = None) -> str:
    """
    List all available log files in the system.

    Args:
        dag_id: Optional DAG ID to filter logs. If not provided, lists all logs.

    Returns:
        A formatted string listing available log files with their paths and metadata.

    Use this tool first to discover what logs are available before retrieving them.
    """
    logs_found = []

    # Check CloudWatch logs
    cw_file = MOCK_DATA_DIR / "cloudwatch" / "sample_logs.json"
    if cw_file.exists():
        with open(cw_file) as f:
            cw_data = json.load(f)
            for stream in cw_data.get("logStreams", []):
                stream_name = stream["logStreamName"]
                if dag_id is None or dag_id in stream_name:
                    logs_found.append({
                        "source": "CloudWatch",
                        "path": stream_name,
                        "log_group": cw_data.get("logGroupName", "unknown")
                    })

    # Check S3 logs
    s3_base = MOCK_DATA_DIR / "s3" / "logs"
    if s3_base.exists():
        for log_file in s3_base.rglob("*.log"):
            rel_path = log_file.relative_to(s3_base)
            if dag_id is None or dag_id in str(rel_path):
                logs_found.append({
                    "source": "S3",
                    "path": str(rel_path),
                    "size_bytes": log_file.stat().st_size
                })

    if not logs_found:
        return "No logs found matching the criteria."

    result = f"Found {len(logs_found)} log sources:\n\n"
    for log in logs_found:
        result += f"- [{log['source']}] {log['path']}\n"

    return result


@tool
def search_cloudwatch_logs(
    dag_id: str,
    task_id: Optional[str] = None,
    search_term: Optional[str] = None
) -> str:
    """
    Search CloudWatch logs for a specific DAG and optionally filter by task or search term.

    Args:
        dag_id: The DAG ID to search logs for (required)
        task_id: Optional task ID to filter results
        search_term: Optional term to search for in log messages (e.g., "ERROR", "timeout")

    Returns:
        Matching log events with timestamps and messages.

    Use this tool to find specific errors or events in CloudWatch logs.
    """
    cw_file = MOCK_DATA_DIR / "cloudwatch" / "sample_logs.json"

    if not cw_file.exists():
        return "CloudWatch logs not available."

    with open(cw_file) as f:
        cw_data = json.load(f)

    matching_events = []

    for event in cw_data.get("events", []):
        stream_name = event.get("logStreamName", "")

        # Filter by DAG ID
        if dag_id not in stream_name:
            continue

        # Filter by task ID if provided
        if task_id and task_id not in stream_name:
            continue

        message = event.get("message", "")

        # Filter by search term if provided
        if search_term and search_term.lower() not in message.lower():
            continue

        matching_events.append({
            "stream": stream_name,
            "timestamp": event.get("timestamp"),
            "message": message
        })

    if not matching_events:
        return f"No logs found for dag_id={dag_id}" + (f", task_id={task_id}" if task_id else "") + (f", containing '{search_term}'" if search_term else "")

    result = f"Found {len(matching_events)} matching events:\n\n"
    for event in matching_events[:20]:  # Limit to 20 events
        result += f"[{event['stream']}]\n{event['message']}\n\n"

    if len(matching_events) > 20:
        result += f"\n... and {len(matching_events) - 20} more events"

    return result


@tool
def search_s3_logs(
    dag_id: str,
    task_id: str,
    attempt: Optional[int] = None
) -> str:
    """
    Search S3 logs for a specific DAG and task.

    Args:
        dag_id: The DAG ID (required)
        task_id: The task ID (required)
        attempt: Optional specific attempt number (1, 2, etc.)

    Returns:
        Log file contents from S3.

    Use this tool to retrieve full task execution logs from S3 storage.
    """
    s3_base = MOCK_DATA_DIR / "s3" / "logs" / dag_id / task_id

    if not s3_base.exists():
        return f"No S3 logs found for dag_id={dag_id}, task_id={task_id}"

    # Find all run directories
    run_dirs = [d for d in s3_base.iterdir() if d.is_dir()]

    if not run_dirs:
        return f"No run directories found for dag_id={dag_id}, task_id={task_id}"

    results = []

    for run_dir in run_dirs:
        log_files = sorted(run_dir.glob("*.log"))

        for log_file in log_files:
            attempt_num = int(log_file.stem)

            if attempt and attempt_num != attempt:
                continue

            content = log_file.read_text()
            results.append({
                "run_id": run_dir.name,
                "attempt": attempt_num,
                "content": content
            })

    if not results:
        return f"No log files found" + (f" for attempt {attempt}" if attempt else "")

    output = ""
    for r in results:
        output += f"=== Run: {r['run_id']} | Attempt: {r['attempt']} ===\n"
        output += r['content']
        output += "\n\n"

    return output


@tool
def get_log_content(source: str, path: str) -> str:
    """
    Get the full content of a specific log file.

    Args:
        source: Log source - either "cloudwatch" or "s3"
        path: Path to the log (stream name for CloudWatch, file path for S3)

    Returns:
        Full log content.

    Use this tool when you need to read the complete contents of a specific log.
    """
    if source.lower() == "cloudwatch":
        cw_file = MOCK_DATA_DIR / "cloudwatch" / "sample_logs.json"

        if not cw_file.exists():
            return "CloudWatch logs not available."

        with open(cw_file) as f:
            cw_data = json.load(f)

        events = [e for e in cw_data.get("events", []) if e.get("logStreamName") == path]

        if not events:
            return f"No events found for stream: {path}"

        return "\n".join([e.get("message", "") for e in events])

    elif source.lower() == "s3":
        log_file = MOCK_DATA_DIR / "s3" / "logs" / path

        if not log_file.exists():
            return f"S3 log file not found: {path}"

        return log_file.read_text()

    else:
        return f"Unknown source: {source}. Use 'cloudwatch' or 's3'."
