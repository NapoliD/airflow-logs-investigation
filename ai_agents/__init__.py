"""
AI Agents for Airflow Log Investigation

This module provides intelligent agents that use LLMs to:
- Automatically diagnose Airflow task failures
- Perform multi-step investigations using tools
- Generate actionable recommendations

Supports multiple LLM backends:
- Ollama (local models like llama3, mistral, codellama)
- OpenAI (gpt-4, gpt-3.5-turbo)
- Anthropic (claude-3-opus, claude-3-sonnet)
"""

from .config import get_llm, LLMConfig
from .agents.diagnostic_agent import DiagnosticAgent
from .agents.multi_tool_agent import MultiToolAgent

__all__ = [
    "get_llm",
    "LLMConfig",
    "DiagnosticAgent",
    "MultiToolAgent"
]

__version__ = "1.0.0"
