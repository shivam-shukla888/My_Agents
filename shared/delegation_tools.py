"""
Inter-Agent Task Delegation Tools.
Equips agents with tools to consult sibling agents in the network.
"""

from typing import Any, Callable, List, Optional
from langchain_core.tools import BaseTool, tool
from shared.bus import AgentCommunicationBus
from shared.security import SecureWorkspaceVault


def create_agent_delegation_tools(
    current_agent_id: str,
    bus: AgentCommunicationBus,
    vault: Optional[SecureWorkspaceVault] = None,
) -> List[BaseTool]:
    """
    Generate delegation tools tailored for an agent to communicate with peer agents.
    """
    sec_vault = vault or SecureWorkspaceVault()

    @tool
    def ask_product_agent(question: str) -> str:
        """
        Ask Agent 01 (Product & Shopping Assistant) about product specifications, catalog pricing,
        warehouse stock, discount coupons, or to generate a PDF invoice.

        Args:
            question: The inquiry to send to the Product Agent.

        Returns:
            The Product Agent's response.
        """
        res = bus.send_task(
            sender_agent=current_agent_id,
            target_agent="01_product_query_agent",
            task_instruction=question,
        )
        if res["status"] == "success":
            return res["response"]
        return f"Error communicating with Product Agent: {res.get('message')}"

    @tool
    def ask_web_research_agent(research_topic_or_query: str) -> str:
        """
        Ask Agent 02 (Web Research Agent) to perform internet searches, look up external competitor prices,
        scrape reviews, or synthesize market intelligence briefs.

        Args:
            research_topic_or_query: The research instruction or query.

        Returns:
            The Web Research Agent's synthesized report.
        """
        res = bus.send_task(
            sender_agent=current_agent_id,
            target_agent="02_web_research_agent",
            task_instruction=research_topic_or_query,
        )
        if res["status"] == "success":
            return res["response"]
        return f"Error communicating with Web Research Agent: {res.get('message')}"

    @tool
    def ask_data_analyst_agent(data_analysis_task: str) -> str:
        """
        Ask Agent 03 (SQL & Data Analyst Agent) to analyze tabular data, run SQL metrics,
        calculate sales aggregations, generate charts, or forecast demand.

        Args:
            data_analysis_task: The statistical or data analysis question.

        Returns:
            The Data Analyst Agent's insights and chart summaries.
        """
        res = bus.send_task(
            sender_agent=current_agent_id,
            target_agent="03_data_analyst_agent",
            task_instruction=data_analysis_task,
        )
        if res["status"] == "success":
            return res["response"]
        return f"Error communicating with Data Analyst Agent: {res.get('message')}"

    @tool
    def save_shared_workspace_file(filename: str, file_content: str) -> str:
        """
        Save a report, dataset, or notes to the secure shared workspace for other agents to read.

        Args:
            filename: Name of the file (e.g. 'competitor_prices.md', 'sales_summary.csv').
            file_content: Text content to save.

        Returns:
            Confirmation of file save with path.
        """
        res = sec_vault.write_file(
            filename=filename,
            content=file_content,
            author_agent=current_agent_id,
        )
        return f"File successfully saved to shared workspace: {res['filename']} ({res['size_bytes']} bytes)."

    @tool
    def read_shared_workspace_file(filename: str) -> str:
        """
        Read a report or dataset saved by another agent from the secure shared workspace.

        Args:
            filename: Name of the file to read.

        Returns:
            Content of the file.
        """
        res = sec_vault.read_file(
            filename=filename,
            reader_agent=current_agent_id,
        )
        if res["status"] == "success":
            return res["content"]
        return f"Could not read file: {res.get('message')}"

    # Filter out self-delegation
    all_tools = [
        ask_product_agent,
        ask_web_research_agent,
        ask_data_analyst_agent,
        save_shared_workspace_file,
        read_shared_workspace_file,
    ]

    # Don't give an agent a tool to delegate to itself
    filtered = []
    for t in all_tools:
        if current_agent_id == "01_product_query_agent" and t.name == "ask_product_agent":
            continue
        if current_agent_id == "02_web_research_agent" and t.name == "ask_web_research_agent":
            continue
        if current_agent_id == "03_data_analyst_agent" and t.name == "ask_data_analyst_agent":
            continue
        filtered.append(t)

    return filtered
