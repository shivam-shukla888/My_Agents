"""
Cost & Performance Evaluation Module (Pillar 2).
Measures:
1. Tokens (Prompt tokens, Completion tokens, Total tokens)
2. Execution Latency (seconds & milliseconds)
3. Model Cost Estimation (USD)
"""

import time
from typing import Any, Dict, Optional
from contextlib import contextmanager

# Cost per 1 Million Tokens (USD)
MODEL_PRICING = {
    # Groq Models
    "qwen/qwen3.8-27b": {"input_per_m": 0.20, "output_per_m": 0.40},
    "openai/gpt-oss-120b": {"input_per_m": 0.59, "output_per_m": 0.79},
    "openai/gpt-oss-20b": {"input_per_m": 0.075, "output_per_m": 0.30},
    # Google Gemini Models
    "gemini-2.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
    "gemini-1.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
    "gemini-1.5-pro": {"input_per_m": 1.25, "output_per_m": 5.00},
    # Default fallback
    "default": {"input_per_m": 0.15, "output_per_m": 0.40},
}


class CostEvaluator:
    """
    Evaluates token usage throughput, execution latency, and financial cost.
    """

    def __init__(self, default_model: str = "qwen/qwen3.8-27b"):
        self.default_model = default_model

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (approx 1 token ~= 4 characters or 0.75 words)."""
        if not text:
            return 0
        words = len(text.split())
        chars = len(text)
        return max(1, int((words * 1.3 + chars / 4.0) / 2.0))

    @contextmanager
    def measure_latency(self):
        """Context manager to measure execution latency with high precision."""
        start_time = time.perf_counter()
        metrics = {"start_time": start_time, "latency_seconds": 0.0, "latency_ms": 0.0}
        try:
            yield metrics
        finally:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            metrics["latency_seconds"] = round(elapsed, 4)
            metrics["latency_ms"] = round(elapsed * 1000, 2)

    def evaluate_cost(
        self,
        prompt_text: str,
        completion_text: str,
        latency_seconds: float = 0.0,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compute full token usage, latency metrics, and estimated USD cost.
        """
        model = model_name or self.default_model
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])

        prompt_tokens = self.estimate_tokens(prompt_text)
        completion_tokens = self.estimate_tokens(completion_text)
        total_tokens = prompt_tokens + completion_tokens

        cost_input = (prompt_tokens / 1_000_000.0) * pricing["input_per_m"]
        cost_output = (completion_tokens / 1_000_000.0) * pricing["output_per_m"]
        total_cost_usd = round(cost_input + cost_output, 6)

        return {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency_seconds": round(latency_seconds, 3),
            "latency_ms": round(latency_seconds * 1000, 2),
            "tokens_per_second": round(total_tokens / max(latency_seconds, 0.001), 2),
            "estimated_cost_usd": total_cost_usd,
            "cost_formatted": f"${total_cost_usd:.6f}",
        }
