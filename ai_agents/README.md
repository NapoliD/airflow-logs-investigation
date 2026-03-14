# AI Agents for Airflow Log Investigation

LLM-powered agents that automatically diagnose Airflow task failures using natural language understanding.

## Features

- **Diagnostic Agent**: Analyzes provided logs and generates detailed diagnoses
- **Multi-Tool Agent**: Autonomously investigates using search, API queries, and analysis tools
- **Multiple LLM Support**: Ollama (local), OpenAI, Anthropic
- **Production-Ready Tools**: 10 specialized tools for log investigation

## Quick Start

### Installation

```bash
pip install -r ai_agents/requirements.txt
```

### Using Ollama (Local - Free)

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3

# Run demo
python -m ai_agents.demo
```

### Using Cloud Providers

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
python -m ai_agents.demo --provider openai --model gpt-4

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python -m ai_agents.demo --provider anthropic --model claude-3-sonnet-20240229
```

## Agents

### 1. Diagnostic Agent

Analyzes log content you provide and generates expert diagnoses.

```python
from ai_agents import DiagnosticAgent, get_llm

# Initialize
llm = get_llm("ollama", "llama3")
agent = DiagnosticAgent(llm)

# Analyze a failure
result = agent.diagnose(
    dag_id="etl_sales_daily",
    task_id="extract_data",
    log_content=open("task.log").read(),
    attempt=1
)

print(result.diagnosis)
```

**Output includes:**
- Summary of the issue
- Root cause identification
- Evidence from logs
- Impact assessment
- Actionable recommendations

### 2. Multi-Tool Agent

Autonomously investigates issues using multiple tools.

```python
from ai_agents import MultiToolAgent, get_llm

# Initialize
llm = get_llm("ollama", "llama3")
agent = MultiToolAgent(llm, verbose=True)

# Investigate
result = agent.investigate(
    "The etl_sales_daily DAG failed this morning. What happened?"
)

print(result["output"])
print(f"Tools used: {result['tools_used']}")
```

**Available Tools:**

| Category | Tools |
|----------|-------|
| Log Discovery | `list_available_logs`, `search_cloudwatch_logs`, `search_s3_logs`, `get_log_content` |
| API Queries | `get_dag_runs`, `get_task_instances`, `get_task_status` |
| Analysis | `extract_errors`, `analyze_stack_trace`, `get_error_summary` |

## LLM Configuration

```python
from ai_agents import get_llm

# Ollama (local)
llm = get_llm("ollama", "llama3")
llm = get_llm("ollama", "mistral")
llm = get_llm("ollama", "codellama")

# OpenAI
llm = get_llm("openai", "gpt-4")
llm = get_llm("openai", "gpt-3.5-turbo")

# Anthropic
llm = get_llm("anthropic", "claude-3-opus-20240229")
llm = get_llm("anthropic", "claude-3-sonnet-20240229")
```

## Demo Modes

```bash
# Run all demos
python -m ai_agents.demo

# Specific modes
python -m ai_agents.demo --mode diagnostic
python -m ai_agents.demo --mode multi-tool
python -m ai_agents.demo --mode interactive
```

## Architecture

```
ai_agents/
├── config.py           # LLM provider configuration
├── agents/
│   ├── diagnostic_agent.py   # Log analysis agent
│   └── multi_tool_agent.py   # Autonomous investigation agent
├── tools/
│   ├── log_tools.py          # CloudWatch/S3 log retrieval
│   ├── api_tools.py          # Airflow API queries
│   └── analysis_tools.py     # Error extraction & analysis
├── prompts/
│   ├── diagnostic_prompt.py  # Expert system prompts
│   └── multi_tool_prompt.py  # Investigation prompts
└── demo.py             # Interactive demonstration
```

## Extending

### Adding New Tools

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Tool description for the LLM."""
    return f"Result for {param}"

# Add to MultiToolAgent.TOOLS list
```

### Custom Prompts

Modify prompts in `prompts/` to customize agent behavior for your use case.

## Why This Matters

This module demonstrates:

- **LLM Integration**: Connecting LangChain with multiple providers
- **Tool Calling**: Building agents that use tools autonomously
- **Prompt Engineering**: Expert-level prompts for diagnostic reasoning
- **Agentic Architecture**: Multi-step autonomous investigation
- **Production Patterns**: Configuration, error handling, extensibility
