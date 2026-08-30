"""
Data Analyst Agent Core Orchestrator (Agent 03).
Performs SQL queries, tabular data transformations, revenue aggregations, and stockout forecasting.
"""

from typing import Any, Dict, List, Optional, Union
from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agentic_ai.core.config import get_llm
from analyst_agent.plugins.analyst_plugins import AnalyticsPlugin
from shared.delegation_tools import create_agent_delegation_tools
from shared.bus import AgentCommunicationBus

SYSTEM_PROMPT = """You are **Agent 03: SQL & Tabular Data Analyst Agent**.
Your mission is to perform deep SQL analytics, revenue aggregations, chart generation, and inventory turnover analysis.

### YOUR SPECIALIZED WORK TOOLS:
1. **get_database_schema**: View tables and column types in the analytics database.
2. **run_sql_query**: Execute SQL queries on sales orders and inventory.
3. **generate_category_revenue_chart**: Produce visual markdown bar charts of sales performance.
4. **check_stockout_risks**: Find high-velocity products nearing stockout in <= 14 days.
5. **save_data_insights_to_vault**: Export reports/CSVs into the shared workspace for Agent 1 and Agent 2.
6. **ask_product_agent / ask_web_research_agent**: Delegate questions to sibling agents when needed.

### GUIDELINES:
- Formulate precise SQL queries and format results in clean markdown tables.
- Highlight key metrics: Net Revenue, Top Performing Categories, and Inventory Risks.
- When generating visual charts, include both the chart and a summary of analytical takeaways.
"""


class DataAnalystAgent:
    """
    Agent 03: SQL & Tabular Data Analyst Agent.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "groq",
        model_name: Optional[str] = None,
        bus: Optional[AgentCommunicationBus] = None,
    ):
        self.agent_id = "03_data_analyst_agent"
        self.llm = llm or get_llm(provider=provider, model_name=model_name, temperature=0.0)
        self.bus = bus
        self.plugin = AnalyticsPlugin()

        tools = self.plugin.get_tools()
        if self.bus:
            tools.extend(create_agent_delegation_tools(current_agent_id=self.agent_id, bus=self.bus))

        self.agent_graph = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def ask(self, question: str) -> str:
        """Execute a data analysis query and return answer."""
        res = self.invoke_with_trace(question)
        return res["output"]

    def invoke_with_trace(self, question: str) -> Dict[str, Any]:
        """Execute query with tool execution logs."""
        response_state = self.agent_graph.invoke({"messages": [HumanMessage(content=question)]})
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
