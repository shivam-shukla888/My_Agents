"""
Agent 02: Autonomous Web Research Agent Package.
"""

from research_agent.core.agent import WebResearchAgent
from research_agent.plugins.research_plugin import ResearchPlugin
from research_agent.connectors.web_search_connector import WebSearchConnector
from research_agent.connectors.scraper_connector import ScraperConnector

__all__ = [
    "WebResearchAgent",
    "ResearchPlugin",
    "WebSearchConnector",
    "ScraperConnector",
]
