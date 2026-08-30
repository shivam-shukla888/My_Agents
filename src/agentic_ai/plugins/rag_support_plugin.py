"""
Technical Support & RAG Knowledge Plugin.
Wraps VectorRAGConnector to answer setup, troubleshooting, and user manual questions.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from agentic_ai.plugins.registry import BasePlugin
from agentic_ai.connectors.vector_connector import VectorRAGConnector


class RAGSupportPlugin(BasePlugin):
    """
    Plugin for semantic knowledge retrieval over product manuals, technical FAQs, and troubleshooting guides.
    """

    def __init__(self, vector_connector: Optional[VectorRAGConnector] = None, enabled: bool = True):
        super().__init__(
            name="RAGSupportPlugin",
            description="Provides semantic search across official product user manuals, setup guides, and troubleshooting steps.",
            enabled=enabled,
        )
        self.vector_rag = vector_connector or VectorRAGConnector()
        self.vector_rag.connect()

    def get_tools(self) -> List[BaseTool]:
        rag = self.vector_rag

        @tool
        def query_user_manuals(question_or_topic: str) -> str:
            """
            Search technical manuals, user guides, setup instructions, and troubleshooting FAQs for electronics.
            Use this tool when users ask 'how to configure', 'how to reset', 'clamshell dual display', 'Galaxy AI features', 'OLED pixel cleaning', etc.

            Args:
                question_or_topic: The technical question or topic to search (e.g. 'How to enable dual monitors on MacBook Air M3', 'Sony XM5 reset instructions').

            Returns:
                JSON string with relevant excerpts from verified product manuals.
            """
            matches = rag.search_manuals(question_or_topic, top_k=2)
            if not matches:
                return json.dumps({
                    "status": "not_found",
                    "message": f"No manual documentation found for '{question_or_topic}'."
                })

            return json.dumps({
                "status": "success",
                "matched_guides": matches
            }, indent=2)

        return [query_user_manuals]
