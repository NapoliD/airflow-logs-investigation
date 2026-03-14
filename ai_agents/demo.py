#!/usr/bin/env python3
"""
AI Agents Demo

Interactive demonstration of the Airflow Log Investigation AI Agents.
Shows both the Diagnostic Agent and Multi-Tool Agent in action.

Usage:
    # Using Ollama (default)
    python -m ai_agents.demo

    # Using OpenAI
    LLM_PROVIDER=openai LLM_MODEL=gpt-4 python -m ai_agents.demo

    # Using Anthropic
    LLM_PROVIDER=anthropic python -m ai_agents.demo

    # Specific demo mode
    python -m ai_agents.demo --mode diagnostic
    python -m ai_agents.demo --mode multi-tool
    python -m ai_agents.demo --mode interactive
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agents.config import get_llm, check_ollama_available, list_ollama_models, LLMConfig
from ai_agents.agents.diagnostic_agent import DiagnosticAgent
from ai_agents.agents.multi_tool_agent import MultiToolAgent


MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_section(title: str) -> None:
    """Print a section divider."""
    print(f"\n--- {title} ---\n")


def check_llm_availability(provider: str, model: str) -> bool:
    """Check if the specified LLM is available."""
    if provider == "ollama":
        if not check_ollama_available():
            print("ERROR: Ollama is not running.")
            print("Please start Ollama with: ollama serve")
            print("Or use a cloud provider: --provider openai")
            return False

        available_models = list_ollama_models()
        if model not in available_models and f"{model}:latest" not in available_models:
            print(f"WARNING: Model '{model}' not found in Ollama.")
            print(f"Available models: {', '.join(available_models) or 'None'}")
            print(f"Pull the model with: ollama pull {model}")
            return False

    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY environment variable not set.")
            return False

    elif provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
            return False

    return True


def demo_diagnostic_agent(llm, verbose: bool = True) -> None:
    """Demonstrate the Diagnostic Agent."""
    print_header("DIAGNOSTIC AGENT DEMO")

    print("The Diagnostic Agent analyzes log content you provide")
    print("and generates detailed diagnoses with recommendations.\n")

    # Load sample log
    log_file = MOCK_DATA_DIR / "s3" / "logs" / "etl_sales_daily" / "extract_data" / "2024-01-15T10:00:00+00:00" / "1.log"

    if not log_file.exists():
        print(f"ERROR: Sample log not found at {log_file}")
        return

    log_content = log_file.read_text()

    print("Sample log content (first 500 chars):")
    print("-" * 40)
    print(log_content[:500])
    print("-" * 40)

    print("\nInitializing Diagnostic Agent...")
    agent = DiagnosticAgent(llm=llm, verbose=verbose)

    print("\nAnalyzing log...")
    print_section("DIAGNOSIS")

    result = agent.diagnose(
        dag_id="etl_sales_daily",
        task_id="extract_data",
        run_id="scheduled__2024-01-15T10:00:00+00:00",
        attempt=1,
        log_content=log_content
    )

    print(result.diagnosis)

    # Demonstrate compare_attempts
    print_section("COMPARING FAILED VS SUCCESS")

    success_log_file = MOCK_DATA_DIR / "s3" / "logs" / "etl_sales_daily" / "extract_data" / "2024-01-15T10:00:00+00:00" / "2.log"

    if success_log_file.exists():
        success_log = success_log_file.read_text()

        print("Comparing attempt 1 (failed) with attempt 2 (success)...\n")

        comparison = agent.compare_attempts(
            dag_id="etl_sales_daily",
            task_id="extract_data",
            failed_log=log_content,
            success_log=success_log,
            run_id="scheduled__2024-01-15T10:00:00+00:00"
        )

        print(comparison)


def demo_multi_tool_agent(llm, verbose: bool = True) -> None:
    """Demonstrate the Multi-Tool Agent."""
    print_header("MULTI-TOOL INVESTIGATION AGENT DEMO")

    print("The Multi-Tool Agent autonomously investigates issues")
    print("using multiple tools to search logs, query APIs, and analyze errors.\n")

    print("Initializing Multi-Tool Agent...")
    agent = MultiToolAgent(llm=llm, verbose=verbose, max_iterations=10)

    # Show available tools
    print_section("AVAILABLE TOOLS")
    print(agent.get_tools_info())

    # Run investigation
    print_section("STARTING INVESTIGATION")

    query = """The etl_sales_daily DAG had issues this morning.
    Can you investigate what happened with the extract_data task?
    Find the logs, analyze any errors, and tell me what went wrong."""

    print(f"Query: {query}\n")
    print("Agent is thinking and using tools...\n")

    result = agent.investigate(
        query=query,
        dag_id="etl_sales_daily",
        task_id="extract_data"
    )

    print_section("INVESTIGATION COMPLETE")
    print(f"Tools used: {', '.join(result['tools_used'])}\n")
    print(result["output"])


def interactive_mode(llm) -> None:
    """Run in interactive mode."""
    print_header("INTERACTIVE MODE")

    print("Choose an agent to interact with:\n")
    print("1. Diagnostic Agent - Analyze logs you provide")
    print("2. Multi-Tool Agent - Autonomous investigation")
    print("3. Exit\n")

    while True:
        choice = input("\nSelect (1/2/3): ").strip()

        if choice == "1":
            print("\nStarting Diagnostic Agent...")
            agent = DiagnosticAgent(llm=llm, verbose=True)

            while True:
                print("\nOptions:")
                print("  a) Analyze sample failed log")
                print("  b) Enter custom log content")
                print("  c) Back to menu")

                sub_choice = input("\nSelect: ").strip().lower()

                if sub_choice == "a":
                    log_file = MOCK_DATA_DIR / "s3" / "logs" / "etl_sales_daily" / "extract_data" / "2024-01-15T10:00:00+00:00" / "1.log"
                    if log_file.exists():
                        result = agent.diagnose(
                            dag_id="etl_sales_daily",
                            task_id="extract_data",
                            log_content=log_file.read_text(),
                            attempt=1
                        )
                        print("\n" + result.diagnosis)

                elif sub_choice == "b":
                    print("\nPaste log content (end with empty line):")
                    lines = []
                    while True:
                        line = input()
                        if line == "":
                            break
                        lines.append(line)

                    if lines:
                        dag_id = input("DAG ID: ") or "unknown"
                        task_id = input("Task ID: ") or "unknown"

                        result = agent.diagnose(
                            dag_id=dag_id,
                            task_id=task_id,
                            log_content="\n".join(lines)
                        )
                        print("\n" + result.diagnosis)

                elif sub_choice == "c":
                    break

        elif choice == "2":
            print("\nStarting Multi-Tool Agent...")
            agent = MultiToolAgent(llm=llm, verbose=True, max_iterations=10)

            while True:
                query = input("\nEnter your question (or 'back' to return): ").strip()

                if query.lower() == "back":
                    break

                result = agent.investigate(query)
                print("\n" + result["output"])
                print(f"\n[Tools used: {', '.join(result['tools_used'])}]")

        elif choice == "3":
            print("\nGoodbye!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="AI Agents Demo for Airflow Log Investigation"
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "openai", "anthropic"],
        default=os.getenv("LLM_PROVIDER", "ollama"),
        help="LLM provider (default: ollama)"
    )
    parser.add_argument(
        "--model",
        default=os.getenv("LLM_MODEL", "llama3"),
        help="Model name (default: llama3 for Ollama)"
    )
    parser.add_argument(
        "--mode",
        choices=["diagnostic", "multi-tool", "interactive", "all"],
        default="all",
        help="Demo mode (default: all)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce verbose output"
    )

    args = parser.parse_args()

    print_header("AIRFLOW LOG INVESTIGATION AI AGENTS")

    print(f"Provider: {args.provider}")
    print(f"Model: {args.model}")
    print(f"Mode: {args.mode}")

    # Check availability
    if not check_llm_availability(args.provider, args.model):
        sys.exit(1)

    # Initialize LLM
    print("\nInitializing LLM...")
    try:
        llm = get_llm(provider=args.provider, model=args.model)
        print("LLM ready!\n")
    except Exception as e:
        print(f"ERROR initializing LLM: {e}")
        sys.exit(1)

    verbose = not args.quiet

    # Run demos
    if args.mode == "diagnostic":
        demo_diagnostic_agent(llm, verbose)
    elif args.mode == "multi-tool":
        demo_multi_tool_agent(llm, verbose)
    elif args.mode == "interactive":
        interactive_mode(llm)
    else:  # all
        demo_diagnostic_agent(llm, verbose)
        demo_multi_tool_agent(llm, verbose)

    print_header("DEMO COMPLETE")


if __name__ == "__main__":
    main()
