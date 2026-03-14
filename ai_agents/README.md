# 🤖 AI Agents for Airflow Log Investigation

> Intelligent agents that turn "what happened?" into actionable insights.

## Why AI Agents?

Traditional log investigation is tedious:
1. Open CloudWatch, search for the right log group
2. Find the right stream among dozens
3. Scroll through walls of text looking for "ERROR"
4. Copy the stack trace, try to understand it
5. Repeat for S3, API, etc.

These agents automate the entire workflow. You ask a question, they do the investigation.

---

## Quick Start

### Installation

```bash
pip install -r ai_agents/requirements.txt
```

### Using Ollama (Local, Free)

The easiest way to get started — no API keys needed:

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3

# Run the demo
python -m ai_agents.demo
```

### Using Cloud Providers

For better reasoning (especially with complex stack traces):

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
python -m ai_agents.demo --provider openai --model gpt-4

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python -m ai_agents.demo --provider anthropic --model claude-3-sonnet-20240229
```

---

## The Two Agents

### 1. DiagnosticAgent — "Here's the log, what's wrong?"

Best when you already have the log content and just need analysis.

```python
from ai_agents import DiagnosticAgent, get_llm

llm = get_llm("ollama", "llama3")
agent = DiagnosticAgent(llm)

# Analyze a failure
result = agent.diagnose(
    dag_id="etl_sales_daily",
    task_id="extract_data",
    log_content=open("failed_task.log").read(),
    attempt=1
)

print(result.diagnosis)
```

**What you get:**
- Root cause identification
- Evidence from the logs
- Impact assessment
- Actionable recommendations
- Confidence level

### 2. MultiToolAgent — "Something broke, figure it out"

The autonomous investigator. Give it a vague question, it finds the answers.

```python
from ai_agents import MultiToolAgent, get_llm

llm = get_llm("ollama", "llama3")
agent = MultiToolAgent(llm, verbose=True)  # Watch it think

result = agent.investigate(
    "The morning ETL is failing. Can you check what's happening?"
)

print(result["output"])
print(f"Tools used: {result['tools_used']}")
```

**What it does autonomously:**
1. Searches CloudWatch for recent errors
2. Retrieves relevant log streams
3. Queries the Airflow API for task status
4. Extracts and analyzes errors
5. Correlates findings across sources
6. Generates a comprehensive report

---

## Available Tools

The MultiToolAgent has access to 10 specialized tools:

| Category | Tools |
|----------|-------|
| **Discovery** | `list_available_logs` — Find what's out there |
| **CloudWatch** | `search_cloudwatch_logs` — Search by DAG, task, keywords |
| **S3** | `search_s3_logs` — Retrieve full task logs |
| **Content** | `get_log_content` — Read specific log files |
| **API** | `get_dag_runs` — Recent run history |
| **API** | `get_task_instances` — Task states in a run |
| **API** | `get_task_status` — Detailed task info |
| **Analysis** | `extract_errors` — Find all errors in a log |
| **Analysis** | `analyze_stack_trace` — Deep-dive on exceptions |
| **Analysis** | `get_error_summary` — Quick health check |

---

## LLM Configuration

Flexible provider support — use what works for you:

```python
from ai_agents import get_llm

# Local models via Ollama (free, private)
llm = get_llm("ollama", "llama3")
llm = get_llm("ollama", "mistral")
llm = get_llm("ollama", "codellama")  # Good for code-heavy logs

# OpenAI (best reasoning, paid)
llm = get_llm("openai", "gpt-4")
llm = get_llm("openai", "gpt-4-turbo")
llm = get_llm("openai", "gpt-3.5-turbo")  # Cheaper, still good

# Anthropic (great for analysis, paid)
llm = get_llm("anthropic", "claude-3-opus-20240229")
llm = get_llm("anthropic", "claude-3-sonnet-20240229")
```

---

## Demo Modes

```bash
# Full demo — both agents
python -m ai_agents.demo

# Just the diagnostic agent
python -m ai_agents.demo --mode diagnostic

# Just the multi-tool agent
python -m ai_agents.demo --mode multi-tool

# Interactive mode — ask your own questions
python -m ai_agents.demo --mode interactive

# Quieter output
python -m ai_agents.demo --quiet
```

---

## Architecture

```
ai_agents/
├── config.py                  # Provider-agnostic LLM setup
├── agents/
│   ├── diagnostic_agent.py    # Single-shot analysis
│   └── multi_tool_agent.py    # Autonomous investigation
├── tools/
│   ├── log_tools.py           # CloudWatch/S3 retrieval
│   ├── api_tools.py           # Airflow API queries
│   └── analysis_tools.py      # Error extraction & patterns
├── prompts/
│   ├── diagnostic_prompt.py   # Expert diagnostic reasoning
│   └── multi_tool_prompt.py   # Investigation methodology
└── demo.py                    # Interactive demonstration
```

---

## Extending

### Adding Custom Tools

```python
from langchain_core.tools import tool

@tool
def query_slack_alerts(channel: str, hours: int = 24) -> str:
    """Search Slack for related alerts in the specified channel."""
    # Your implementation
    return "Found 3 alerts about database latency..."

# Add to the agent
from ai_agents.agents.multi_tool_agent import MultiToolAgent
MultiToolAgent.TOOLS.append(query_slack_alerts)
```

### Customizing Prompts

The prompts in `prompts/` define how the agent reasons. Modify them to:
- Add company-specific context
- Adjust the output format
- Include domain knowledge
- Change the investigation methodology

---

## Tips for Best Results

1. **Use GPT-4 or Claude for complex traces** — Local models are great for simple errors, but complex multi-file stack traces benefit from stronger reasoning.

2. **Be specific in your questions** — "Why did extract_data fail?" works better than "Something's broken."

3. **Watch verbose mode** — Running with `verbose=True` shows you exactly what the agent is thinking and which tools it's using.

4. **Start with the DiagnosticAgent** — If you already have the log, it's faster than letting the MultiToolAgent search.

---

## Performance Notes

- **Ollama + llama3**: ~5-10 seconds for a diagnosis
- **OpenAI GPT-4**: ~10-15 seconds (includes API latency)
- **MultiToolAgent**: 30-60 seconds for full investigation (multiple tool calls)

The MultiToolAgent makes several LLM calls as it reasons through the investigation, so it's naturally slower but more thorough.

---

## What This Demonstrates

Building these agents required:

- **Understanding LangChain's agent framework** — Tool calling, agent executors, prompt templates
- **Designing effective tools** — Clear descriptions, appropriate granularity, useful outputs
- **Prompt engineering** — Getting consistent, high-quality reasoning from the LLM
- **Production thinking** — Error handling, timeouts, context management

This isn't a tutorial project — it's a working toolkit I'd actually use in production.
