"""
LLM Configuration Module

Provides flexible configuration for multiple LLM backends:
- Ollama: Local models (llama3, mistral, codellama, etc.)
- OpenAI: Cloud API (gpt-4, gpt-3.5-turbo)
- Anthropic: Cloud API (claude-3-opus, claude-3-sonnet)

Usage:
    # Using Ollama (local)
    llm = get_llm(provider="ollama", model="llama3")

    # Using OpenAI
    llm = get_llm(provider="openai", model="gpt-4")

    # Using Anthropic
    llm = get_llm(provider="anthropic", model="claude-3-sonnet-20240229")
"""

import os
from dataclasses import dataclass
from typing import Optional, Literal

from langchain_core.language_models import BaseChatModel


LLMProvider = Literal["ollama", "openai", "anthropic"]


@dataclass
class LLMConfig:
    """Configuration for LLM initialization."""
    provider: LLMProvider = "ollama"
    model: str = "llama3"
    temperature: float = 0.1
    base_url: Optional[str] = None  # For Ollama custom URL
    api_key: Optional[str] = None   # For cloud providers

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create config from environment variables."""
        return cls(
            provider=os.getenv("LLM_PROVIDER", "ollama"),
            model=os.getenv("LLM_MODEL", "llama3"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        )


def get_llm(
    provider: LLMProvider = "ollama",
    model: Optional[str] = None,
    temperature: float = 0.1,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """
    Get an LLM instance based on provider.

    Args:
        provider: LLM provider ("ollama", "openai", "anthropic")
        model: Model name (defaults vary by provider)
        temperature: Sampling temperature (0.0 = deterministic)
        base_url: Base URL for Ollama (default: http://localhost:11434)
        api_key: API key for cloud providers
        **kwargs: Additional provider-specific arguments

    Returns:
        LangChain chat model instance

    Examples:
        # Local Ollama
        llm = get_llm("ollama", "llama3")

        # OpenAI
        llm = get_llm("openai", "gpt-4", api_key="sk-...")

        # Anthropic
        llm = get_llm("anthropic", "claude-3-sonnet-20240229")
    """

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model or "llama3",
            temperature=temperature,
            base_url=base_url or "http://localhost:11434",
            **kwargs
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model or "gpt-4",
            temperature=temperature,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            **kwargs
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=model or "claude-3-sonnet-20240229",
            temperature=temperature,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            **kwargs
        )

    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'ollama', 'openai', or 'anthropic'")


def check_ollama_available(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible."""
    import requests
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def list_ollama_models(base_url: str = "http://localhost:11434") -> list:
    """List available Ollama models."""
    import requests
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
    except requests.RequestException:
        pass
    return []
