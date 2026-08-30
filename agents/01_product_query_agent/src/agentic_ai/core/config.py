"""
Configuration and Multi-Provider LLM Factory with Ultra-Low Latency & High-TPM Fallbacks.
Primary: Ultra-Fast Groq LPUs (openai/gpt-oss-20b, qwen/qwen3.8-27b, openai/gpt-oss-120b).
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

# Load environment variables
current_file = Path(__file__).resolve()
src_dir = current_file.parent.parent
load_dotenv(current_file.parent / ".env")
load_dotenv(src_dir / ".env")
load_dotenv(src_dir.parent / ".env")
load_dotenv(src_dir.parent.parent / ".env")


def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    api_key: Optional[str] = None,
) -> BaseChatModel:
    """
    Factory function initializing LLMs with ultra-fast sub-second response latency
    and resilient high-TPM fallback chaining.

    Args:
        provider: 'groq', 'primary', or 'google' / 'gemini'.
        model_name: Specific model ID (defaults to 'openai/gpt-oss-20b').
        temperature: Sampling temperature (0.0 for deterministic tool execution).
        api_key: Optional API key override.

    Returns:
        BaseChatModel instance with active fallbacks configured.
    """
    prov = (provider or "groq").lower().strip()
    primary_key = api_key or os.getenv("PRIMARY_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    # High-TPM Fast Groq Models Chain (~400ms - 700ms)
    fallbacks: List[BaseChatModel] = []
    if groq_key:
        try:
            from langchain_groq import ChatGroq

            selected_model = model_name or "openai/gpt-oss-20b"
            groq_primary = ChatGroq(
                model=selected_model,
                temperature=temperature,
                api_key=groq_key,
                max_retries=1,
                request_timeout=8.0,
            )
            # Fallback 1: Qwen 27B
            groq_fallback_1 = ChatGroq(
                model="qwen/qwen3.8-27b",
                temperature=temperature,
                api_key=groq_key,
                max_retries=1,
                request_timeout=8.0,
            )
            # Fallback 2: GPT-OSS 120B
            groq_fallback_2 = ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=temperature,
                api_key=groq_key,
                max_retries=1,
                request_timeout=8.0,
            )
            if selected_model == "openai/gpt-oss-20b":
                fallbacks.extend([groq_fallback_1, groq_fallback_2])
            else:
                fallbacks.extend([groq_primary, groq_fallback_1])
        except Exception:
            groq_primary = None
    else:
        groq_primary = None

    # Google Gemini Direct (if valid non-sk key)
    if prov in ("google", "gemini") and google_key and not google_key.startswith("sk-c0"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        gemini_model = ChatGoogleGenerativeAI(
            model=model_name or "gemini-2.5-flash",
            temperature=temperature,
            google_api_key=google_key,
        )
        if fallbacks:
            return gemini_model.with_fallbacks(fallbacks)
        return gemini_model

    # Direct Groq LPUs (Ultra-fast primary engine)
    if groq_primary:
        if fallbacks:
            return groq_primary.with_fallbacks(fallbacks)
        return groq_primary

    # Ultimate fallback
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=model_name or "openai/gpt-oss-20b",
        temperature=temperature,
        api_key=groq_key or "mock_key",
    )
