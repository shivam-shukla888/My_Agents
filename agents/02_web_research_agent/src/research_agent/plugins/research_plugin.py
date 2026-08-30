"""
Research & Market Intelligence Plugin for Agent 02.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from research_agent.connectors.web_search_connector import WebSearchConnector
from research_agent.connectors.scraper_connector import ScraperConnector
from shared.security import SecureWorkspaceVault


class ResearchPlugin:
    """
    Plugin providing tools for web search, competitor pricing, web scraping, and saving research briefs.
    """

    def __init__(
        self,
        search_conn: Optional[WebSearchConnector] = None,
        scraper_conn: Optional[ScraperConnector] = None,
        vault: Optional[SecureWorkspaceVault] = None,
    ):
        self.search = search_conn or WebSearchConnector()
        self.scraper = scraper_conn or ScraperConnector()
        self.vault = vault or SecureWorkspaceVault()

    def get_tools(self) -> List[BaseTool]:
        search_c = self.search
        scraper_c = self.scraper
        vault_c = self.vault

        @tool
        def search_tech_web(query: str, max_results: int = 3) -> str:
            """
            Search web publications, tech review outlets, and lab benchmarks.

            Args:
                query: Keywords or questions to search on the web (e.g. 'MacBook Air M3 review', 'Sony WH-1000XM5 ANC rating').
                max_results: Maximum number of articles to return.

            Returns:
                JSON string with article summaries, URLs, and ratings.
            """
            results = search_c.search_articles(query=query, max_results=max_results)
            return json.dumps({
                "query": query,
                "count": len(results),
                "articles": results,
            }, indent=2)

        @tool
        def compare_competitor_retail_prices(product_name: str) -> str:
            """
            Look up live competitor retail prices (Amazon, Best Buy, B&H, Walmart, Direct) for price matching.

            Args:
                product_name: Name of product (e.g. 'MacBook Air M3', 'Sony WH-1000XM5', 'Dell UltraSharp 27 4K').

            Returns:
                JSON string with competitor listings, lowest market price, and shipping conditions.
            """
            res = search_c.get_competitor_prices(product_name=product_name)
            return json.dumps(res, indent=2)

        @tool
        def scrape_webpage(url: str) -> str:
            """
            Extract structured text and review insights from a specific webpage URL.

            Args:
                url: Web URL to scrape.

            Returns:
                JSON string with extracted text and metrics.
            """
            res = scraper_c.scrape_url(url=url)
            return json.dumps(res, indent=2)

        @tool
        def save_research_brief_to_shared_vault(topic: str, markdown_content: str) -> str:
            """
            Save a completed research brief into the shared workspace so other agents can read it.

            Args:
                topic: Slug/title for the file (e.g. 'macbook_m3_market_analysis.md').
                markdown_content: The comprehensive markdown report content.

            Returns:
                Confirmation string with file path.
            """
            fname = topic.lower().replace(" ", "_").replace(".md", "") + ".md"
            res = vault_c.write_file(
                filename=fname,
                content=markdown_content,
                author_agent="02_web_research_agent",
            )
            return f"Research brief successfully saved: {res['filename']} in shared vault ({res['size_bytes']} bytes)."

        return [
            search_tech_web,
            compare_competitor_retail_prices,
            scrape_webpage,
            save_research_brief_to_shared_vault,
        ]
