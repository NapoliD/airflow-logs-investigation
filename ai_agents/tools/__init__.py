"""
LangChain Tools for Airflow Log Investigation

These tools allow agents to:
- Search and retrieve logs from multiple sources
- Query Airflow API for task metadata
- Analyze log patterns and errors
"""

from .log_tools import (
    search_cloudwatch_logs,
    search_s3_logs,
    get_log_content,
    list_available_logs
)

from .api_tools import (
    get_dag_runs,
    get_task_instances,
    get_task_status
)

from .analysis_tools import (
    extract_errors,
    analyze_stack_trace,
    get_error_summary
)

__all__ = [
    "search_cloudwatch_logs",
    "search_s3_logs",
    "get_log_content",
    "list_available_logs",
    "get_dag_runs",
    "get_task_instances",
    "get_task_status",
    "extract_errors",
    "analyze_stack_trace",
    "get_error_summary"
]
