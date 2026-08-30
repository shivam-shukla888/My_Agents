"""
High-Level Modular Agent Orchestrator with Persistent Memory & ChromaDB Grounding.
Integrates Connectors, Plugin Registry, Checkpointing, and Anti-Hallucination Tools.
"""

import time
from typing import Any, Dict, List, Optional, Union
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agentic_ai.core.config import get_llm
from agentic_ai.plugins.registry import PluginRegistry
from agentic_ai.plugins.catalog_plugin import CatalogPlugin
from agentic_ai.plugins.rag_support_plugin import RAGSupportPlugin
from agentic_ai.plugins.pricing_plugin import FinancePlugin
from agentic_ai.plugins.invoice_plugin import InvoicePlugin
from agentic_ai.plugins.memory_plugin import MemoryPlugin
from agentic_ai.connectors.chroma_connector import ChromaMemoryConnector

SYSTEM_PROMPT = """You are an intelligent, high-level E-Commerce & Product AI Assistant equipped with persistent long-term memory and ground-truth data connectors:
1. **Catalog & Inventory Plugin**: Look up product details, hardware specs, stock availability, and prices.
2. **RAG Knowledge & Support Plugin**: Query official user manuals, setup guides, and troubleshooting steps.
3. **Finance & Currency Plugin**: Perform multi-currency conversions (EUR, GBP, INR, JPY), sales tax, and discount lookups.
4. **Invoice & PDF Plugin**: Generate official downloadable order invoice PDFs for purchases.
5. **Memory & Grounding Plugin**: Save and recall persistent long-term user preferences and verify facts with ChromaDB.

### STRICT ANTI-HALLUCINATION & FACTUAL GROUNDING RULES:
- **Never Guess Technical Specs or Prices**: Always verify through `get_product`, `verify_and_ground_fact`, or `query_user_manuals`.
- **Long-Term Memory Utilization**: When talking with a user, recall and respect their previously saved preferences, owned gear, and budget limits.
- **Proactive Savings**: Check for active discount coupons when discussing prices.
- **Structured Presentation**: Use markdown comparison tables, bullet points, and bold values for readability.
"""


class HighLevelAgent:
    """
    High-Level Agent orchestrator supporting dynamic plugin management,
    persistent conversation threads (Checkpointer), ChromaDB long-term memory,
    and simple `ask(question, user_id, thread_id)` execution.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "primary",
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        registry: Optional[PluginRegistry] = None,
        system_prompt: str = SYSTEM_PROMPT,
        checkpointer: Optional[Any] = None,
        chroma_conn: Optional[ChromaMemoryConnector] = None,
        debug: bool = False,
    ):
        self.llm = llm or get_llm(provider=provider, model_name=model_name, temperature=temperature)
        self.system_prompt = system_prompt
        self.debug = debug
        self.checkpointer = checkpointer or MemorySaver()

        # Shared ChromaDB connector (reused from cache if provided)
        if chroma_conn:
            self.chroma_conn = chroma_conn
        else:
            self.chroma_conn = ChromaMemoryConnector()
            self.chroma_conn.connect()

        # Initialize Plugin Registry
        if registry:
            self.registry = registry
        else:
            self.registry = PluginRegistry()
            self._register_default_plugins()

        self._agent_graph = None
        self._rebuild_agent()

    def _register_default_plugins(self) -> None:
        """Register the default suite of work plugins."""
        self.registry.register(CatalogPlugin(enabled=True))
        self.registry.register(RAGSupportPlugin(enabled=True))
        self.registry.register(FinancePlugin(enabled=True))
        self.registry.register(InvoicePlugin(enabled=True))
        self.registry.register(MemoryPlugin(chroma_connector=self.chroma_conn, enabled=True))

    def _rebuild_agent(self) -> None:
        """Recompile the LangChain StateGraph with currently active plugin tools and checkpointer."""
        active_tools = self.registry.get_active_tools()
        self._agent_graph = create_agent(
            model=self.llm,
            tools=active_tools,
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer,
            debug=self.debug,
        )

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin and rebuild the agent graph."""
        res = self.registry.enable_plugin(plugin_name)
        if res:
            self._rebuild_agent()
        return res

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin and rebuild the agent graph."""
        res = self.registry.disable_plugin(plugin_name)
        if res:
            self._rebuild_agent()
        return res

    def ask(
        self,
        question: str,
        user_id: str = "default_user",
        thread_id: str = "main_session",
    ) -> str:
        """
        Execute a question with thread persistence and long-term user memory.
        """
        result = self.invoke_with_trace(
            question=question,
            user_id=user_id,
            thread_id=thread_id,
        )
        return result["output"]

    def invoke_with_trace(
        self,
        question: str,
        user_id: str = "default_user",
        thread_id: str = "main_session",
        chat_history: Optional[List[BaseMessage]] = None,
    ) -> Dict[str, Any]:
        """
        Execute query with thread persistence, message trace, tool call logging, and latency telemetry.
        """
        t0 = time.perf_counter()
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        # Check for long-term memories for this user to inject as background context
        t_mem_start = time.perf_counter()
        memories = self.chroma_conn.recall_user_memories(user_id=user_id, n_results=3)
        t_mem_elapsed = round((time.perf_counter() - t_mem_start) * 1000, 1)

        context_prefix = ""
        if memories:
            mem_bullets = "\n".join(f"- {m['memory']}" for m in memories)
            context_prefix = f"[System Context: User ID is '{user_id}'. Known Long-Term Preferences:\n{mem_bullets}]\n\n"

        prompt_input = f"{context_prefix}{question}"

        messages = []
        if chat_history:
            messages.extend(chat_history)
        messages.append(HumanMessage(content=prompt_input))

        t_graph_start = time.perf_counter()
        response_state = self._agent_graph.invoke(
            {"messages": messages},
            config=config,
        )
        t_graph_elapsed = round((time.perf_counter() - t_graph_start) * 1000, 1)
        all_msgs = response_state.get("messages", [])

        # Extract final answer
        final_answer = ""
        for m in reversed(all_msgs):
            if isinstance(m, AIMessage) and m.content:
                final_answer = m.content
                break
            elif getattr(m, "role", None) == "assistant" and getattr(m, "content", None):
                final_answer = m.content
                break

        # Extract tool calls
        tool_calls = []
        for m in all_msgs:
            if getattr(m, "tool_calls", None):
                for tc in m.tool_calls:
                    tool_calls.append({
                        "name": tc.get("name"),
                        "args": tc.get("args"),
                        "id": tc.get("id"),
                    })

        total_latency_seconds = round(time.perf_counter() - t0, 3)

        return {
            "output": final_answer,
            "messages": all_msgs,
            "tool_calls": tool_calls,
            "user_id": user_id,
            "thread_id": thread_id,
            "memories_recalled": len(memories),
            "telemetry": {
                "total_seconds": total_latency_seconds,
                "memory_retrieval_ms": t_mem_elapsed,
                "graph_execution_ms": t_graph_elapsed,
                "tool_count": len(tool_calls),
            }
        }
