"""
High-Level Modular Agent Orchestrator with Persistent Memory, ChromaDB Grounding,
Real Token-by-Token Streaming, and Stage-Based Telemetry.
"""

import time
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, ToolMessage

from agentic_ai.core.config import get_llm
from agentic_ai.plugins.registry import PluginRegistry
from agentic_ai.plugins.catalog_plugin import CatalogPlugin
from agentic_ai.plugins.rag_support_plugin import RAGSupportPlugin
from agentic_ai.plugins.pricing_plugin import FinancePlugin
from agentic_ai.plugins.invoice_plugin import InvoicePlugin
from agentic_ai.plugins.memory_plugin import MemoryPlugin
from agentic_ai.connectors.chroma_connector import ChromaMemoryConnector

# High-density, single-turn optimized system prompt
SYSTEM_PROMPT = """You are a high-speed E-Commerce AI Assistant.
Tools:
- Catalog: `get_product`, `search_catalog`, `check_warehouse_stock`
- Support/RAG: `query_user_manuals`
- Grounding: `verify_and_ground_fact`
- Finance: `convert_currency_and_tax`, `lookup_promotional_discounts`
- Invoices: `generate_customer_invoice_pdf`
- Memory: `save_user_memory`, `recall_user_memories`

Rules:
1. High Efficiency: Resolve requests in 1 tool call whenever possible. `convert_currency_and_tax`, `search_catalog`, and `generate_customer_invoice_pdf` are multi-purpose tools.
2. Accuracy: Ground technical specifications and prices strictly on tool results.
3. Clarity: Provide concise markdown answers with bold metrics and bullet points.
"""


class HighLevelAgent:
    """
    High-Level Agent orchestrator supporting dynamic plugin management,
    persistent conversation threads (Checkpointer), ChromaDB long-term memory,
    real token-by-token streaming, and stage-based latency telemetry.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "groq",
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

    def get_registered_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins and active state."""
        return self.registry.list_plugins()

    def stream_with_trace(
        self,
        query: str,
        user_id: str = "default_user",
        thread_id: str = "default_thread",
    ) -> Generator[Dict[str, Any], None, None]:
        """
        True token-by-token streaming generator with execution trace events.
        Yields events:
        - {"type": "stage", "stage": "...", "detail": "..."}
        - {"type": "tool_start", "name": "...", "args": {...}}
        - {"type": "tool_end", "name": "...", "duration_ms": 120}
        - {"type": "token", "content": "..."}
        - {"type": "complete", "output": "...", "telemetry": {...}}
        """
        t0 = time.perf_counter()
        ttft_recorded = False
        t_ttft = 0.0
        active_tools_called = []
        full_tokens = []
        active_tool_timers = {}

        # Stage 1: Memory Recall
        yield {"type": "stage", "stage": "MEMORY", "detail": "Recalling user memory from ChromaDB..."}
        t_mem_start = time.perf_counter()
        user_memories = []
        try:
            user_memories = self.chroma_conn.recall_user_memories(user_id=user_id, query="")
        except Exception:
            pass
        t_mem = round((time.perf_counter() - t_mem_start) * 1000, 1)

        # Context Prep
        memory_context = ""
        if user_memories:
            memory_context = f"\n[User Persistent Preferences]:\n" + "\n".join(f"- {m}" for m in user_memories[:3])

        augmented_query = query + memory_context if memory_context else query
        config = {"configurable": {"thread_id": thread_id}}
        messages = [HumanMessage(content=augmented_query)]

        yield {"type": "stage", "stage": "REASONING", "detail": "LangGraph executing agent loop..."}

        # Stream LangGraph events
        for chunk, metadata in self._agent_graph.stream(
            {"messages": messages},
            config=config,
            stream_mode="messages",
        ):
            # Check for tool invocations
            if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                for tc in chunk.tool_calls:
                    t_name = tc.get("name", "tool")
                    active_tool_timers[t_name] = time.perf_counter()
                    yield {
                        "type": "tool_start",
                        "name": t_name,
                        "args": tc.get("args", {}),
                    }

            # Check for tool responses
            elif isinstance(chunk, ToolMessage):
                t_name = chunk.name or "tool"
                t_start = active_tool_timers.pop(t_name, time.perf_counter())
                t_dur = round((time.perf_counter() - t_start) * 1000, 1)
                active_tools_called.append({
                    "name": t_name,
                    "duration_ms": t_dur,
                    "preview": str(chunk.content)[:120],
                })
                yield {
                    "type": "tool_end",
                    "name": t_name,
                    "duration_ms": t_dur,
                }

            # Check for generated content tokens
            elif isinstance(chunk, (AIMessageChunk, AIMessage)) and chunk.content:
                if not ttft_recorded:
                    t_ttft = round(time.perf_counter() - t0, 3)
                    ttft_recorded = True

                if isinstance(chunk.content, str):
                    full_tokens.append(chunk.content)
                    yield {"type": "token", "content": chunk.content}
                elif isinstance(chunk.content, list):
                    for part in chunk.content:
                        if isinstance(part, str):
                            full_tokens.append(part)
                            yield {"type": "token", "content": part}
                        elif isinstance(part, dict) and "text" in part:
                            full_tokens.append(part["text"])
                            yield {"type": "token", "content": part["text"]}

        # Final Telemetry
        t_total = round(time.perf_counter() - t0, 3)
        final_output = "".join(full_tokens).strip()

        telemetry = {
            "total_latency_seconds": t_total,
            "ttft_seconds": t_ttft or t_total,
            "memory_recall_ms": t_mem,
            "tools_count": len(active_tools_called),
            "tool_calls": active_tools_called,
        }

        yield {
            "type": "complete",
            "output": final_output,
            "telemetry": telemetry,
        }

    def ask(
        self,
        query: str,
        user_id: str = "default_user",
        thread_id: str = "default_thread",
    ) -> str:
        """Standard synchronous invocation returning final answer text."""
        res = self.invoke_with_trace(query, user_id=user_id, thread_id=thread_id)
        return res.get("output", "")

    def invoke_with_trace(
        self,
        query: str,
        user_id: str = "default_user",
        thread_id: str = "default_thread",
    ) -> Dict[str, Any]:
        """
        Synchronous invocation returning structured output with latency metrics.
        """
        t0 = time.perf_counter()
        t_mem_start = time.perf_counter()
        user_memories = []
        try:
            user_memories = self.chroma_conn.recall_user_memories(user_id=user_id, query="")
        except Exception:
            pass
        t_mem = round((time.perf_counter() - t_mem_start) * 1000, 1)

        memory_context = ""
        if user_memories:
            memory_context = f"\n[User Persistent Preferences]:\n" + "\n".join(f"- {m}" for m in user_memories[:3])

        augmented_query = query + memory_context if memory_context else query
        config = {"configurable": {"thread_id": thread_id}}
        messages = [HumanMessage(content=augmented_query)]

        response = self._agent_graph.invoke({"messages": messages}, config=config)

        t_total = round(time.perf_counter() - t0, 3)

        # Extract final answer
        all_msgs = response.get("messages", [])
        final_output = ""
        tool_calls = []

        for m in reversed(all_msgs):
            if isinstance(m, AIMessage) and m.content and not final_output:
                if isinstance(m.content, str):
                    final_output = m.content
                elif isinstance(m.content, list):
                    final_output = "\n".join(str(p.get("text", p) if isinstance(p, dict) else p) for p in m.content)
            if hasattr(m, "tool_calls") and m.tool_calls:
                for tc in m.tool_calls:
                    tool_calls.append(tc.get("name"))

        return {
            "output": final_output,
            "tool_calls": tool_calls,
            "telemetry": {
                "total_latency_seconds": t_total,
                "memory_recall_ms": t_mem,
                "tools_count": len(tool_calls),
            }
        }
