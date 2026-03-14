#!/usr/bin/env python3
"""
Fetch Airflow Task Logs from CloudWatch

This script retrieves task logs from CloudWatch Logs for Amazon MWAA
or any Airflow deployment that ships logs to CloudWatch.

Usage:
    python fetch_cloudwatch_logs.py --log-group airflow-prod-Task --dag-id my_dag --task-id my_task --run-id scheduled__2024-01-15T10:00:00+00:00

Requirements:
    - boto3
    - AWS credentials configured (via environment, ~/.aws/credentials, or IAM role)
"""

import argparse
import sys
from datetime import datetime, timedelta

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("Error: boto3 is required. Install with: pip install boto3")
    sys.exit(1)


def get_cloudwatch_client(region: str = "us-east-1"):
    """Create a CloudWatch Logs client."""
    return boto3.client("logs", region_name=region)


def list_log_groups(client, prefix: str = "airflow") -> list:
    """List CloudWatch log groups matching a prefix."""
    log_groups = []
    paginator = client.get_paginator("describe_log_groups")

    for page in paginator.paginate(logGroupNamePrefix=prefix):
        for group in page.get("logGroups", []):
            log_groups.append(group["logGroupName"])

    return log_groups


def find_log_stream(client, log_group: str, dag_id: str, task_id: str, run_id: str, attempt: int = None) -> str:
    """Find the log stream for a specific task instance."""
    # MWAA log stream naming convention:
    # {dag_id}/{task_id}/{run_id}/{attempt_number}
    prefix = f"{dag_id}/{task_id}/{run_id}"

    if attempt:
        prefix = f"{prefix}/{attempt}"

    try:
        response = client.describe_log_streams(
            logGroupName=log_group,
            logStreamNamePrefix=prefix,
            orderBy="LastEventTime",
            descending=True,
            limit=10
        )

        streams = response.get("logStreams", [])
        if streams:
            return streams[0]["logStreamName"]

    except ClientError as e:
        print(f"Error finding log stream: {e}")

    return None


def get_log_events(client, log_group: str, log_stream: str, start_time: datetime = None, end_time: datetime = None) -> list:
    """Retrieve log events from a specific stream."""
    kwargs = {
        "logGroupName": log_group,
        "logStreamName": log_stream,
        "startFromHead": True
    }

    if start_time:
        kwargs["startTime"] = int(start_time.timestamp() * 1000)
    if end_time:
        kwargs["endTime"] = int(end_time.timestamp() * 1000)

    events = []
    next_token = None

    while True:
        if next_token:
            kwargs["nextToken"] = next_token

        try:
            response = client.get_log_events(**kwargs)
            events.extend(response.get("events", []))

            # Check if there are more events
            new_token = response.get("nextForwardToken")
            if new_token == next_token:
                break
            next_token = new_token

        except ClientError as e:
            print(f"Error retrieving events: {e}")
            break

    return events


def format_timestamp(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to readable format."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Airflow task logs from CloudWatch"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--log-group",
        required=True,
        help="CloudWatch log group name"
    )
    parser.add_argument(
        "--dag-id",
        required=True,
        help="Airflow DAG ID"
    )
    parser.add_argument(
        "--task-id",
        required=True,
        help="Airflow Task ID"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Airflow Run ID (e.g., scheduled__2024-01-15T10:00:00+00:00)"
    )
    parser.add_argument(
        "--attempt",
        type=int,
        help="Specific attempt number (optional, gets latest if not specified)"
    )
    parser.add_argument(
        "--list-groups",
        action="store_true",
        help="List available log groups and exit"
    )
    parser.add_argument(
        "--output",
        help="Output file (default: print to stdout)"
    )

    args = parser.parse_args()

    # Initialize client
    client = get_cloudwatch_client(args.region)

    # List groups mode
    if args.list_groups:
        print("Available log groups:")
        for group in list_log_groups(client):
            print(f"  - {group}")
        return

    # Find log stream
    print(f"Searching for log stream...")
    print(f"  Log Group: {args.log_group}")
    print(f"  DAG ID:    {args.dag_id}")
    print(f"  Task ID:   {args.task_id}")
    print(f"  Run ID:    {args.run_id}")

    log_stream = find_log_stream(
        client,
        args.log_group,
        args.dag_id,
        args.task_id,
        args.run_id,
        args.attempt
    )

    if not log_stream:
        print("\nNo matching log stream found.")
        return

    print(f"\nFound stream: {log_stream}")

    # Retrieve events
    print("Retrieving log events...")
    events = get_log_events(client, args.log_group, log_stream)

    if not events:
        print("No log events found.")
        return

    print(f"Retrieved {len(events)} events\n")

    # Format output
    output_lines = []
    for event in events:
        timestamp = format_timestamp(event["timestamp"])
        message = event["message"]
        output_lines.append(f"[{timestamp}] {message}")

    output_text = "\n".join(output_lines)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Logs written to: {args.output}")
    else:
        print("-" * 60)
        print(output_text)
        print("-" * 60)


if __name__ == "__main__":
    main()
