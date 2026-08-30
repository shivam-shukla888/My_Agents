"""
Configuration and Multi-Provider LLM Factory with Ultra-Low Latency Fallbacks.
Primary: Configured Primary LLM (OpenAI / Custom Endpoint)
Fallback: Blazing-fast Groq LPU models (qwen/qwen3.8-27b, openai/gpt-oss-20b)
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


def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    api_key: Optional[str] = None,
) -> BaseChatModel:
    """
    Factory function initializing LLMs with primary key priority and ultra-fast Groq fallbacks.

    Args:
        provider: 'primary', 'groq', or 'google' / 'gemini'.
        model_name: Specific model ID.
        temperature: Sampling temperature (0.0 for deterministic tool execution).
        api_key: Optional API key override.

    Returns:
        BaseChatModel instance with active fallbacks configured.
    """
    prov = (provider or "primary").lower().strip()
    primary_key = api_key or os.getenv("PRIMARY_API_KEY") or os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    # Build Fallback Chain of Fast Groq Models
    fallbacks: List[BaseChatModel] = []

    if groq_key:
        try:
            from langchain_groq import ChatGroq

            # Fast Fallback 1: Qwen 27B on Groq LPUs (~300-600ms latency)
            groq_fast_1 = ChatGroq(
                model="qwen/qwen3.8-27b",
                temperature=temperature,
                api_key=groq_key,
                max_retries=1,
                request_timeout=8.0,
            )
            # Fast Fallback 2: GPT-OSS 20B on Groq
            groq_fast_2 = ChatGroq(
                model="openai/gpt-oss-20b",
                temperature=temperature,
                api_key=groq_key,
                max_retries=1,
                request_timeout=8.0,
            )
            fallbacks.extend([groq_fast_1, groq_fast_2])
        except Exception:
            pass

    # Google Provider Explicit Request
    if prov in ("google", "gemini") and google_key and not google_key.startswith("sk-"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        primary = ChatGoogleGenerativeAI(
            model=model_name or "gemini-2.5-flash",
            temperature=temperature,
            google_api_key=google_key,
        )
        if fallbacks:
            return primary.with_fallbacks(fallbacks)
        return primary

    # Primary Key Strategy (ChatOpenAI / Custom Base URL)
    if primary_key and prov != "groq":
        try:
            from langchain_openai import ChatOpenAI

            base_url = os.getenv("PRIMARY_BASE_URL", "https://api.openai.com/v1")
            primary_model = model_name or os.getenv("PRIMARY_MODEL", "gpt-4o-mini")

            primary_llm = ChatOpenAI(
                model=primary_model,
                temperature=temperature,
                api_key=primary_key,
                base_url=base_url,
                max_retries=1,
                request_timeout=5.0,  # Fast 5s timeout to prevent hanging
            )

            if fallbacks:
                return primary_llm.with_fallbacks(fallbacks)
            return primary_llm
        except Exception:
            pass

    # Direct Groq Provider
    if fallbacks:
        primary_groq = fallbacks[0]
        remaining = fallbacks[1:]
        if remaining:
            return primary_groq.with_fallbacks(remaining)
        return primary_groq

    # Ultimate default fallback
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=model_name or "qwen/qwen3.8-27b",
        temperature=temperature,
        api_key=groq_key,
    )
