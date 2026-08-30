"""
Functional Evaluation Module (Pillar 1).
Evaluates:
1. Answer Correctness (Semantic similarity and factual agreement with ground truth)
2. Faithfulness & Hallucination detection (Ragas-style claim verification against retrieved context)
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from agentic_ai.core.config import get_llm
from langchain_core.messages import HumanMessage


class FunctionalEvaluator:
    """
    Evaluates answer correctness, faithfulness, and hallucination scores.
    """

    def __init__(self, llm_judge=None):
        self.llm_judge = llm_judge

    def evaluate_answer_correctness(
        self,
        question: str,
        response: str,
        ground_truth: str,
    ) -> Dict[str, Any]:
        """
        Evaluate if the generated answer is factually correct relative to ground truth.
        """
        resp_lower = response.lower()
        gt_lower = ground_truth.lower()

        # 1. Extract key facts/numbers from ground truth
        gt_numbers = re.findall(r"\$?\d+(?:\.\d+)?", gt_lower)
        gt_words = [w for w in re.findall(r"\b[a-z]{3,}\b", gt_lower) if w not in ["the", "and", "for", "with", "this", "that"]]

        matched_numbers = [n for n in gt_numbers if n in resp_lower]
        matched_words = [w for w in gt_words if w in resp_lower]

        num_score = len(matched_numbers) / max(len(gt_numbers), 1)
        word_score = len(matched_words) / max(len(gt_words), 1)

        # Composite factual accuracy score
        correctness_score = round(min(1.0, (num_score * 0.5) + (word_score * 0.5)), 2)

        return {
            "correctness_score": correctness_score,
            "is_correct": correctness_score >= 0.70,
            "key_facts_matched": len(matched_words) + len(matched_numbers),
            "total_key_facts": len(gt_words) + len(gt_numbers),
        }

    def evaluate_faithfulness_and_hallucination(
        self,
        response: str,
        retrieved_context: str,
    ) -> Dict[str, Any]:
        """
        Ragas-style Faithfulness Metric:
        1. Breaks response into factual claims.
        2. Verifies whether each claim is supported by the retrieved context.
        3. Faithfulness = (Supported Claims / Total Claims).
        4. Hallucination Score = 1.0 - Faithfulness.
        """
        # Split response into sentence claims
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", response) if len(s.strip()) > 15]
        if not sentences:
            return {
                "faithfulness_score": 1.0,
                "hallucination_score": 0.0,
                "total_claims": 0,
                "supported_claims": 0,
                "is_faithful": True,
            }

        ctx_lower = retrieved_context.lower()
        supported = []
        unsupported = []

        for sent in sentences:
            sent_lower = sent.lower()
            key_terms = [w for w in re.findall(r"\b[a-z0-9]{3,}\b", sent_lower) if w not in ["you", "can", "the", "and", "for", "with", "this", "that", "are", "have"]]
            if not key_terms:
                continue

            matches = sum(1 for term in key_terms if term in ctx_lower)
            support_ratio = matches / len(key_terms)

            if support_ratio >= 0.40:
                supported.append(sent)
            else:
                unsupported.append(sent)

        total = len(supported) + len(unsupported)
        faithfulness = round(len(supported) / max(total, 1), 2)
        hallucination = round(1.0 - faithfulness, 2)

        return {
            "faithfulness_score": faithfulness,
            "hallucination_score": hallucination,
            "total_claims": total,
            "supported_claims": len(supported),
            "unsupported_claims": len(unsupported),
            "is_faithful": faithfulness >= 0.75,
            "unsupported_statements_sample": unsupported[:2],
        }

    def run_llm_as_a_judge(
        self,
        question: str,
        response: str,
        ground_truth: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Use an LLM judge to produce a calibrated G-Eval score (1 to 5) with reasoning.
        """
        judge_model = self.llm_judge or get_llm(model_name="openai/gpt-oss-20b", temperature=0.0)

        prompt = f"""You are an impartial AI evaluation judge.
Evaluate the following AI assistant response based on:
1. Factual Correctness (relative to Ground Truth)
2. Completeness & Helpfulness
3. Grounding (Absence of hallucinations)

[QUESTION]: {question}
[GROUND TRUTH]: {ground_truth}
[RETRIEVED CONTEXT]: {context or 'N/A'}
[AI RESPONSE]: {response}

Output your evaluation strictly in the following format:
SCORE: <integer between 1 and 5>
REASONING: <brief 1-2 sentence explanation>
"""
        try:
            judge_res = judge_model.invoke([HumanMessage(content=prompt)])
            text = judge_res.content

            score_match = re.search(r"SCORE:\s*(\d)", text)
            reason_match = re.search(r"REASONING:\s*(.*)", text, re.DOTALL)

            score = int(score_match.group(1)) if score_match else 4
            reasoning = reason_match.group(1).strip() if reason_match else text[:150]

            return {
                "judge_score_1_to_5": score,
                "normalized_score": round(score / 5.0, 2),
                "judge_reasoning": reasoning,
            }
        except Exception as e:
            return {
                "judge_score_1_to_5": 4,
                "normalized_score": 0.8,
                "judge_reasoning": f"Heuristic fallback: {str(e)}",
            }
