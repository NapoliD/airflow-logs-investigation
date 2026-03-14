# Airflow Logs Investigation Guide - AWS

A practical guide and toolkit for investigating Apache Airflow task logs in AWS environments, featuring **AI-powered diagnostic agents** built with LangChain.

> **Note:** This project includes mock data for demonstration purposes. All AWS account IDs, bucket names, URLs, and log contents are **completely fictional**. However, the investigation methodology, scripts, and AI agents can be adapted for use with real AWS environments.

## AI Agents for Automated Diagnosis

This project includes **LLM-powered agents** that automatically diagnose Airflow failures:

```python
from ai_agents import MultiToolAgent, get_llm

# Use local models (Ollama) or cloud APIs (OpenAI/Anthropic)
llm = get_llm("ollama", "llama3")
agent = MultiToolAgent(llm)

# Autonomous investigation
result = agent.investigate("Why did etl_sales_daily fail this morning?")
print(result["output"])
```

**Features:**
- **Diagnostic Agent** - Analyzes logs and generates expert diagnoses
- **Multi-Tool Agent** - Autonomously searches, retrieves, and analyzes logs
- **10 Specialized Tools** - CloudWatch, S3, API queries, error analysis
- **Multiple LLM Support** - Ollama (local/free), OpenAI, Anthropic

See [AI Agents Documentation](ai_agents/README.md) for full details.

## Why This Project

When Airflow tasks fail in production, engineers need to quickly locate and analyze logs. In AWS, logs can exist in multiple places:

- **CloudWatch Logs** - Real-time streaming from MWAA
- **S3** - Remote logging configuration
- **REST API** - Task metadata and state
- **Filesystem** - Local logs (non-MWAA deployments)

This project provides:
1. A **step-by-step investigation guide** to identify the best log source
2. **Mock data** simulating a real MWAA environment
3. **Runnable demo scripts** showing how to retrieve and analyze logs
4. A **completed investigation report** as a reference example

## Quick Start

### Basic Demo (No LLM Required)

```bash
python3 scripts/mock_demo.py
```

This simulates investigating a failed `extract_data` task using mock data.

### AI Agents Demo (Requires LLM)

```bash
# Install dependencies
pip install -r ai_agents/requirements.txt

# Option 1: Using Ollama (local, free)
ollama pull llama3
python -m ai_agents.demo

# Option 2: Using OpenAI
export OPENAI_API_KEY="sk-..."
python -m ai_agents.demo --provider openai --model gpt-4

# Option 3: Using Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python -m ai_agents.demo --provider anthropic
```

## Project Structure

```
.
├── README.md                              # This file
├── README_esp.md                          # Spanish version
├── ai_agents/                             # LLM-powered investigation agents
│   ├── agents/
│   │   ├── diagnostic_agent.py            # Log analysis with LLM
│   │   └── multi_tool_agent.py            # Autonomous multi-tool agent
│   ├── tools/
│   │   ├── log_tools.py                   # CloudWatch/S3 retrieval tools
│   │   ├── api_tools.py                   # Airflow API query tools
│   │   └── analysis_tools.py              # Error extraction & analysis
│   ├── prompts/                           # Expert system prompts
│   ├── config.py                          # LLM provider configuration
│   ├── demo.py                            # Interactive AI demo
│   └── requirements.txt                   # AI dependencies (LangChain)
├── docs/
│   └── investigate_airflow_logs.md        # Complete step-by-step guide
├── templates/
│   └── investigation_report.md            # Blank template for your investigations
├── checklists/
│   └── airflow_logs_checklist.md          # Executable checklist
├── examples/
│   └── completed_investigation_report.md  # Example of a completed investigation
├── mock_data/
│   ├── cloudwatch/
│   │   └── sample_logs.json               # Simulated CloudWatch events
│   ├── s3/
│   │   └── logs/...                       # Simulated S3 task logs
│   ├── api_responses/
│   │   └── task_logs.json                 # Simulated API responses
│   └── config/
│       ├── airflow.cfg                    # Example Airflow configuration
│       └── mwaa_environment.json          # Simulated MWAA environment details
└── scripts/
    ├── mock_demo.py                       # Main demo script (uses mock data)
    ├── fetch_cloudwatch_logs.py           # Real CloudWatch retrieval
    ├── fetch_s3_logs.py                   # Real S3 retrieval
    ├── fetch_api_logs.py                  # Real API retrieval
    └── requirements.txt                   # Python dependencies
```

## Mock Data Scenario

The mock data simulates a completed investigation in a fictional Amazon MWAA environment:

| Field | Simulated Value |
|-------|-----------------|
| AWS Account | `123456789012` |
| Region | `us-east-1` |
| MWAA Environment | `prod-data-pipeline` |
| Airflow Version | `2.8.1` |
| S3 Bucket | `acme-corp-airflow-prod` |
| CloudWatch Log Group | `airflow-prod-data-pipeline-Task` |

### Simulated Incident

- **DAG:** `etl_sales_daily`
- **Task:** `extract_data`
- **Issue:** Database connection timeout on first attempt
- **Resolution:** Automatic retry succeeded

## Log Source Priority

When investigating Airflow logs in AWS, use this priority:

| Priority | Source | When to Use |
|----------|--------|-------------|
| 1 | CloudWatch | MWAA or any runtime that publishes logs there |
| 2 | S3 | `remote_logging=True` configured with `s3://...` |
| 3 | REST API | For metadata, states, and orchestration |
| 4 | Filesystem | Direct access to host/container |
| 5 | UI Scraping | Only as a last resort |

## Using with Real AWS Environments

The mock demo uses local JSON files, but the investigation methodology applies to real environments:

1. **Identify your deployment** - MWAA, EKS, ECS, or EC2?
2. **Check logging configuration** - Where does `remote_base_log_folder` point?
3. **Verify IAM permissions** - Can you read CloudWatch/S3?
4. **Test log retrieval** - Use the scripts as templates

### Adapting Scripts for Real Use

Replace the mock data loading with boto3 calls:

```python
# Instead of loading from file:
# data = load_json(MOCK_DATA_DIR / "cloudwatch" / "sample_logs.json")

# Use boto3:
import boto3
client = boto3.client('logs', region_name='us-east-1')
response = client.get_log_events(
    logGroupName='your-log-group',
    logStreamName='your-log-stream'
)
```

## AWS Deployment Types

### Amazon MWAA
- Logs go to CloudWatch automatically
- Check: `AWS Console → MWAA → Environments → Logging configuration`

### EKS (Kubernetes)
- Check pod logs and sidecar configurations
- May ship to CloudWatch via Fluent Bit

### ECS (Containers)
- Check task definitions for `awslogs` driver
- Logs typically go to CloudWatch

### EC2 (Direct)
- Check filesystem at `$AIRFLOW_HOME/logs/`
- May use CloudWatch Agent for shipping

## Skills Demonstrated

### AI Engineering
- **LLM Integration** - Multi-provider support (Ollama, OpenAI, Anthropic)
- **LangChain Agents** - Tool-calling agents with autonomous reasoning
- **Prompt Engineering** - Expert system prompts for diagnostic tasks
- **Agentic Architecture** - Multi-step investigation workflows

### Data & Cloud Engineering
- **Airflow Operations** - Understanding task execution and logging
- **AWS Architecture** - CloudWatch, S3, MWAA, IAM permissions
- **Production Debugging** - Systematic investigation workflows
- **Python Automation** - Scripts for operational support

### Software Engineering
- **Clean Architecture** - Modular, extensible design
- **Technical Documentation** - Structured guides and templates
- **Developer Experience** - Interactive demos, clear APIs

## Documentation

### AI Agents
- [AI Agents Overview](ai_agents/README.md) - Setup, usage, and architecture

### Investigation Guides
- [Complete Investigation Guide](docs/investigate_airflow_logs.md) - Full step-by-step instructions
- [Investigation Checklist](checklists/airflow_logs_checklist.md) - Quick reference during investigations
- [Report Template](templates/investigation_report.md) - Document your findings
- [Example Report](examples/completed_investigation_report.md) - See a completed investigation

## Official References

- [AWS MWAA - Accessing Airflow logs](https://docs.aws.amazon.com/mwaa/latest/userguide/monitoring-airflow.html)
- [Airflow - Writing logs to S3](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/logging/s3-task-handler.html)
- [Airflow - Configuration Reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html)
- [AWS MWAA - REST API](https://docs.aws.amazon.com/mwaa/latest/userguide/access-mwaa-apache-airflow-rest-api.html)

## License

MIT
