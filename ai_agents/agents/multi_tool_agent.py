"""
Multi-Tool Investigation Agent

An autonomous agent that uses multiple tools to investigate Airflow
task failures. This agent can search logs, query APIs, and analyze
errors without requiring the user to provide log content directly.

This is the "showcase" agent demonstrating agentic capabilities.
"""

from typing import Optional, List, Dict, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..config import get_llm
from ..prompts.multi_tool_prompt import MULTI_TOOL_SYSTEM_PROMPT
from ..tools.log_tools import (
    list_available_logs,
    search_cloudwatch_logs,
    search_s3_logs,
    get_log_content
)
from ..tools.api_tools import (
    get_dag_runs,
    get_task_instances,
    get_task_status
)
from ..tools.analysis_tools import (
    extract_errors,
    analyze_stack_trace,
    get_error_summary
)


class MultiToolAgent:
    """
    Autonomous investigation agent with access to multiple tools.

    This agent can:
    - Discover available logs and their sources
    - Search CloudWatch and S3 for relevant logs
    - Query Airflow API for task metadata
    - Analyze errors and stack traces
    - Generate comprehensive investigation reports

    Example:
        ```python
        from ai_agents import MultiToolAgent, get_llm

        # Using Ollama
        llm = get_llm("ollama", "llama3")
        agent = MultiToolAgent(llm)

        # Investigate a failure
        result = agent.investigate(
            "The etl_sales_daily DAG failed this morning. "
            "Can you find out what went wrong?"
        )

        print(result)
        ```
    """

    # All available tools for the agent
    TOOLS = [
        # Log discovery and retrieval
        list_available_logs,
        search_cloudwatch_logs,
        search_s3_logs,
        get_log_content,
        # API queries
        get_dag_runs,
        get_task_instances,
        get_task_status,
        # Analysis
        extract_errors,
        analyze_stack_trace,
        get_error_summary
    ]

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "ollama",
        model: str = "llama3",
        verbose: bool = True,
        max_iterations: int = 15
    ):
        """
        Initialize the multi-tool agent.

        Args:
            llm: Pre-configured LLM instance. If not provided, creates one.
            provider: LLM provider if llm not provided ("ollama", "openai", "anthropic")
            model: Model name if llm not provided
            verbose: Whether to print agent's reasoning steps
            max_iterations: Maximum tool-calling iterations
        """
        self.llm = llm or get_llm(provider=provider, model=model)
        self.verbose = verbose
        self.max_iterations = max_iterations

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", MULTI_TOOL_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create the agent
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.TOOLS,
            prompt=self.prompt
        )

        # Create the executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.TOOLS,
            verbose=verbose,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        # Conversation history for multi-turn interactions
        self.chat_history: List = []

    def investigate(
        self,
        query: str,
        dag_id: Optional[str] = None,
        task_id: Optional[str] = None,
        run_id: Optional[str] = None,
        clear_history: bool = False
    ) -> Dict[str, Any]:
        """
        Investigate an Airflow issue using available tools.

        The agent will autonomously:
        1. Search for relevant logs
        2. Query the API for context
        3. Analyze errors found
        4. Generate a diagnosis

        Args:
            query: Natural language description of the issue
            dag_id: Optional DAG ID to focus on
            task_id: Optional task ID to focus on
            run_id: Optional run ID to focus on
            clear_history: Whether to clear conversation history

        Returns:
            Dict containing:
            - output: The final investigation report
            - intermediate_steps: List of (action, result) tuples
            - tools_used: List of tools that were called

        Example:
            ```python
            result = agent.investigate(
                "Why did extract_data fail in etl_sales_daily?"
            )
            print(result["output"])
            ```
        """
        if clear_history:
            self.chat_history = []

        # Build the input with any provided context
        input_text = query

        if dag_id or task_id or run_id:
            context_parts = []
            if dag_id:
                context_parts.append(f"DAG ID: {dag_id}")
            if task_id:
                context_parts.append(f"Task ID: {task_id}")
            if run_id:
                context_parts.append(f"Run ID: {run_id}")

            input_text += f"\n\nContext provided:\n" + "\n".join(context_parts)

        # Run the agent
        result = self.executor.invoke({
            "input": input_text,
            "chat_history": self.chat_history
        })

        # Extract tools used
        tools_used = []
        for step in result.get("intermediate_steps", []):
            if hasattr(step[0], 'tool'):
                tools_used.append(step[0].tool)

        # Update history
        self.chat_history.append(HumanMessage(content=query))
        self.chat_history.append(SystemMessage(content=result["output"]))

        return {
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "tools_used": list(set(tools_used))
        }

    def quick_diagnose(self, dag_id: str, task_id: str) -> str:
        """
        Perform a quick diagnosis for a specific task.

        This is a convenience method that constructs an appropriate
        query and returns just the diagnosis text.

        Args:
            dag_id: The DAG ID
            task_id: The task ID

        Returns:
            The diagnosis text

        Example:
            ```python
            diagnosis = agent.quick_diagnose("etl_sales_daily", "extract_data")
            print(diagnosis)
            ```
        """
        query = f"""Investigate the task '{task_id}' in DAG '{dag_id}'.

Please:
1. Check the task status to see if it failed
2. Find and retrieve the relevant logs
3. Analyze any errors found
4. Provide a diagnosis and recommendations"""

        result = self.investigate(query, dag_id=dag_id, task_id=task_id)
        return result["output"]

    def get_tools_info(self) -> str:
        """
        Get information about available tools.

        Returns:
            Formatted string describing all available tools.
        """
        info = "Available Investigation Tools:\n"
        info += "=" * 40 + "\n\n"

        categories = {
            "Log Discovery & Retrieval": [
                list_available_logs,
                search_cloudwatch_logs,
                search_s3_logs,
                get_log_content
            ],
            "API Queries": [
                get_dag_runs,
                get_task_instances,
                get_task_status
            ],
            "Analysis": [
                extract_errors,
                analyze_stack_trace,
                get_error_summary
            ]
        }

        for category, tools in categories.items():
            info += f"## {category}\n\n"
            for tool in tools:
                info += f"**{tool.name}**\n"
                info += f"  {tool.description.split(chr(10))[0]}\n\n"

        return info

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.chat_history = []
