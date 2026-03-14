#!/usr/bin/env python3
"""
Visual Demo for GIF Recording

A visually appealing demo designed to be captured as a GIF.
Shows the AI agent investigating a failure with nice formatting.

Usage:
    python scripts/visual_demo.py

For recording:
    1. Use a tool like asciinema, terminalizer, or peek
    2. Run this script
    3. Convert to GIF

Example with asciinema:
    asciinema rec demo.cast
    python scripts/visual_demo.py
    # Press Ctrl+D when done
    # Convert: agg demo.cast demo.gif
"""

import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def type_text(text: str, delay: float = 0.03):
    """Simulate typing effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_slow(text: str, delay: float = 0.5):
    """Print with a pause."""
    print(text)
    time.sleep(delay)


def print_header():
    """Print the demo header."""
    header = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🔍 Airflow Logs Investigation Toolkit                   ║
    ║      AI-Powered Diagnostic Agents                         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(header)
    time.sleep(1)


def simulate_investigation():
    """Simulate an AI agent investigation."""

    print_header()

    # User question
    print(f"{Colors.YELLOW}You:{Colors.RESET} ", end='')
    type_text("The ETL pipeline failed this morning. What happened?", 0.04)
    print()
    time.sleep(0.5)

    # Agent thinking
    print(f"{Colors.CYAN}🤖 Agent:{Colors.RESET} Investigating...\n")
    time.sleep(0.3)

    # Tool calls
    tools = [
        ("🔎 Searching CloudWatch logs", "etl_sales_daily"),
        ("📂 Retrieving S3 logs", "extract_data/attempt_1"),
        ("🔌 Querying Airflow API", "task_instances"),
        ("⚠️  Extracting errors", "2 errors found"),
        ("📊 Analyzing stack trace", "psycopg2.OperationalError"),
    ]

    for tool, detail in tools:
        print(f"   {Colors.DIM}{tool}...{Colors.RESET} ", end='', flush=True)
        time.sleep(0.8)
        print(f"{Colors.GREEN}{detail}{Colors.RESET}")
        time.sleep(0.3)

    print()
    time.sleep(0.5)

    # Result
    result = f"""
{Colors.GREEN}{Colors.BOLD}✓ Investigation Complete{Colors.RESET}
{Colors.DIM}{'─' * 50}{Colors.RESET}

{Colors.BOLD}Root Cause:{Colors.RESET} Database connection timeout (transient)

{Colors.BOLD}What happened:{Colors.RESET}
  The {Colors.CYAN}extract_data{Colors.RESET} task failed on attempt 1 due to a
  connection timeout to {Colors.YELLOW}salesdb.acme-corp.internal:5432{Colors.RESET}
  after 30 seconds. The retry succeeded automatically.

{Colors.BOLD}Evidence:{Colors.RESET}
  {Colors.RED}✗{Colors.RESET} Attempt 1: psycopg2.OperationalError at 10:00:32
  {Colors.GREEN}✓{Colors.RESET} Attempt 2: Completed successfully at 10:05:55

{Colors.BOLD}Recommendation:{Colors.RESET}
  {Colors.DIM}1.{Colors.RESET} Monitor database connection pool health
  {Colors.DIM}2.{Colors.RESET} Consider increasing query timeout
  {Colors.DIM}3.{Colors.RESET} Current retry config handled this well ✓

{Colors.BOLD}Confidence:{Colors.RESET} {Colors.GREEN}High{Colors.RESET}

{Colors.DIM}{'─' * 50}{Colors.RESET}
{Colors.DIM}Tools used: search_cloudwatch_logs, search_s3_logs,
             get_task_status, extract_errors, analyze_stack_trace{Colors.RESET}
"""

    for line in result.split('\n'):
        print(line)
        time.sleep(0.1)

    print()
    time.sleep(1)

    # Footer
    print(f"{Colors.CYAN}🌐 napolidata.com{Colors.RESET}")
    print()


def main():
    try:
        simulate_investigation()
    except KeyboardInterrupt:
        print(f"\n{Colors.DIM}Demo interrupted{Colors.RESET}")


if __name__ == "__main__":
    main()
