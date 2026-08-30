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

# High-density compact system prompt (avoids TPM token exhaustion)
SYSTEM_PROMPT = """You are an expert E-Commerce AI Assistant with tools:
- Catalog: `get_product`, `search_catalog`, `get_stock`
- Knowledge: `query_user_manuals`, `verify_and_ground_fact`
- Finance: `convert_currency`, `calculate_total_with_tax`, `lookup_discount`
- Invoices: `generate_order_invoice`
- Memory: `save_user_memory`, `recall_user_memories`

Rules:
1. Always verify technical specifications, stock, and prices using tools before answering.
2. Recall and respect user preferences and budget.
3. Present answers clearly with markdown bullet points and bold key values.
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

    def stream_with_trace(
        self,
        question: str,
        user_id: str = "default_user",
        thread_id: str = "main_session",
        chat_history: Optional[List[BaseMessage]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Real Token-by-Token Streaming with stage execution events and live TTFT telemetry.
        """
        t0 = time.perf_counter()
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        # Stage 1: Memory Recall
        yield {"type": "stage", "stage": "MEMORY", "detail": "Recalling user memory from ChromaDB..."}
        t_mem_start = time.perf_counter()
        memories = self.chroma_conn.recall_user_memories(user_id=user_id, n_results=3)
        t_mem_elapsed = round((time.perf_counter() - t_mem_start) * 1000, 1)

        context_prefix = ""
        if memories:
            mem_bullets = "\n".join(f"- {m['memory']}" for m in memories)
            context_prefix = f"[User '{user_id}' Preferences:\n{mem_bullets}]\n\n"

        prompt_input = f"{context_prefix}{question}"

        messages = []
        if chat_history:
            messages.extend(chat_history)
        messages.append(HumanMessage(content=prompt_input))

        # Stage 2: Graph Execution & Streaming
        yield {"type": "stage", "stage": "ANALYZING", "detail": "Reasoning & planning tool execution..."}

        accumulated_text = ""
        tool_calls: List[Dict[str, Any]] = []
        first_token_time: Optional[float] = None
        tool_start_times: Dict[str, float] = {}

        try:
            for chunk, metadata in self._agent_graph.stream(
                {"messages": messages},
                config=config,
                stream_mode="messages",
            ):
                # Detect Tool Invocations
                if getattr(chunk, "tool_calls", None):
                    for tc in chunk.tool_calls:
                        t_name = tc.get("name", "tool")
                        tool_start_times[t_name] = time.perf_counter()
                        yield {
                            "type": "tool_start",
                            "name": t_name,
                            "args": tc.get("args", {}),
                            "id": tc.get("id"),
                        }

                # Detect Tool Message Responses
                if isinstance(chunk, ToolMessage):
                    t_name = getattr(chunk, "name", "tool")
                    t_dur = round((time.perf_counter() - tool_start_times.get(t_name, time.perf_counter())) * 1000, 1)
                    tc_record = {
                        "name": t_name,
                        "duration_ms": t_dur,
                        "preview": str(chunk.content)[:120],
                    }
                    tool_calls.append(tc_record)
                    yield {
                        "type": "tool_end",
                        "name": t_name,
                        "duration_ms": t_dur,
                    }

                # Detect Content Streaming Tokens (AIMessageChunk)
                if isinstance(chunk, AIMessageChunk) and chunk.content and not getattr(chunk, "tool_call_chunks", None):
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                        yield {"type": "stage", "stage": "GENERATING", "detail": "Streaming response tokens..."}

                    content_str = str(chunk.content)
                    accumulated_text += content_str
                    yield {"type": "token", "content": content_str}

        except Exception as e:
            res = self.invoke_with_trace(question=question, user_id=user_id, thread_id=thread_id, chat_history=chat_history)
            accumulated_text = res["output"]
            tool_calls = res["tool_calls"]

        total_latency = round(time.perf_counter() - t0, 3)
        ttft_val = round(first_token_time - t0, 3) if first_token_time else total_latency

        telemetry = {
            "total_seconds": total_latency,
            "ttft_seconds": ttft_val,
            "memory_retrieval_ms": t_mem_elapsed,
            "tool_count": len(tool_calls),
            "tool_calls": tool_calls,
        }

        yield {
            "type": "complete",
            "output": accumulated_text,
            "tool_calls": tool_calls,
            "telemetry": telemetry,
            "user_id": user_id,
            "thread_id": thread_id,
        }

    def invoke_with_trace(
        self,
        question: str,
        user_id: str = "default_user",
        thread_id: str = "main_session",
        chat_history: Optional[List[BaseMessage]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous execution with telemetry timing.
        """
        t0 = time.perf_counter()
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        t_mem_start = time.perf_counter()
        memories = self.chroma_conn.recall_user_memories(user_id=user_id, n_results=3)
        t_mem_elapsed = round((time.perf_counter() - t_mem_start) * 1000, 1)

        context_prefix = ""
        if memories:
            mem_bullets = "\n".join(f"- {m['memory']}" for m in memories)
            context_prefix = f"[User '{user_id}' Preferences:\n{mem_bullets}]\n\n"

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

        final_answer = ""
        for m in reversed(all_msgs):
            if isinstance(m, AIMessage) and m.content:
                final_answer = m.content
                break
            elif getattr(m, "role", None) == "assistant" and getattr(m, "content", None):
                final_answer = m.content
                break

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
