"""
Agentic AI Evaluation Framework (Evals Suite).
3 Pillars:
1. Functional Evaluation (Correctness, Faithfulness & Hallucination)
2. Cost & Performance Evaluation (Tokens, Latency, USD Cost)
3. Safety & Robustness Evaluation (Toxicity, PII Leaks, Jailbreak)
"""

from evals.functional_eval import FunctionalEvaluator
from evals.cost_eval import CostEvaluator
from evals.safety_eval import SafetyEvaluator
from evals.benchmark_dataset import BENCHMARK_TEST_SUITE
from evals.runner import EvaluationRunner

__all__ = [
    "FunctionalEvaluator",
    "CostEvaluator",
    "SafetyEvaluator",
    "BENCHMARK_TEST_SUITE",
    "EvaluationRunner",
]
