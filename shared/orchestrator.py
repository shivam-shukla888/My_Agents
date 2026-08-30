"""
Multi-Agent Network Master Orchestrator.
Connects Agent 01, Agent 02, and Agent 03 into a collaborative ecosystem
backed by the Inter-Agent Communication Bus and Secure Workspace Vault.
"""

from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel

from agentic_ai.core.config import get_llm
from agentic_ai.core.agent import HighLevelAgent
from research_agent.core.agent import WebResearchAgent
from analyst_agent.core.agent import DataAnalystAgent

from shared.bus import AgentCommunicationBus
from shared.security import SecureWorkspaceVault
from shared.delegation_tools import create_agent_delegation_tools


class MultiAgentNetwork:
    """
    Central Network Orchestrator managing all 3 domain agents, inter-agent routing,
    and collaborative multi-step problem solving.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "groq",
        model_name: Optional[str] = None,
        vault_dir: str = "shared/workspace",
    ):
        self.provider = provider
        self.model_name = model_name
        self.llm = llm or get_llm(provider=provider, model_name=model_name, temperature=0.0)

        # Shared Communication Bus & Secure Vault
        self.bus = AgentCommunicationBus()
        self.vault = SecureWorkspaceVault(sandbox_dir=vault_dir)

        # Initialize the 3 Agents
        self.agent_01 = HighLevelAgent(llm=self.llm)
        self.agent_02 = WebResearchAgent(llm=self.llm, bus=self.bus)
        self.agent_03 = DataAnalystAgent(llm=self.llm, bus=self.bus)

        # Register all 3 agents on the bus
        self.bus.register_agent(
            agent_id="01_product_query_agent",
            agent_instance=self.agent_01,
            description="Product specifications, ChromaDB persistent memory, catalog pricing, and PDF invoice generation."
        )
        self.bus.register_agent(
            agent_id="02_web_research_agent",
            agent_instance=self.agent_02,
            description="Web search, competitor retail price comparison, review synthesis, and research reports."
        )
        self.bus.register_agent(
            agent_id="03_data_analyst_agent",
            agent_instance=self.agent_03,
            description="SQL queries on transactional sales, revenue metrics, and inventory stockout forecasting."
        )

        # Inject delegation tools into Agent 01 as well
        delegation_tools_for_01 = create_agent_delegation_tools(
            current_agent_id="01_product_query_agent",
            bus=self.bus,
            vault=self.vault,
        )
        for t in delegation_tools_for_01:
            self.agent_01.registry._plugins["DelegationPlugin"] = type(
                "DelegationPluginWrapper", (), {"enabled": True, "get_tools": lambda s, t=t: [t]}
            )()
        self.agent_01._rebuild_agent()

    def get_agent(self, agent_id: str):
        """Retrieve an individual agent by its ID."""
        if "01" in agent_id or "product" in agent_id:
            return self.agent_01
        elif "02" in agent_id or "research" in agent_id:
            return self.agent_02
        elif "03" in agent_id or "analyst" in agent_id or "data" in agent_id:
            return self.agent_03
        else:
            raise ValueError(f"Unknown agent ID '{agent_id}'. Choose from: 01_product_query_agent, 02_web_research_agent, 03_data_analyst_agent.")

    def run_collaborative_workflow(self, goal: str) -> Dict[str, Any]:
        """
        Execute an end-to-end multi-agent collaboration workflow where agents
        cooperate to solve a complex business objective.
        """
        workflow_trace = []

        # Step 1: Agent 01 analyzes product options
        step1_res = self.agent_01.invoke_with_trace(
            question=f"Analyze available products, specifications, and prices for: {goal}"
        )
        workflow_trace.append({
            "step": 1,
            "agent": "01_product_query_agent",
            "task": "Catalog & Specs Analysis",
            "output": step1_res["output"],
        })

        # Step 2: Agent 02 conducts competitor price research & market validation
        step2_res = self.agent_02.invoke_with_trace(
            question=f"Based on the product options ({goal}), research competitor retail prices (Amazon, Best Buy, B&H) and summarize deals."
        )
        workflow_trace.append({
            "step": 2,
            "agent": "02_web_research_agent",
            "task": "Competitor Price & Market Intelligence",
            "output": step2_res["output"],
        })

        # Step 3: Agent 03 analyzes historical sales velocity & stockout health
        step3_res = self.agent_03.invoke_with_trace(
            question="Analyze sales performance, category revenue, and stockout risks related to this product category."
        )
        workflow_trace.append({
            "step": 3,
            "agent": "03_data_analyst_agent",
            "task": "Sales & Inventory Analytics",
            "output": step3_res["output"],
        })

        # Save collaborative findings to shared workspace
        report_content = f"""# 🌐 Multi-Agent Collaborative Executive Brief

## Goal
{goal}

---

## 🛍️ 1. Product Catalog & Ground-Truth Analysis (Agent 01)
{step1_res['output']}

---

## 🔍 2. Competitor Market Pricing & Reviews (Agent 02)
{step2_res['output']}

---

## 📊 3. Sales Performance & Inventory Velocity (Agent 03)
{step3_res['output']}
"""
        vault_res = self.vault.write_file(
            filename="collaborative_executive_brief.md",
            content=report_content,
            author_agent="MultiAgentNetwork",
        )

        return {
            "status": "success",
            "goal": goal,
            "steps": workflow_trace,
            "shared_vault_report": vault_res["filename"],
            "report_path": vault_res["path"],
            "final_summary": report_content,
        }
