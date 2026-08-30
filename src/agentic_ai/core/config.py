"""
Configuration and Multi-Provider LLM Factory with Automatic Rate-Limit Fallbacks.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

# Load environment variables
current_file = Path(__file__).resolve()
src_dir = current_file.parent.parent
load_dotenv(current_file.parent / ".env")
load_dotenv(src_dir / ".env")
load_dotenv(src_dir.parent / ".env")


def get_llm(
    provider: str = "groq",
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    api_key: Optional[str] = None,
) -> BaseChatModel:
    """
    Factory function to initialize Chat models with automatic fallback for high reliability.

    Args:
        provider: 'groq' or 'google' / 'gemini'.
        model_name: Specific model ID (e.g. 'qwen/qwen3.8-27b', 'openai/gpt-oss-120b', 'gemini-2.5-flash').
        temperature: Sampling temperature (default 0.0 for deterministic tool calling).
        api_key: Optional API key override.

    Returns:
        BaseChatModel instance with fallbacks configured.
    """
    prov = provider.lower().strip()

    if prov in ("google", "gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI

        key = api_key or os.getenv("GOOGLE_API_KEY")
        model = model_name or "gemini-2.5-flash"
        primary = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=key,
        )
        return primary
    else:
        # Default to Groq with automatic fallback to prevent 429 TPM exhaustion
        from langchain_groq import ChatGroq

        key = api_key or os.getenv("GROQ_API_KEY")
        primary_model = model_name or "qwen/qwen3.8-27b"
        fallback_model = "openai/gpt-oss-20b" if primary_model != "openai/gpt-oss-20b" else "qwen/qwen3.8-27b"

        primary_llm = ChatGroq(
            model=primary_model,
            temperature=temperature,
            api_key=key,
            max_retries=3,
        )

        fallback_llm = ChatGroq(
            model=fallback_model,
            temperature=temperature,
            api_key=key,
            max_retries=3,
        )

        # Attach fallback LLM
        return primary_llm.with_fallbacks([fallback_llm])
