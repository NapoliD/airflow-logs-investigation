#!/usr/bin/env python3
"""
Fetch Airflow Task Logs from S3

This script retrieves task logs from S3 when Airflow is configured
with remote_logging=True and remote_base_log_folder=s3://...

Usage:
    python fetch_s3_logs.py --bucket my-airflow-bucket --prefix logs/ --dag-id my_dag --task-id my_task --run-id scheduled__2024-01-15T10:00:00+00:00

Requirements:
    - boto3
    - AWS credentials configured (via environment, ~/.aws/credentials, or IAM role)
"""

import argparse
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("Error: boto3 is required. Install with: pip install boto3")
    sys.exit(1)


def get_s3_client(region: str = "us-east-1"):
    """Create an S3 client."""
    return boto3.client("s3", region_name=region)


def list_log_files(client, bucket: str, prefix: str, dag_id: str, task_id: str, run_id: str) -> list:
    """List log files for a specific task instance."""
    # Airflow S3 log path convention:
    # {prefix}/{dag_id}/{task_id}/{run_id}/{attempt}.log
    full_prefix = f"{prefix.rstrip('/')}/{dag_id}/{task_id}/{run_id}/"

    log_files = []

    try:
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=full_prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".log"):
                    log_files.append({
                        "key": key,
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "attempt": Path(key).stem
                    })

    except ClientError as e:
        print(f"Error listing objects: {e}")

    return sorted(log_files, key=lambda x: x["key"])


def get_log_content(client, bucket: str, key: str) -> str:
    """Download and return log file content."""
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read().decode("utf-8")
    except ClientError as e:
        print(f"Error downloading log: {e}")
        return None


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Airflow task logs from S3"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="S3 bucket name"
    )
    parser.add_argument(
        "--prefix",
        default="logs/",
        help="S3 prefix for logs (default: logs/)"
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
        help="Specific attempt number (optional, shows all if not specified)"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list available log files, don't download"
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to save log files (default: print to stdout)"
    )

    args = parser.parse_args()

    # Initialize client
    client = get_s3_client(args.region)

    # Find log files
    print(f"Searching for log files...")
    print(f"  Bucket:    s3://{args.bucket}")
    print(f"  Prefix:    {args.prefix}")
    print(f"  DAG ID:    {args.dag_id}")
    print(f"  Task ID:   {args.task_id}")
    print(f"  Run ID:    {args.run_id}")

    log_files = list_log_files(
        client,
        args.bucket,
        args.prefix,
        args.dag_id,
        args.task_id,
        args.run_id
    )

    if not log_files:
        print("\nNo log files found.")
        return

    # Filter by attempt if specified
    if args.attempt:
        log_files = [f for f in log_files if f["attempt"] == str(args.attempt)]

    print(f"\nFound {len(log_files)} log file(s):\n")

    for lf in log_files:
        print(f"  Attempt {lf['attempt']}:")
        print(f"    Key:      {lf['key']}")
        print(f"    Size:     {format_size(lf['size'])}")
        print(f"    Modified: {lf['last_modified']}")
        print()

    if args.list_only:
        return

    # Download and display/save logs
    for lf in log_files:
        print(f"Downloading: {lf['key']}")
        content = get_log_content(client, args.bucket, lf["key"])

        if content is None:
            continue

        if args.output_dir:
            output_path = Path(args.output_dir) / f"attempt_{lf['attempt']}.log"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(content)
            print(f"  Saved to: {output_path}")
        else:
            print(f"\n{'=' * 60}")
            print(f"ATTEMPT {lf['attempt']}")
            print("=" * 60)
            print(content)
            print("=" * 60)


if __name__ == "__main__":
    main()
