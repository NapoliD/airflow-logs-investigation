"""
Log Analysis Tools

Tools for analyzing log content, extracting errors, and identifying patterns.
"""

import re
from typing import List, Dict, Any

from langchain_core.tools import tool


@tool
def extract_errors(log_content: str) -> str:
    """
    Extract all error messages and exceptions from log content.

    Args:
        log_content: The raw log text to analyze

    Returns:
        A structured list of errors found, including error types, messages, and line numbers.

    Use this tool to quickly identify all errors in a log without reading the entire content.
    """
    errors = []
    lines = log_content.split('\n')

    error_patterns = [
        r'ERROR',
        r'Exception',
        r'Error:',
        r'FAILED',
        r'Traceback',
        r'raise \w+Error',
    ]

    combined_pattern = '|'.join(error_patterns)

    in_traceback = False
    traceback_lines = []

    for i, line in enumerate(lines, 1):
        # Detect start of traceback
        if 'Traceback (most recent call last)' in line:
            in_traceback = True
            traceback_lines = [f"Line {i}: {line}"]
            continue

        # Continue collecting traceback
        if in_traceback:
            traceback_lines.append(f"Line {i}: {line}")
            # End of traceback (exception line)
            if re.match(r'^\w+Error:|^\w+Exception:', line.strip()):
                errors.append({
                    "type": "traceback",
                    "lines": traceback_lines,
                    "exception": line.strip()
                })
                in_traceback = False
                traceback_lines = []
            continue

        # Check for error patterns
        if re.search(combined_pattern, line, re.IGNORECASE):
            errors.append({
                "type": "error_line",
                "line_number": i,
                "content": line.strip()
            })

    if not errors:
        return "No errors found in the log content."

    result = f"Found {len(errors)} error(s):\n\n"

    for i, error in enumerate(errors, 1):
        if error["type"] == "traceback":
            result += f"--- Error #{i}: Stack Trace ---\n"
            result += f"Exception: {error['exception']}\n"
            result += "Trace:\n"
            for line in error["lines"][:10]:  # Limit traceback lines
                result += f"  {line}\n"
            if len(error["lines"]) > 10:
                result += f"  ... ({len(error['lines']) - 10} more lines)\n"
            result += "\n"
        else:
            result += f"--- Error #{i}: Line {error['line_number']} ---\n"
            result += f"{error['content']}\n\n"

    return result


@tool
def analyze_stack_trace(stack_trace: str) -> str:
    """
    Analyze a Python stack trace and extract key information.

    Args:
        stack_trace: The stack trace text to analyze

    Returns:
        Analysis including: root cause, affected files, suggested fixes.

    Use this tool to understand complex stack traces and get actionable insights.
    """
    analysis = {
        "exception_type": None,
        "exception_message": None,
        "affected_files": [],
        "root_cause_file": None,
        "root_cause_line": None,
        "suggested_category": None
    }

    lines = stack_trace.strip().split('\n')

    # Find exception type and message (usually last line)
    for line in reversed(lines):
        match = re.match(r'^(\w+(?:Error|Exception)):\s*(.+)?$', line.strip())
        if match:
            analysis["exception_type"] = match.group(1)
            analysis["exception_message"] = match.group(2) or "No message"
            break

    # Extract file references
    file_pattern = r'File "([^"]+)", line (\d+)'
    for match in re.finditer(file_pattern, stack_trace):
        file_path = match.group(1)
        line_num = match.group(2)
        analysis["affected_files"].append({"file": file_path, "line": line_num})

    # The last file in the trace is usually the root cause
    if analysis["affected_files"]:
        root = analysis["affected_files"][-1]
        analysis["root_cause_file"] = root["file"]
        analysis["root_cause_line"] = root["line"]

    # Categorize the error
    exception_type = analysis["exception_type"] or ""
    if "Connection" in exception_type or "Timeout" in exception_type:
        analysis["suggested_category"] = "Network/Connection Issue"
    elif "Permission" in exception_type or "Access" in exception_type:
        analysis["suggested_category"] = "Permission/Access Issue"
    elif "Key" in exception_type or "Index" in exception_type:
        analysis["suggested_category"] = "Data Structure Issue"
    elif "Type" in exception_type or "Attribute" in exception_type:
        analysis["suggested_category"] = "Type/Attribute Issue"
    elif "Value" in exception_type:
        analysis["suggested_category"] = "Invalid Value Issue"
    elif "Import" in exception_type or "Module" in exception_type:
        analysis["suggested_category"] = "Import/Module Issue"
    else:
        analysis["suggested_category"] = "General Runtime Error"

    # Format output
    result = "Stack Trace Analysis\n"
    result += "=" * 40 + "\n\n"

    result += f"Exception Type: {analysis['exception_type'] or 'Unknown'}\n"
    result += f"Message: {analysis['exception_message'] or 'None'}\n"
    result += f"Category: {analysis['suggested_category']}\n\n"

    if analysis["root_cause_file"]:
        result += f"Root Cause Location:\n"
        result += f"  File: {analysis['root_cause_file']}\n"
        result += f"  Line: {analysis['root_cause_line']}\n\n"

    if analysis["affected_files"]:
        result += f"Call Stack ({len(analysis['affected_files'])} frames):\n"
        for f in analysis["affected_files"]:
            result += f"  → {f['file']}:{f['line']}\n"

    return result


@tool
def get_error_summary(log_content: str) -> str:
    """
    Generate a concise summary of errors in the log.

    Args:
        log_content: The raw log text to summarize

    Returns:
        A brief summary including: error count, types, severity, and recommended actions.

    Use this tool to get a quick overview of log health without detailed analysis.
    """
    error_count = 0
    warning_count = 0
    error_types = set()
    has_traceback = False
    has_timeout = False
    has_connection_error = False
    has_permission_error = False

    lines = log_content.split('\n')

    for line in lines:
        line_lower = line.lower()

        if 'error' in line_lower:
            error_count += 1
        if 'warning' in line_lower or 'warn' in line_lower:
            warning_count += 1
        if 'traceback' in line_lower:
            has_traceback = True
        if 'timeout' in line_lower:
            has_timeout = True
        if 'connection' in line_lower and ('error' in line_lower or 'failed' in line_lower):
            has_connection_error = True
        if 'permission' in line_lower or 'access denied' in line_lower:
            has_permission_error = True

        # Extract exception types
        match = re.search(r'(\w+(?:Error|Exception))', line)
        if match:
            error_types.add(match.group(1))

    # Determine severity
    if error_count > 5 or has_permission_error:
        severity = "HIGH"
    elif error_count > 0 or has_traceback:
        severity = "MEDIUM"
    elif warning_count > 0:
        severity = "LOW"
    else:
        severity = "NONE"

    # Build summary
    result = "Log Summary\n"
    result += "=" * 40 + "\n\n"

    result += f"Severity: {severity}\n"
    result += f"Errors: {error_count}\n"
    result += f"Warnings: {warning_count}\n\n"

    if error_types:
        result += f"Exception Types Found:\n"
        for et in sorted(error_types):
            result += f"  • {et}\n"
        result += "\n"

    result += "Issues Detected:\n"
    if has_traceback:
        result += "  ⚠ Stack trace present - exception occurred\n"
    if has_timeout:
        result += "  ⚠ Timeout detected - possible performance/network issue\n"
    if has_connection_error:
        result += "  ⚠ Connection error - check network/database connectivity\n"
    if has_permission_error:
        result += "  ⚠ Permission error - check IAM/access policies\n"
    if not any([has_traceback, has_timeout, has_connection_error, has_permission_error]):
        result += "  ✓ No critical issues detected\n"

    result += "\nRecommended Actions:\n"
    if has_timeout:
        result += "  1. Check network latency and database load\n"
        result += "  2. Consider increasing timeout values\n"
    if has_connection_error:
        result += "  1. Verify database/service is running\n"
        result += "  2. Check security groups and network ACLs\n"
    if has_permission_error:
        result += "  1. Review IAM role permissions\n"
        result += "  2. Check resource policies\n"
    if has_traceback and not any([has_timeout, has_connection_error, has_permission_error]):
        result += "  1. Review stack trace for root cause\n"
        result += "  2. Check recent code changes\n"

    return result
