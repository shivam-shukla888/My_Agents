"""
Web Research Agent Core Orchestrator (Agent 02).
Performs autonomous internet search, tech reviews, competitor price intelligence, and report synthesis.
"""

from typing import Any, Dict, List, Optional, Union
from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agentic_ai.core.config import get_llm
from research_agent.plugins.research_plugin import ResearchPlugin
from shared.delegation_tools import create_agent_delegation_tools
from shared.bus import AgentCommunicationBus

SYSTEM_PROMPT = """You are **Agent 02: Autonomous Web Research Agent**.
Your mission is to perform deep web intelligence, competitor price-matching analysis, review synthesis, and structured reporting.

### YOUR SPECIALIZED WORK TOOLS:
1. **search_tech_web**: Search web articles, tech reviews, lab benchmarks, and hardware ratings.
2. **compare_competitor_retail_prices**: Query live competitor prices from Amazon, Best Buy, B&H, Walmart.
3. **scrape_webpage**: Extract deep content from URLs.
4. **save_research_brief_to_shared_vault**: Save reports to the shared vault for your peer agents (Agent 1 & Agent 3).
5. **ask_product_agent / ask_data_analyst_agent**: Delegate questions to sibling agents when needed.

### GUIDELINES:
- Synthesize multiple sources into cohesive, executive-ready markdown briefs with clear comparison tables.
- Highlight lowest market prices and actionable shopping recommendations.
- When generating reports, save them to the shared workspace vault.
"""


class WebResearchAgent:
    """
    Agent 02: Autonomous Web Research Agent.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "groq",
        model_name: Optional[str] = None,
        bus: Optional[AgentCommunicationBus] = None,
    ):
        self.agent_id = "02_web_research_agent"
        self.llm = llm or get_llm(provider=provider, model_name=model_name, temperature=0.0)
        self.bus = bus
        self.plugin = ResearchPlugin()

        # Gather tools
        tools = self.plugin.get_tools()
        if self.bus:
            tools.extend(create_agent_delegation_tools(current_agent_id=self.agent_id, bus=self.bus))

        self.agent_graph = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def ask(self, question: Optional[str] = None, *, query: Optional[str] = None) -> str:
        """Execute a research query and return answer."""
        prompt = question if question is not None else (query or "")
        res = self.invoke_with_trace(prompt)
        return res["output"]

    def invoke_with_trace(self, question: Optional[str] = None, *, query: Optional[str] = None) -> Dict[str, Any]:
        """Execute query with tool execution logs. Accepts `question` or `query`."""
        prompt = question if question is not None else (query or "")
        response_state = self.agent_graph.invoke({"messages": [HumanMessage(content=prompt)]})
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
                    })

        return {
            "output": final_answer,
            "messages": all_msgs,
            "tool_calls": tool_calls,
            "agent_id": self.agent_id,
        }
