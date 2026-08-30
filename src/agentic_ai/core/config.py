"""
Configuration and Multi-Provider LLM Factory with Ultra-Low Latency & Multi-Model Cascading Fallbacks.
Primary: Ultra-Fast Groq LPUs (qwen/qwen3.6-27b, openai/gpt-oss-120b, openai/gpt-oss-20b).
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
    and resilient multi-model cascading fallback chaining.

    Args:
        provider: 'groq', 'primary', or 'google' / 'gemini'.
        model_name: Specific model ID (defaults to 'qwen/qwen3.6-27b').
        temperature: Sampling temperature (0.0 for deterministic tool execution).
        api_key: Optional API key override.

    Returns:
        BaseChatModel instance with active fallbacks configured.
    """
    prov = (provider or "groq").lower().strip()
    primary_key = api_key or os.getenv("PRIMARY_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    # High-performance Groq model candidate list
    candidate_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b", "openai/gpt-oss-120b"]

    fallbacks: List[BaseChatModel] = []
    if groq_key:
        try:
            from langchain_groq import ChatGroq

            selected_model = model_name or "qwen/qwen3.8-27b"
            groq_primary = ChatGroq(
                model=selected_model,
                temperature=temperature,
                api_key=groq_key,
                max_retries=3,
                request_timeout=20.0,
            )

            # Build resilient fallback chain from alternate models
            for alt in candidate_models:
                if alt != selected_model:
                    fallbacks.append(ChatGroq(
                        model=alt,
                        temperature=temperature,
                        api_key=groq_key,
                        max_retries=3,
                        request_timeout=20.0,
                    ))
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

    # Fallback instantiation
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=model_name or "qwen/qwen3.8-27b",
        temperature=temperature,
        api_key=groq_key or "mock_key",
    )
