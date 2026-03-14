"""
Diagnostic Agent

An LLM-powered agent that analyzes Airflow task logs and provides
detailed diagnoses with actionable recommendations.

This agent receives log content directly and focuses on analysis,
making it efficient for cases where logs are already available.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel

from ..config import get_llm
from ..prompts.diagnostic_prompt import DIAGNOSTIC_SYSTEM_PROMPT, DIAGNOSTIC_HUMAN_TEMPLATE


@dataclass
class DiagnosisResult:
    """Structured result from the diagnostic agent."""
    dag_id: str
    task_id: str
    run_id: str
    attempt: int
    diagnosis: str
    raw_response: str

    def __str__(self) -> str:
        return self.diagnosis


class DiagnosticAgent:
    """
    Agent for diagnosing Airflow task failures.

    This agent analyzes provided log content using an LLM to:
    - Identify the root cause of failures
    - Extract relevant error information
    - Provide actionable recommendations

    Example:
        ```python
        from ai_agents import DiagnosticAgent, get_llm

        # Using Ollama (local)
        llm = get_llm("ollama", "llama3")
        agent = DiagnosticAgent(llm)

        # Analyze a failure
        result = agent.diagnose(
            dag_id="etl_sales_daily",
            task_id="extract_data",
            run_id="scheduled__2024-01-15T10:00:00+00:00",
            attempt=1,
            log_content="[ERROR] Connection timeout..."
        )

        print(result.diagnosis)
        ```
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "ollama",
        model: str = "llama3",
        verbose: bool = False
    ):
        """
        Initialize the diagnostic agent.

        Args:
            llm: Pre-configured LLM instance. If not provided, creates one.
            provider: LLM provider if llm not provided ("ollama", "openai", "anthropic")
            model: Model name if llm not provided
            verbose: Whether to print debug information
        """
        self.llm = llm or get_llm(provider=provider, model=model)
        self.verbose = verbose

        # Build the chain
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", DIAGNOSTIC_SYSTEM_PROMPT),
            ("human", DIAGNOSTIC_HUMAN_TEMPLATE)
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def diagnose(
        self,
        dag_id: str,
        task_id: str,
        log_content: str,
        run_id: str = "unknown",
        attempt: int = 1,
        additional_context: str = ""
    ) -> DiagnosisResult:
        """
        Analyze log content and generate a diagnosis.

        Args:
            dag_id: The DAG identifier
            task_id: The task identifier
            log_content: The raw log text to analyze
            run_id: The run identifier (optional)
            attempt: The attempt number (1, 2, etc.)
            additional_context: Any additional context to provide

        Returns:
            DiagnosisResult with the full diagnosis

        Example:
            ```python
            result = agent.diagnose(
                dag_id="my_dag",
                task_id="failing_task",
                log_content=open("task.log").read(),
                attempt=1
            )
            print(result)
            ```
        """
        if self.verbose:
            print(f"Diagnosing: {dag_id}/{task_id} (attempt {attempt})")
            print(f"Log content length: {len(log_content)} chars")

        # Truncate very long logs to avoid context limits
        max_log_length = 15000
        if len(log_content) > max_log_length:
            # Keep beginning and end
            half = max_log_length // 2
            log_content = (
                log_content[:half] +
                f"\n\n... [{len(log_content) - max_log_length} characters truncated] ...\n\n" +
                log_content[-half:]
            )

        # Run the chain
        response = self.chain.invoke({
            "dag_id": dag_id,
            "task_id": task_id,
            "run_id": run_id,
            "attempt": attempt,
            "log_content": log_content,
            "additional_context": additional_context or "None provided"
        })

        return DiagnosisResult(
            dag_id=dag_id,
            task_id=task_id,
            run_id=run_id,
            attempt=attempt,
            diagnosis=response,
            raw_response=response
        )

    def diagnose_from_file(
        self,
        log_file_path: str,
        dag_id: str,
        task_id: str,
        **kwargs
    ) -> DiagnosisResult:
        """
        Convenience method to diagnose from a log file.

        Args:
            log_file_path: Path to the log file
            dag_id: The DAG identifier
            task_id: The task identifier
            **kwargs: Additional arguments passed to diagnose()

        Returns:
            DiagnosisResult with the full diagnosis
        """
        with open(log_file_path, 'r') as f:
            log_content = f.read()

        return self.diagnose(
            dag_id=dag_id,
            task_id=task_id,
            log_content=log_content,
            **kwargs
        )

    def compare_attempts(
        self,
        dag_id: str,
        task_id: str,
        failed_log: str,
        success_log: str,
        run_id: str = "unknown"
    ) -> str:
        """
        Compare a failed attempt with a successful retry.

        Args:
            dag_id: The DAG identifier
            task_id: The task identifier
            failed_log: Log content from the failed attempt
            success_log: Log content from the successful attempt
            run_id: The run identifier

        Returns:
            Analysis comparing the two attempts
        """
        comparison_prompt = ChatPromptTemplate.from_messages([
            ("system", DIAGNOSTIC_SYSTEM_PROMPT),
            ("human", """Compare these two execution attempts of the same task:

## Context
- DAG ID: {dag_id}
- Task ID: {task_id}
- Run ID: {run_id}

## Failed Attempt (Attempt 1)
```
{failed_log}
```

## Successful Attempt (Attempt 2)
```
{success_log}
```

Please analyze:
1. What was different between the two attempts?
2. Why did the first attempt fail?
3. Why did the second attempt succeed?
4. Is this a transient or persistent issue?
5. What can be done to prevent the initial failure?""")
        ])

        chain = comparison_prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "dag_id": dag_id,
            "task_id": task_id,
            "run_id": run_id,
            "failed_log": failed_log[:8000],  # Truncate for context
            "success_log": success_log[:8000]
        })
