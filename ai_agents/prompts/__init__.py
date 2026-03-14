"""
Agent Prompts

System prompts and templates for the diagnostic and multi-tool agents.
"""

from .diagnostic_prompt import DIAGNOSTIC_SYSTEM_PROMPT, DIAGNOSTIC_HUMAN_TEMPLATE
from .multi_tool_prompt import MULTI_TOOL_SYSTEM_PROMPT, MULTI_TOOL_HUMAN_TEMPLATE

__all__ = [
    "DIAGNOSTIC_SYSTEM_PROMPT",
    "DIAGNOSTIC_HUMAN_TEMPLATE",
    "MULTI_TOOL_SYSTEM_PROMPT",
    "MULTI_TOOL_HUMAN_TEMPLATE"
]
