# 🔍 Airflow Logs Investigation Toolkit

> **From "where are my logs?" to "here's what went wrong" — in seconds, not hours.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A practical toolkit for investigating Apache Airflow task logs in AWS environments, featuring **AI-powered diagnostic agents** that can autonomously find, analyze, and explain failures.

---

## 💡 The Problem I Solved

Every data engineer knows this pain: a DAG fails at 3 AM, and you spend the next hour jumping between CloudWatch, S3, and the Airflow UI trying to piece together what happened.

I built this toolkit after one too many late-night debugging sessions. Instead of manually hunting through log sources, I wanted an AI agent that could:

1. **Find the relevant logs** across CloudWatch, S3, and the API
2. **Extract the actual error** from walls of text
3. **Explain what went wrong** in plain English
4. **Suggest what to do next**

The result? An investigation that used to take 30+ minutes now takes 30 seconds.

---

## 🤖 AI Agents in Action

```python
from ai_agents import MultiToolAgent, get_llm

# Works with local models (free!) or cloud APIs
llm = get_llm("ollama", "llama3")
agent = MultiToolAgent(llm)

# Just ask what happened
result = agent.investigate(
    "The sales ETL failed this morning. What went wrong?"
)

print(result["output"])
```

**Output:**
```
Investigation Complete
======================

Root Cause: Database connection timeout (transient)

The extract_data task failed on attempt 1 due to a connection timeout
to salesdb.acme-corp.internal:5432 after 30 seconds. The retry succeeded,
indicating a transient network issue.

Evidence:
- CloudWatch shows psycopg2.OperationalError at 10:00:32
- S3 logs confirm retry at 10:05:00 completed successfully
- Task duration: 355s total (including retry wait)

Recommendation:
1. Monitor database connection pool health
2. Consider increasing timeout for large queries
3. Current retry config (2 attempts) handled this well

Confidence: High
```

---

## ⚡ Quick Start

### Option 1: Basic Demo (No AI)

```bash
git clone https://github.com/NapoliD/airflow-logs-investigation.git
cd airflow-logs-investigation
python3 scripts/mock_demo.py
```

### Option 2: AI Agents with Ollama (Free, Local)

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3

pip install -r ai_agents/requirements.txt
python -m ai_agents.demo
```

### Option 3: AI Agents with OpenAI/Anthropic

```bash
export OPENAI_API_KEY="sk-..."  # or ANTHROPIC_API_KEY
pip install -r ai_agents/requirements.txt
python -m ai_agents.demo --provider openai --model gpt-4
```

---

## 🛠️ What's Inside

### AI Agents (`ai_agents/`)

| Component | What It Does |
|-----------|--------------|
| **DiagnosticAgent** | Analyzes logs you provide, generates expert diagnosis |
| **MultiToolAgent** | Autonomously searches, retrieves, and analyzes logs |
| **10 Custom Tools** | CloudWatch search, S3 retrieval, API queries, error analysis |

### Investigation Resources

| Resource | Purpose |
|----------|---------|
| [Investigation Guide](docs/investigate_airflow_logs.md) | Step-by-step methodology |
| [Checklist](checklists/airflow_logs_checklist.md) | Quick reference while investigating |
| [Report Template](templates/investigation_report.md) | Document your findings |
| [Example Report](examples/completed_investigation_report.md) | See a completed investigation |

### Mock Data

Realistic simulation of an Amazon MWAA environment with:
- CloudWatch log events with actual error patterns
- S3 task logs showing failure → retry → success
- API responses matching Airflow's REST API format
- MWAA configuration examples

---

## 🏗️ Architecture

```
ai_agents/
├── agents/
│   ├── diagnostic_agent.py    # Direct log analysis
│   └── multi_tool_agent.py    # Autonomous investigation
├── tools/
│   ├── log_tools.py           # CloudWatch & S3 retrieval
│   ├── api_tools.py           # Airflow API queries
│   └── analysis_tools.py      # Error extraction & patterns
├── prompts/
│   ├── diagnostic_prompt.py   # Expert diagnostic reasoning
│   └── multi_tool_prompt.py   # Investigation workflow
└── config.py                  # Multi-provider LLM config
```

---

## 🎯 Skills Demonstrated

This project showcases production-ready implementations of:

**AI Engineering**
- LLM integration with multiple providers (Ollama, OpenAI, Anthropic)
- LangChain agents with custom tool calling
- Prompt engineering for domain-specific reasoning
- Agentic workflows with autonomous decision-making

**Data & Cloud Engineering**
- AWS services: CloudWatch Logs, S3, MWAA
- Airflow internals: task lifecycle, logging, retries
- Production debugging methodologies

**Software Engineering**
- Clean, modular architecture
- Comprehensive documentation
- Interactive demonstrations

---

## 📊 Mock Scenario Details

The mock data simulates a real incident I've seen many times:

| Component | Value |
|-----------|-------|
| Environment | Amazon MWAA `prod-data-pipeline` |
| DAG | `etl_sales_daily` |
| Failed Task | `extract_data` |
| Error | `psycopg2.OperationalError: connection timed out` |
| Resolution | Automatic retry succeeded |

This pattern — transient failures that resolve on retry — is extremely common in production data pipelines.

---

## 🔗 Log Source Priority

Based on my experience, here's the order I recommend:

| Priority | Source | Why |
|----------|--------|-----|
| 1️⃣ | CloudWatch | Native MWAA integration, real-time, queryable |
| 2️⃣ | S3 | Persistent, cheap, good for historical analysis |
| 3️⃣ | REST API | Best for metadata and orchestration |
| 4️⃣ | Filesystem | Only if you have direct access |
| 5️⃣ | UI Scraping | Avoid if possible — fragile and slow |

---

## 🚀 Extending This Project

### Add a New Tool

```python
from langchain_core.tools import tool

@tool
def check_database_status(connection_string: str) -> str:
    """Check if a database is reachable and responding."""
    # Your implementation here
    return "Database is healthy"

# Add to MultiToolAgent.TOOLS
```

### Custom Prompts

Edit `ai_agents/prompts/` to customize the agent's reasoning for your specific use case (different error patterns, company-specific context, etc.).

---

## 📚 References

- [AWS MWAA - Accessing Airflow logs](https://docs.aws.amazon.com/mwaa/latest/userguide/monitoring-airflow.html)
- [Airflow - Logging for Tasks](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/logging-tasks.html)
- [LangChain - Tool Calling](https://python.langchain.com/docs/modules/agents/tools/)

---

## 📝 Note on Mock Data

All AWS account IDs, bucket names, URLs, and log contents in this project are **completely fictional**. The data is designed to be realistic enough for demonstrations and testing, but contains no real infrastructure references.

The methodology and code, however, are production-ready and can be adapted for real AWS environments.

---

## 👤 About

Built by someone who got tired of debugging Airflow at 3 AM.

If you're dealing with similar challenges in your data pipelines, feel free to reach out — I'm always happy to discuss Airflow, AWS, and AI-powered operations.

---

## 📄 License

MIT — use it, modify it, make it yours.
