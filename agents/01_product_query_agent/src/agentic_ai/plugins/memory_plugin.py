"""
Long-Term Memory & Anti-Hallucination Grounding Plugin.
Uses ChromaMemoryConnector to store/recall customer facts and verify technical claims against ground-truth docs.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from agentic_ai.plugins.registry import BasePlugin
from agentic_ai.connectors.chroma_connector import ChromaMemoryConnector


class MemoryPlugin(BasePlugin):
    """
    Plugin providing persistent cross-session memory and strict anti-hallucination fact verification.
    """

    def __init__(
        self,
        chroma_connector: Optional[ChromaMemoryConnector] = None,
        enabled: bool = True
    ):
        super().__init__(
            name="MemoryPlugin",
            description="Provides long-term persistent memory for user preferences and ChromaDB anti-hallucination ground-truth verification.",
            enabled=enabled,
        )
        self.chroma = chroma_connector or ChromaMemoryConnector()
        self.chroma.connect()

    def get_tools(self) -> List[BaseTool]:
        chroma_conn = self.chroma

        @tool
        def save_user_memory(user_id: str, memory_fact: str) -> str:
            """
            Save a persistent long-term fact, preference, or owned device for a customer to ChromaDB.
            (e.g., 'User owns MacBook Air M3 and needs a high-contrast monitor', 'User budget is strictly under $500').

            Args:
                user_id: Unique customer ID or username (e.g. 'john_doe', 'user_123').
                memory_fact: The fact, preference, or detail to store permanently.

            Returns:
                JSON confirmation of the saved memory.
            """
            res = chroma_conn.save_user_memory(user_id=user_id, memory_fact=memory_fact)
            return json.dumps(res, indent=2)

        @tool
        def recall_user_memories(user_id: str, query: str = "") -> str:
            """
            Recall persistent long-term preferences, owned devices, and past requirements for a specific customer from ChromaDB.

            Args:
                user_id: Customer ID or username to look up memories for.
                query: Optional search topic (e.g. 'budget', 'monitor preference', 'owned laptop').

            Returns:
                JSON list of stored long-term memories.
            """
            memories = chroma_conn.recall_user_memories(user_id=user_id, query=query)
            return json.dumps({
                "user_id": user_id,
                "memory_count": len(memories),
                "memories": memories,
            }, indent=2)

        @tool
        def verify_and_ground_fact(claim_or_question: str) -> str:
            """
            Retrieve verified ground-truth documentation from ChromaDB to prevent hallucinations.
            Use this tool whenever you need to verify exact technical parameters, battery hours, display modes, or compatibility rules.

            Args:
                claim_or_question: The specific technical claim or question to check against verified documents.

            Returns:
                JSON string with exact verified documentation excerpts.
            """
            ground_truth = chroma_conn.verify_ground_truth(claim_or_question, n_results=2)
            return json.dumps({
                "query": claim_or_question,
                "verified_sources_count": len(ground_truth),
                "verified_documents": ground_truth,
            }, indent=2)

        return [save_user_memory, recall_user_memories, verify_and_ground_fact]
